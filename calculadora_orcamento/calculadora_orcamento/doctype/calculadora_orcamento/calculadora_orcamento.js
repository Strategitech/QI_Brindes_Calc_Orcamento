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

			frm.add_custom_button(__("Gerar Confirmacao de Pedido"), function () {
				frappe.call({
					method:
						"calculadora_orcamento.calculadora_orcamento.doctype.calculadora_orcamento.calculadora_orcamento.make_confirmacao_pedido",
					args: { source_name: frm.doc.name },
					freeze: true,
					freeze_message: __("Criando Confirmação de Pedido..."),
					callback: function (r) {
						if (r.message) {
							frappe.set_route("Form", "Confirmacao Pedido", r.message);
						}
					},
				});
			});
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

	item(frm) {
		if (frm.doc.item) {
			frappe.db.get_value("Item", frm.doc.item, "image", (r) => {
				if (r && r.image) {
					frm.set_value("imagem_produto", r.image);
				}
			});
		}
	},

	tabela_comissao(frm) {
		if (frm.doc.tabela_comissao) {
			frappe.db.get_doc("Tabela Comissao", frm.doc.tabela_comissao).then((doc) => {
				frm.set_value("margin", doc.margem_lucro);
				if (!frm.doc.custom_commission) {
					frm.set_value("comis_custom", doc.comissao);
				}
			});
		}
	},

	quantidade(frm) {
		// Refresh all gravacao child rows when quantity changes
		if (frm.doc.gravacoes && frm.doc.gravacoes.length > 0) {
			frm.doc.gravacoes.forEach(function (row) {
				if (row.catalogo_gravacao) {
					frappe.call({
						method:
							"calculadora_orcamento.calculadora_orcamento.doctype.catalogo_gravacao.catalogo_gravacao.get_custo_gravacao",
						args: { catalogo_name: row.catalogo_gravacao, qty: frm.doc.quantidade || 0 },
						callback: function (r) {
							if (r.message) {
								frappe.model.set_value(row.doctype, row.name, "descricao", r.message.descricao);
							}
						},
					});
				}
			});
		}
	},
});

frappe.ui.form.on("Gravacao Item", {
	catalogo_gravacao(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		var qty = frm.doc.quantidade || 0;

		if (!row.catalogo_gravacao) {
			frappe.model.set_value(cdt, cdn, "descricao", "");
			return;
		}

		if (qty <= 0) {
			frappe.model.set_value(cdt, cdn, "descricao", "Informe a quantidade");
			return;
		}

		frappe.call({
			method:
				"calculadora_orcamento.calculadora_orcamento.doctype.catalogo_gravacao.catalogo_gravacao.get_custo_gravacao",
			args: { catalogo_name: row.catalogo_gravacao, qty: qty },
			callback: function (r) {
				if (r.message) {
					frappe.model.set_value(cdt, cdn, "descricao", r.message.descricao);
				}
			},
		});
	},
});
