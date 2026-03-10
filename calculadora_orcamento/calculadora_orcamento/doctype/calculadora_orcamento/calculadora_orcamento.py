# Copyright (c) 2025, Strategitech and contributors
# For license information, please see license.txt

import json
import math

import frappe
from frappe.model.document import Document


def get_scale_price(item_code, qty):
	"""Get price from scale_prices JSON if available, else fall back to Item Price."""
	scale_json = frappe.db.get_value("Item", item_code, "scale_prices")
	if scale_json:
		try:
			tiers = json.loads(scale_json)
			if isinstance(tiers, list) and tiers:
				# Sort by MinQt descending, pick first where qty >= MinQt
				tiers_sorted = sorted(tiers, key=lambda t: t.get("MinQt", 0), reverse=True)
				for tier in tiers_sorted:
					if qty >= tier.get("MinQt", 0):
						return tier.get("Price", 0.0)
		except (json.JSONDecodeError, TypeError, KeyError):
			pass

	# Fallback to flat Item Price
	filters = {"item_code": item_code, "selling": 1}
	rate = frappe.db.get_value("Item Price", filters, "price_list_rate")
	return rate if rate else 0.0


def _to_float(value):
	try:
		return float(value or 0)
	except (TypeError, ValueError):
		return 0.0


def _to_int(value):
	try:
		return int(value or 0)
	except (TypeError, ValueError):
		return 0


def _is_empty_line(line):
	return (
		not line.get("item")
		and not line.get("descricao")
		and _to_int(line.get("quantidade")) <= 0
		and _to_float(line.get("valor_unitario")) <= 0
		and _to_float(line.get("valor_total")) <= 0
	)


def _get_gravacao_metodos(doc):
	metodos = []
	for row in doc.get("gravacoes") or []:
		catalogo_gravacao = row.get("catalogo_gravacao")
		if not catalogo_gravacao:
			continue

		metodo = frappe.db.get_value("Catalogo Gravacao", catalogo_gravacao, "metodo_gravacao")
		if metodo and metodo not in metodos:
			metodos.append(metodo)

	return metodos


def _append_gravacao_metodos(descricao, gravacao_metodos):
	base = str(descricao or "").strip()
	if not gravacao_metodos:
		return base

	suffix = f"personalizada a {', '.join(gravacao_metodos).lower()}"
	if suffix in base.lower():
		return base
	if base:
		return f"{base}, {suffix}"
	return suffix.capitalize()


def _collect_product_line_models(doc):
	models = []
	for row in doc.get("produtos") or []:
		model = {
			"item": row.get("item"),
			"descricao": row.get("descricao"),
			"quantidade": _to_int(row.get("quantidade")),
			"valor_unitario": _to_float(row.get("valor_unitario")),
			"valor_total": _to_float(row.get("valor_total")),
			"imagem_produto": row.get("imagem_produto"),
			"_row": row,
			"_legacy": 0,
		}
		if not _is_empty_line(model):
			models.append(model)

	if models:
		return models

	legacy = {
		"item": doc.get("item"),
		"descricao": doc.get("descrição") or doc.get("descricao"),
		"quantidade": _to_int(doc.get("quantidade")),
		"valor_unitario": _to_float(doc.get("valor_final_unitario")),
		"valor_total": _to_float(doc.get("valor_final_total")),
		"imagem_produto": doc.get("imagem_produto"),
		"_row": None,
		"_legacy": 1,
	}
	if _is_empty_line(legacy):
		return []
	return [legacy]


def get_orcamento_product_lines(doc):
	lines = []
	for model in _collect_product_line_models(doc):
		lines.append(
			{
				"item": model.get("item"),
				"descricao": model.get("descricao"),
				"quantidade": _to_int(model.get("quantidade")),
				"valor_unitario": _to_float(model.get("valor_unitario")),
				"valor_total": _to_float(model.get("valor_total")),
				"imagem_produto": model.get("imagem_produto"),
			}
		)
	return lines


def get_primary_product_line(doc):
	lines = get_orcamento_product_lines(doc)
	return lines[0] if lines else None


def distribute_total_across_lines(lines, total_value):
	normalized = []
	for line in lines:
		normalized.append(
			{
				"item": line.get("item"),
				"descricao": line.get("descricao"),
				"quantidade": _to_int(line.get("quantidade")),
				"valor_unitario": _to_float(line.get("valor_unitario")),
				"valor_total": _to_float(line.get("valor_total")),
				"imagem_produto": line.get("imagem_produto"),
				"base_total": _to_float(line.get("base_total")),
				"_row": line.get("_row"),
				"_legacy": line.get("_legacy"),
			}
		)

	if not normalized:
		return []

	weights = [max(_to_float(line.get("base_total")), 0.0) for line in normalized]
	weight_total = sum(weights)
	if weight_total <= 0:
		weights = [max(_to_int(line.get("quantidade")), 0) for line in normalized]
		weight_total = sum(weights)
	if weight_total <= 0:
		weights = [1.0 for _ in normalized]
		weight_total = float(len(normalized))

	total_rounded = round(_to_float(total_value), 2)
	running = 0.0
	last_index = len(normalized) - 1
	for index, line in enumerate(normalized):
		if index == last_index:
			line_total = round(total_rounded - running, 2)
		else:
			line_total = round(total_rounded * (weights[index] / weight_total), 2)
			running = round(running + line_total, 2)
		qty = _to_int(line.get("quantidade"))
		line["valor_total"] = line_total
		line["valor_unitario"] = round((line_total / qty), 4) if qty > 0 else 0.0

	return normalized


def build_confirmacao_resumo(doc):
	lines = get_orcamento_product_lines(doc)
	gravacao_metodos = _get_gravacao_metodos(doc)
	if not lines:
		return {
			"item": "Produto personalizado",
			"descricao": "",
			"quantidade": 0,
			"valor_unitario": 0.0,
			"valor_total": 0.0,
		}

	total_qty = sum(_to_int(line.get("quantidade")) for line in lines)
	total_valor = sum(_to_float(line.get("valor_total")) for line in lines)
	if total_valor <= 0:
		total_valor = _to_float(doc.get("valor_final_total"))
	if total_qty <= 0:
		total_qty = _to_int(doc.get("quantidade"))

	if len(lines) == 1:
		line = lines[0]
		item_code = line.get("item")
		item_name = frappe.db.get_value("Item", item_code, "item_name") if item_code else None
		item_description = frappe.db.get_value("Item", item_code, "description") if item_code else None
		descricao = _append_gravacao_metodos(
			line.get("descricao") or doc.get("descrição") or doc.get("descricao") or item_description or "",
			gravacao_metodos,
		)
		item = item_name or descricao or "Produto personalizado"
		valor_total = _to_float(line.get("valor_total")) or total_valor
		quantidade = _to_int(line.get("quantidade")) or total_qty
		valor_unitario = _to_float(line.get("valor_unitario")) or (
			_to_float(valor_total) / quantidade if quantidade > 0 else 0.0
		)
		return {
			"item": item,
			"descricao": descricao,
			"quantidade": quantidade,
			"valor_unitario": valor_unitario,
			"valor_total": valor_total,
		}

	linhas_descricao = []
	for line in lines:
		item_code = line.get("item")
		item_name = frappe.db.get_value("Item", item_code, "item_name") if item_code else None
		nome = _append_gravacao_metodos(
			item_name or line.get("descricao") or "Produto personalizado",
			gravacao_metodos,
		)
		quantidade = _to_int(line.get("quantidade"))
		linhas_descricao.append(f"{nome} (Qtd: {quantidade})")

	valor_unitario_total = (total_valor / total_qty) if total_qty > 0 else 0.0
	return {
		"item": f"Pedido com {len(lines)} itens",
		"descricao": "\n".join(linhas_descricao),
		"quantidade": total_qty,
		"valor_unitario": valor_unitario_total,
		"valor_total": total_valor,
	}


class CalculadoraOrcamento(Document):
	def validate(self):
		self.calculate_all()

	def calculate_all(self):
		line_models = _collect_product_line_models(self)
		total_qty = 0
		base_cost_total = 0.0
		for line in line_models:
			qty = _to_int(line.get("quantidade"))
			total_qty += qty
			if line.get("item") and qty > 0:
				base_unit = _to_float(get_scale_price(line.get("item"), qty))
			else:
				base_unit = _to_float(line.get("valor_unitario"))
			base_total = qty * base_unit if qty > 0 else _to_float(line.get("valor_total"))
			line["base_unit"] = base_unit
			line["base_total"] = base_total
			base_cost_total += base_total

		self.custo_base = (base_cost_total / total_qty) if total_qty > 0 else 0.0

		aliquota_on_base = 0.0
		if self.aplicar_aliquota:
			aliquota_on_base = base_cost_total * ((self.tax_rate or 0.0) / 100.0)
		self.aliquota_calculada = aliquota_on_base

		fotolito_cost = 0.0
		if self.fotolito_value and self.fotolito_value != "N/A":
			try:
				fotolito_cost = float(self.fotolito_value)
			except ValueError:
				fotolito_cost = 0.0

		from calculadora_orcamento.calculadora_orcamento.doctype.catalogo_gravacao.catalogo_gravacao import (
			calcular_custo_gravacao,
		)

		qty_for_gravacao = total_qty if total_qty > 0 else _to_int(self.quantidade)
		total_grav_cost = 0.0
		for row in self.gravacoes:
			if row.catalogo_gravacao:
				result = calcular_custo_gravacao(row.catalogo_gravacao, qty_for_gravacao)
				row.total = result["custo"]
				row.custo_unitario = result.get("custo_unitario", 0.0)
				row.descricao = result["descricao"]
			else:
				unit_cost = row.custo_unitario or 0.0
				if row.unidade == "Milheiro":
					milheiros = math.ceil(qty_for_gravacao / 1000.0)
					row.total = milheiros * unit_cost
				else:
					row.total = qty_for_gravacao * unit_cost
				row.descricao = ""

			total_grav_cost += _to_float(row.total)

		self.total_gravacao = total_grav_cost

		embal_config = frappe.get_cached_doc("Embalagem Config")
		cost_standard_pack = (
			(self.qtd_p or 0) * (embal_config.custo_p or 0)
			+ (self.qtd_m or 0) * (embal_config.custo_m or 0)
			+ (self.qtd_g or 0) * (embal_config.custo_g or 0)
			+ (self.qtd_xg or 0) * (embal_config.custo_xg or 0)
			+ (self.qtd_xxg or 0) * (embal_config.custo_xxg or 0)
		)

		# Custom Packaging
		cost_custom_pack = 0.0
		if self.embal_custom:
			cost_custom_pack = (self.qtd_customizada or 0) * (self.valor_customizada or 0)

		total_embal_cost = cost_standard_pack + cost_custom_pack
		self.custo_total_embalagens = total_embal_cost

		total_despesas = (
			(self.mao_de_obra or 0)
			+ (self.gasoline or 0)
			+ (self.motoboy or 0)
			+ (self.frete or 0)
			+ (self.cliche or 0)
			+ (self.extras or 0)
		)
		self.total_despesas = total_despesas

		if self.tabela_comissao:
			tabela = frappe.get_cached_doc("Tabela Comissao", self.tabela_comissao)
			self.margin = tabela.margem_lucro
			if not self.custom_commission:
				comissao_percent = tabela.comissao
			else:
				comissao_percent = self.comis_custom or 0.0
		else:
			comissao_percent = 0.0

		if self.comis_0:
			comissao_percent = 0.0
		elif not self.tabela_comissao:
			if self.custom_commission:
				comissao_percent = self.comis_custom or 0.0

		if "System Manager" in frappe.get_roles(frappe.session.user):
			pass
		else:
			sales_person_limit = 0.0
			employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
			if employee:
				sales_person = frappe.db.get_value(
					"Sales Person",
					{"employee": employee},
					["name", "custom_max_commission_percent"],
					as_dict=True,
				)
				if sales_person:
					sales_person_limit = sales_person.custom_max_commission_percent

			if sales_person_limit > 0 and comissao_percent > sales_person_limit:
				frappe.throw(f"Limite de comissão excedido! Seu limite é {sales_person_limit}%.")

		total_hard_cost = (
			base_cost_total
			+ aliquota_on_base
			+ fotolito_cost
			+ total_grav_cost
			+ total_embal_cost
			+ total_despesas
		)

		margin_rate = (self.margin or 0.0) / 100.0
		target_revenue = total_hard_cost * (1.0 + margin_rate)

		bv_rate = (self.porcentagem or 0.0) / 100.0
		com_rate = comissao_percent / 100.0
		tax_rate = (self.tax_rate or 0.0) / 100.0

		total_fees_rate = bv_rate + com_rate + tax_rate

		valor_final_total = 0.0
		if total_fees_rate < 1.0:
			valor_final_total = target_revenue / (1.0 - total_fees_rate)
		else:
			frappe.throw("A soma de BV, Comissão e Imposto não pode ser 100% ou mais (Divisão por zero).")

		valor_bv = valor_final_total * bv_rate
		valor_comissao = valor_final_total * com_rate
		valor_imposto = valor_final_total * tax_rate
		priced_lines = distribute_total_across_lines(line_models, valor_final_total)
		computed_total = sum(_to_float(line.get("valor_total")) for line in priced_lines)

		self.total_bv = valor_bv
		self.comissao_receber = valor_comissao
		self.total_tax = valor_imposto
		self.valor_final_total = computed_total
		self.valor_final_unitario = (computed_total / total_qty) if total_qty > 0 else 0.0
		self.quantidade = total_qty

		for line in priced_lines:
			row = line.get("_row")
			if row:
				row.valor_unitario = line.get("valor_unitario")
				row.valor_total = line.get("valor_total")

		primary_line = priced_lines[0] if priced_lines else None
		if primary_line:
			if primary_line.get("item"):
				self.item = primary_line["item"]
			if primary_line.get("descricao"):
				self.set("descrição", primary_line["descricao"])
			if primary_line.get("imagem_produto"):
				self.imagem_produto = primary_line["imagem_produto"]


@frappe.whitelist()
def make_delivery_note(source_name):
	doc = frappe.get_doc("Calculadora Orcamento", source_name)

	company = frappe.defaults.get_defaults().get("company")
	warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")

	dn = frappe.new_doc("Delivery Note")
	dn.customer = doc.nome
	dn.company = company
	dn.orcamento = doc.name
	items_added = 0
	for line in get_orcamento_product_lines(doc):
		line_qty = _to_int(line.get("quantidade"))
		if not line.get("item") or line_qty <= 0:
			continue
		dn.append(
			"items",
			{
				"item_code": line.get("item"),
				"qty": line_qty,
				"rate": _to_float(line.get("valor_unitario")),
				"warehouse": warehouse,
			},
		)
		items_added += 1

	if items_added == 0:
		frappe.throw("Informe ao menos um item com quantidade para criar a Nota de Entrega.")

	dn.insert()

	return dn.name


@frappe.whitelist()
def make_confirmacao_pedido(source_name):
	doc = frappe.get_doc("Calculadora Orcamento", source_name)
	resumo = build_confirmacao_resumo(doc)

	conf = frappe.new_doc("Confirmacao Pedido")
	conf.orcamento = doc.name
	conf.cliente = doc.nome
	conf.telefone = doc.telefone_whatsapp
	conf.item = resumo.get("item")
	conf.descricao = resumo.get("descricao")
	conf.quantidade = resumo.get("quantidade")
	conf.valor_unitario = resumo.get("valor_unitario")
	conf.valor_total = resumo.get("valor_total")

	# Auto-populate address from Customer
	from frappe.contacts.doctype.address.address import get_default_address

	address_name = get_default_address("Customer", doc.nome)
	if address_name:
		addr = frappe.get_doc("Address", address_name)
		conf.endereco_logradouro = addr.address_line1
		conf.endereco_complemento = addr.address_line2
		conf.endereco_bairro = addr.county
		conf.endereco_cidade = addr.city
		conf.endereco_estado = addr.state
		conf.endereco_cep = addr.pincode

	conf.insert()

	return conf.name
