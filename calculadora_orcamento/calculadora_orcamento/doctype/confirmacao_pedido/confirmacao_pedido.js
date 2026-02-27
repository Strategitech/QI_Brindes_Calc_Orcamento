// Copyright (c) 2026, Strategitech and contributors
// For license information, please see license.txt

frappe.ui.form.on("Confirmacao Pedido", {
	orcamento(frm) {
		if (frm.doc.orcamento) {
			frappe.db.get_doc("Calculadora Orcamento", frm.doc.orcamento).then((orc) => {
				frm.set_value("cliente", orc.nome);
				frm.set_value("telefone", orc.telefone_whatsapp);
				frm.set_value("descricao", orc.descrição || orc.descricao || "");
				frm.set_value("quantidade", orc.quantidade);
				frm.set_value("valor_unitario", orc.valor_final_unitario);
				frm.set_value("valor_total", orc.valor_final_total);

				if (orc.item) {
					frappe.db.get_value("Item", orc.item, ["item_name", "description"], (r) => {
						const item_name = r && r.item_name ? r.item_name : "";
						const item_description = r && r.description ? r.description : "";

						frm.set_value("item", item_name || orc.descrição || orc.descricao || "Produto personalizado");
						if (!frm.doc.descricao) {
							frm.set_value("descricao", orc.descrição || orc.descricao || item_description || "");
						}
					});
				}

				// Fetch address from Customer
				if (orc.nome) {
					frappe.call({
						method: "frappe.contacts.doctype.address.address.get_default_address",
						args: { doctype: "Customer", name: orc.nome },
						callback: function (r) {
							if (r.message) {
								frappe.db.get_doc("Address", r.message).then((addr) => {
									if (!frm.doc.endereco_logradouro) {
										frm.set_value("endereco_logradouro", addr.address_line1 || "");
									}
									if (!frm.doc.endereco_complemento) {
										frm.set_value("endereco_complemento", addr.address_line2 || "");
									}
									if (!frm.doc.endereco_bairro) {
										frm.set_value("endereco_bairro", addr.county || "");
									}
									if (!frm.doc.endereco_cidade) {
										frm.set_value("endereco_cidade", addr.city || "");
									}
									if (!frm.doc.endereco_estado) {
										frm.set_value("endereco_estado", addr.state || "");
									}
									if (!frm.doc.endereco_cep) {
										frm.set_value("endereco_cep", addr.pincode || "");
									}
								});
							}
						},
					});
				}
			});
		}
	},
});
