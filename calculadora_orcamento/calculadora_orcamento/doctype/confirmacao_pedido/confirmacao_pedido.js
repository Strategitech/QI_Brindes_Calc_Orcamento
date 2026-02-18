// Copyright (c) 2026, Strategitech and contributors
// For license information, please see license.txt

frappe.ui.form.on("Confirmacao Pedido", {
	orcamento(frm) {
		if (frm.doc.orcamento) {
			frappe.db.get_doc("Calculadora Orcamento", frm.doc.orcamento).then((orc) => {
				frm.set_value("cliente", orc.nome);
				frm.set_value("telefone", orc.telefone_whatsapp);
				frm.set_value("descricao", orc.descrição || "");
				frm.set_value("quantidade", orc.quantidade);
				frm.set_value("valor_unitario", orc.valor_final_unitario);
				frm.set_value("valor_total", orc.valor_final_total);

				// Fetch item_name instead of item_code to hide supplier
				if (orc.item) {
					frappe.db.get_value("Item", orc.item, "item_name", (r) => {
						if (r && r.item_name) {
							frm.set_value("item", r.item_name);
						} else {
							frm.set_value("item", orc.item);
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
									frm.set_value("endereco_logradouro", addr.address_line1 || "");
									frm.set_value("endereco_complemento", addr.address_line2 || "");
									frm.set_value("endereco_cidade", addr.city || "");
									frm.set_value("endereco_estado", addr.state || "");
									frm.set_value("endereco_cep", addr.pincode || "");
								});
							}
						},
					});
				}
			});
		}
	},
});
