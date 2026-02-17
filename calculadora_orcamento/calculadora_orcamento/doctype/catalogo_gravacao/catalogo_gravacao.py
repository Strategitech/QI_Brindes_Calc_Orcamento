# Copyright (c) 2026, Strategitech and contributors
# For license information, please see license.txt

import math

import frappe
from frappe.model.document import Document


class CatalogoGravacao(Document):
	def autoname(self):
		self.title = f"{self.metodo_gravacao} - {self.categoria_produto}"
		self.name = self.title

	def before_save(self):
		self.title = f"{self.metodo_gravacao} - {self.categoria_produto}"


def calcular_custo_gravacao(catalogo_name, qty):
	"""Calculate engraving cost from catalog entry for a given quantity."""
	doc = frappe.get_doc("Catalogo Gravacao", catalogo_name)
	qty = int(qty or 0)

	if qty <= 0:
		return {"custo": 0.0, "descricao": "Quantidade zero"}

	for faixa in doc.faixas:
		in_range = qty >= faixa.qty_min
		if faixa.qty_max and faixa.qty_max > 0:
			in_range = in_range and qty <= faixa.qty_max

		if in_range:
			preco = faixa.preco or 0.0

			if faixa.tipo == "Minimo":
				custo = preco
				desc = f"Minimo: R${preco:,.2f}"
			elif faixa.tipo == "Unitario":
				custo = qty * preco
				desc = f"Unitario: {qty} x R${preco:,.2f} = R${custo:,.2f}"
			elif faixa.tipo == "Milheiro":
				milheiros = math.ceil(qty / 1000.0)
				custo = milheiros * preco
				desc = f"Milheiro: {milheiros} x R${preco:,.2f} = R${custo:,.2f}"
			else:
				custo = 0.0
				desc = "Tipo desconhecido"

			return {"custo": custo, "descricao": desc}

	return {"custo": 0.0, "descricao": "Nenhuma faixa encontrada para esta quantidade"}


@frappe.whitelist()
def get_custo_gravacao(catalogo_name, qty):
	"""Whitelisted API to get engraving cost from catalog."""
	return calcular_custo_gravacao(catalogo_name, qty)
