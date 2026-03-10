# Copyright (c) 2026, Strategitech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from calculadora_orcamento.calculadora_orcamento.doctype.calculadora_orcamento.calculadora_orcamento import (
	build_confirmacao_resumo,
)


class ConfirmacaoPedido(Document):
	def validate(self):
		if self.orcamento:
			self.populate_from_orcamento()

	def populate_from_orcamento(self):
		orc = frappe.get_doc("Calculadora Orcamento", self.orcamento)
		resumo = build_confirmacao_resumo(orc)
		self.cliente = orc.nome
		self.telefone = orc.telefone_whatsapp
		self.item = resumo.get("item")
		self.descricao = resumo.get("descricao")
		self.quantidade = resumo.get("quantidade")
		self.valor_unitario = resumo.get("valor_unitario")
		self.valor_total = resumo.get("valor_total")

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
