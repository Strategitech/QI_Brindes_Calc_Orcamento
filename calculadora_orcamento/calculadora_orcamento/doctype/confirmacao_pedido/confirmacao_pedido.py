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
		self.item = frappe.db.get_value("Item", orc.item, "item_name") or orc.item
		self.descricao = orc.get("descrição") or orc.get("descricao") or ""
		self.quantidade = orc.quantidade
		self.valor_unitario = orc.valor_final_unitario
		self.valor_total = orc.valor_final_total

		# Auto-populate address from Customer
		from frappe.contacts.doctype.address.address import get_default_address
		address_name = get_default_address("Customer", orc.nome)
		if address_name:
			addr = frappe.get_doc("Address", address_name)
			self.endereco_logradouro = addr.address_line1
			self.endereco_complemento = addr.address_line2
			self.endereco_cidade = addr.city
			self.endereco_estado = addr.state
			self.endereco_cep = addr.pincode
