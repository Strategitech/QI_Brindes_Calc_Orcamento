// Copyright (c) 2025, Strategitech and contributors
// For license information, please see license.txt

frappe.ui.form.on("Calculadora Orcamento", {
	refresh(frm) {
		if (frm.doc.docstatus === 0 && !frm.is_new()) {
			frm.add_custom_button(__("Criar Nota de Entrega"), function () {
				frappe.call({
					method:
						"calculadora_orcamento.calculadora_orcamento.doctype.calculadora_orcamento.calculadora_orcamento.make_delivery_note",
					args: { source_name: frm.doc.name },
					freeze: true,
					freeze_message: __("Criando Nota de Entrega..."),
					callback: function (r) {
						if (r.message) {
							frappe.set_route("Form", "Delivery Note", r.message);
						}
					},
				});
			}).addClass("btn-primary");
		}
	},
});
