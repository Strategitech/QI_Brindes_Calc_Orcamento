# Copyright (c) 2026, Strategitech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ConfirmacaoPedido(Document):
	def validate(self):
		if self.orcamento:
			self.populate_from_orcamento()

	def populate_from_orcamento(self):
		orc = frappe.get_doc("Calculadora Orcamento", self.orcamento)
		self.cliente = orc.nome
		self.telefone = orc.telefone_whatsapp
		self.item = orc.item
		self.descricao = orc.get("descrição") or orc.get("descricao") or ""
		self.quantidade = orc.quantidade
		self.valor_unitario = orc.valor_final_unitario
		self.valor_total = orc.valor_final_total
