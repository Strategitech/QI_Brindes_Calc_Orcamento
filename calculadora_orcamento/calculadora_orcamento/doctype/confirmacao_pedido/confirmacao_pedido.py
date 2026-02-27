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
		item_details = (
			frappe.db.get_value("Item", orc.item, ["item_name", "description"], as_dict=True)
			if orc.item
			else None
		)
		item_name = item_details.item_name if item_details and item_details.item_name else None
		item_description = item_details.description if item_details and item_details.description else ""
		self.cliente = orc.nome
		self.telefone = orc.telefone_whatsapp
		self.item = item_name or (orc.get("descrição") or orc.get("descricao") or "Produto personalizado")
		self.descricao = orc.get("descrição") or orc.get("descricao") or item_description or ""
		self.quantidade = orc.quantidade
		self.valor_unitario = orc.valor_final_unitario
		self.valor_total = orc.valor_final_total

		# Auto-populate address from Customer
		from frappe.contacts.doctype.address.address import get_default_address

		address_name = get_default_address("Customer", orc.nome)
		if address_name:
			addr = frappe.get_doc("Address", address_name)
			if not self.endereco_logradouro:
				self.endereco_logradouro = addr.address_line1
			if not self.endereco_complemento:
				self.endereco_complemento = addr.address_line2
			if not self.endereco_bairro:
				self.endereco_bairro = addr.county
			if not self.endereco_cidade:
				self.endereco_cidade = addr.city
			if not self.endereco_estado:
				self.endereco_estado = addr.state
			if not self.endereco_cep:
				self.endereco_cep = addr.pincode
