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
		if (!frm.doc.item) return;

		// Fetch Item main image + all attached image files
		Promise.all([
			new Promise((resolve) => {
				frappe.db.get_value("Item", frm.doc.item, "image", (r) => {
					resolve(r && r.image ? r.image : null);
				});
			}),
			new Promise((resolve) => {
				frappe.call({
					method: "frappe.client.get_list",
					args: {
						doctype: "File",
						filters: {
							attached_to_doctype: "Item",
							attached_to_name: frm.doc.item,
							is_folder: 0,
						},
						fields: ["file_url"],
						limit_page_length: 50,
					},
					callback: (r) => resolve(r.message || []),
				});
			}),
		]).then(([main_image, files]) => {
			let urls = new Set();
			if (main_image) urls.add(main_image);
			files.forEach((f) => {
				if (/\.(jpg|jpeg|png|gif|webp|svg)$/i.test(f.file_url || "")) {
					urls.add(f.file_url);
				}
			});

			let images = Array.from(urls);
			if (images.length === 0) return;

			if (images.length === 1) {
				frm.set_value("imagem_produto", images[0]);
				return;
			}

			// Multiple images — show picker dialog
			let html = '<div style="display:flex;flex-wrap:wrap;gap:12px;justify-content:center;">';
			images.forEach((url) => {
				html +=
					`<div class="img-pick" data-url="${url}" style="cursor:pointer;border:3px solid transparent;border-radius:6px;padding:4px;">` +
					`<img src="${url}" style="max-width:160px;max-height:160px;object-fit:contain;border-radius:4px;">` +
					`</div>`;
			});
			html += "</div>";

			let d = new frappe.ui.Dialog({
				title: __("Selecione a Imagem do Produto"),
				fields: [{ fieldtype: "HTML", options: html }],
			});
			d.show();

			d.$wrapper.find(".img-pick").on("click", function () {
				frm.set_value("imagem_produto", $(this).data("url"));
				d.hide();
			});
			d.$wrapper.find(".img-pick").on("mouseenter", function () {
				$(this).css("border-color", "#1b8fdb");
			});
			d.$wrapper.find(".img-pick").on("mouseleave", function () {
				$(this).css("border-color", "transparent");
			});
		});
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
