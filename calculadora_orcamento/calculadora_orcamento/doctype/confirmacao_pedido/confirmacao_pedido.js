// Copyright (c) 2026, Strategitech and contributors
// For license information, please see license.txt

frappe.ui.form.on("Confirmacao Pedido", {
	orcamento(frm) {
		if (frm.doc.orcamento) {
			frappe.db.get_doc("Calculadora Orcamento", frm.doc.orcamento).then((orc) => {
				frm.set_value("cliente", orc.nome);
				frm.set_value("telefone", orc.telefone_whatsapp);
				frm.set_value("item", orc.item);
				frm.set_value("descricao", orc.descrição || "");
				frm.set_value("quantidade", orc.quantidade);
				frm.set_value("valor_unitario", orc.valor_final_unitario);
				frm.set_value("valor_total", orc.valor_final_total);
			});
		}
	},
});
