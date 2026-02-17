# Copyright (c) 2026, Strategitech and contributors
# For license information, please see license.txt

import csv
import io
import os

import frappe
from frappe.model.document import Document


class ImportacaoProdutos(Document):
	def on_submit(self):
		frappe.enqueue(
			"calculadora_orcamento.calculadora_orcamento.doctype.importacao_produtos.importacao_produtos.process_import",
			doc_name=self.name,
			queue="long",
			timeout=600,
		)
		self.db_set("status", "Processando")


def process_import(doc_name):
	"""Background job to process the CSV/XLSX import."""
	doc = frappe.get_doc("Importacao Produtos", doc_name)

	file_url = doc.arquivo
	if not file_url:
		doc.db_set("status", "Erro")
		doc.db_set("log", "Nenhum arquivo anexado")
		return

	# Get file path from Frappe file manager
	file_doc = frappe.get_doc("File", {"file_url": file_url})
	file_path = file_doc.get_full_path()

	ext = os.path.splitext(file_path)[1].lower()

	rows = []
	try:
		if ext == ".csv":
			rows = _parse_csv(file_path)
		elif ext in (".xlsx", ".xls"):
			rows = _parse_xlsx(file_path)
		else:
			doc.db_set("status", "Erro")
			doc.db_set("log", f"Formato nao suportado: {ext}. Use CSV ou XLSX.")
			return
	except Exception as e:
		doc.db_set("status", "Erro")
		doc.db_set("log", f"Erro ao ler arquivo: {str(e)}")
		return

	if not rows:
		doc.db_set("status", "Erro")
		doc.db_set("log", "Arquivo vazio ou sem dados validos")
		return

	supplier = doc.supplier
	total_imported = 0
	total_errors = 0
	log_lines = []

	for i, row in enumerate(rows, start=2):  # start=2 because row 1 is header
		ref = row.get("ref_produto_interno", "").strip()
		nome = row.get("nome", "").strip()
		preco_str = row.get("preco", "0").strip()

		if not ref or not nome:
			total_errors += 1
			log_lines.append(f"Linha {i}: ref_produto_interno ou nome vazio — pulando")
			continue

		try:
			preco = float(preco_str.replace(",", ".")) if preco_str else 0.0
		except ValueError:
			total_errors += 1
			log_lines.append(f"Linha {i}: preco invalido '{preco_str}'")
			continue

		item_code = f"{supplier}-{ref}"

		try:
			# Create or update Item in ERPNext
			if not frappe.db.exists("Item", item_code):
				item = frappe.new_doc("Item")
				item.item_code = item_code
				item.item_name = nome
				item.item_group = supplier.replace("_", " ").title() if supplier else "Products"
				item.stock_uom = "Nos"
				item.is_stock_item = 0
				item.description = row.get("descricao", nome)
				item.supplier_origin = supplier

				if row.get("marca"):
					item.brand = row["marca"]
				if row.get("url_imagem"):
					item.image = row["url_imagem"]

				item.insert(ignore_permissions=True)
			else:
				item = frappe.get_doc("Item", item_code)
				item.item_name = nome
				item.description = row.get("descricao", nome)
				item.save(ignore_permissions=True)

			# Create or update Item Price
			existing_price = frappe.db.get_value(
				"Item Price",
				{"item_code": item_code, "selling": 1},
				"name"
			)
			if existing_price:
				frappe.db.set_value("Item Price", existing_price, "price_list_rate", preco)
			elif preco > 0:
				price_list = frappe.db.get_single_value("Selling Settings", "selling_price_list") or "Standard Selling"
				ip = frappe.new_doc("Item Price")
				ip.item_code = item_code
				ip.price_list = price_list
				ip.price_list_rate = preco
				ip.currency = "BRL"
				ip.insert(ignore_permissions=True)

			total_imported += 1
		except Exception as e:
			total_errors += 1
			log_lines.append(f"Linha {i} ({item_code}): {str(e)}")

	frappe.db.commit()

	doc.db_set("total_importados", total_imported)
	doc.db_set("total_erros", total_errors)
	doc.db_set("log", "\n".join(log_lines) if log_lines else "Importacao concluida sem erros")
	doc.db_set("status", "Concluido" if total_errors == 0 else "Concluido")


def _parse_csv(file_path):
	"""Parse CSV file and return list of dicts."""
	rows = []
	with open(file_path, "r", encoding="utf-8-sig") as f:
		# Try to detect delimiter
		sample = f.read(2048)
		f.seek(0)
		dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
		reader = csv.DictReader(f, dialect=dialect)
		for row in reader:
			# Normalize keys: strip whitespace and lowercase
			normalized = {k.strip().lower().replace(" ", "_"): v for k, v in row.items()}
			rows.append(normalized)
	return rows


def _parse_xlsx(file_path):
	"""Parse XLSX file and return list of dicts."""
	try:
		import openpyxl
	except ImportError:
		frappe.throw("openpyxl nao instalado. Instale com: pip install openpyxl")

	wb = openpyxl.load_workbook(file_path, read_only=True)
	ws = wb.active

	rows = []
	headers = None
	for i, row in enumerate(ws.iter_rows(values_only=True)):
		if i == 0:
			headers = [str(h).strip().lower().replace(" ", "_") if h else f"col_{j}" for j, h in enumerate(row)]
			continue
		row_dict = {}
		for j, val in enumerate(row):
			if j < len(headers):
				row_dict[headers[j]] = str(val) if val is not None else ""
		rows.append(row_dict)

	wb.close()
	return rows
