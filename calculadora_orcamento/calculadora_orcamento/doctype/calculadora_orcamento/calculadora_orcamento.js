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

		if (!frm.is_new()) {
			frm.add_custom_button(__("Enviar WhatsApp"), function () {
				frappe.call({
					method: "whatsapp_integration.whatsapp_integration.api.get_available_templates",
					args: { doctype: frm.doc.doctype },
					callback: function (r) {
						if (!r.message || r.message.length === 0) {
							frappe.msgprint(
								__("Nenhum template WhatsApp configurado para este DocType.")
							);
							return;
						}

						let template_options = r.message.map((t) => t.template_name);

						let d = new frappe.ui.Dialog({
							title: __("Enviar WhatsApp"),
							fields: [
								{
									fieldname: "template",
									fieldtype: "Select",
									label: __("Template"),
									options: template_options,
									reqd: 1,
								},
								{
									fieldname: "phone_preview",
									fieldtype: "Data",
									label: __("Telefone"),
									read_only: 1,
									default: frm.doc.telefone_whatsapp || "",
								},
							],
							primary_action_label: __("Enviar"),
							primary_action(values) {
								d.hide();
								frappe.call({
									method:
										"whatsapp_integration.whatsapp_integration.api.send_template_message",
									args: {
										doctype: frm.doc.doctype,
										docname: frm.doc.name,
										template_name: values.template,
									},
									freeze: true,
									freeze_message: __("Enviando WhatsApp..."),
									callback: function (resp) {
										if (resp.message) {
											frappe.msgprint(
												__("WhatsApp enviado! Message ID: {0}", [
													resp.message.message_id,
												])
											);
										}
									},
								});
							},
						});
						d.show();
					},
				});
			});
		}
	},
});
