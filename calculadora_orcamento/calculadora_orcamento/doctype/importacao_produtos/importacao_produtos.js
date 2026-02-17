// Copyright (c) 2026, Strategitech and contributors
// For license information, please see license.txt

frappe.ui.form.on("Importacao Produtos", {
	refresh(frm) {
		if (frm.doc.status === "Processando") {
			frm.add_custom_button(__("Atualizar Status"), function () {
				frm.reload_doc();
			});
		}
	},
});
