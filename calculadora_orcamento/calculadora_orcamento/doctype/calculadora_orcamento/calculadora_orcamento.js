// Copyright (c) 2025, Strategitech and contributors
// For license information, please see license.txt

const IMAGE_FILE_REGEX = /\.(jpg|jpeg|png|gif|webp|svg)(\?.*)?$/i;

function is_image_url(url) {
	if (!url) return false;
	if (/^data:image\//i.test(url)) return true;
	if (frappe.utils && typeof frappe.utils.is_image_file === "function") {
		return frappe.utils.is_image_file(url);
	}
	return IMAGE_FILE_REGEX.test(url);
}

function add_image_url(target, raw_value, allow_non_image = false) {
	if (!raw_value) return;
	String(raw_value)
		.split(/[\n;]+/)
		.map((value) => value.trim())
		.filter(Boolean)
		.forEach((value) => {
			if (allow_non_image || is_image_url(value)) {
				target.add(value);
			}
		});
}

function ensure_image_picker_styles() {
	if (document.getElementById("qi-image-picker-style")) return;

	const style = document.createElement("style");
	style.id = "qi-image-picker-style";
	style.textContent = `
		[data-fieldname="imagem_produto"] .control-input-wrapper,
		[data-fieldname="imagem_produto"] .control-value,
		[data-fieldname="imagem_produto"] .attached-file,
		[data-fieldname="imagem_produto"] .btn-attach,
		[data-fieldname="imagem_produto"] .attached-file-link {
			display: none !important;
		}

		.qi-image-picker-host {
			margin-top: 8px;
		}

		.qi-image-picker-host .qi-image-picker {
			display: flex;
			flex-wrap: wrap;
			gap: 8px;
		}

		.qi-image-picker-host .qi-image-option {
			border: 2px solid transparent;
			border-radius: 6px;
			padding: 3px;
			background: #fff;
			cursor: pointer;
			line-height: 0;
		}

		.qi-image-picker-host .qi-image-option:hover {
			border-color: #1b8fdb;
		}

		.qi-image-picker-host .qi-image-option.is-selected {
			border-color: #223985;
			box-shadow: 0 0 0 1px #223985 inset;
		}

		.qi-image-picker-host .qi-image-option img {
			width: 96px;
			height: 96px;
			object-fit: contain;
			display: block;
		}

		.qi-image-picker-host .qi-image-picker-help {
			font-size: 12px;
			color: #667085;
			margin: 0;
		}
	`;

	document.head.appendChild(style);
}

function fetch_item_images(frm) {
	if (!frm.doc.item) return Promise.resolve([]);

	return Promise.all([
		frappe.db
			.get_value("Item", frm.doc.item, "image")
			.then((r) => {
				if (r && r.message && r.message.image) return r.message.image;
				return r && r.image ? r.image : null;
			})
			.catch(() => null),
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
					limit_page_length: 200,
				},
				callback: (r) => resolve(r.message || []),
				error: () => resolve([]),
			});
		}),
	]).then(([main_image, files]) => {
		const urls = new Set();
		add_image_url(urls, main_image);
		files.forEach((file_doc) => {
			add_image_url(urls, file_doc.file_url);
		});
		add_image_url(urls, frm.doc.imagem_produto, true);
		return Array.from(urls);
	});
}

function get_image_picker_host(frm) {
	const imageField = frm.fields_dict.imagem_produto;
	const itemField = frm.fields_dict.item;
	const $imageWrapper = imageField && imageField.$wrapper ? imageField.$wrapper : null;
	const $itemWrapper = itemField && itemField.$wrapper ? itemField.$wrapper : null;

	if ($imageWrapper && $imageWrapper.length) {
		$imageWrapper.find("> .qi-image-picker-host").remove();
	}
	if ($itemWrapper && $itemWrapper.length) {
		$itemWrapper.find("> .qi-image-picker-host").remove();
	}

	const useImageWrapper =
		$imageWrapper && $imageWrapper.length && $imageWrapper.is(":visible");
	const $target = useImageWrapper ? $imageWrapper : $itemWrapper;
	if (!$target || !$target.length) return null;

	const $host = $('<div class="qi-image-picker-host"></div>');
	$target.append($host);
	return $host;
}

function render_inline_image_picker(frm, images) {
	const $host = get_image_picker_host(frm);
	if (!$host) return;

	if (!frm.doc.item) {
		$host.append(
			`<div class="qi-image-picker-help">${__("Selecione um item para ver as imagens disponíveis.")}</div>`
		);
		return;
	}

	if (!images.length) {
		$host.append(
			`<div class="qi-image-picker-help">${__("Nenhuma imagem encontrada para este item.")}</div>`
		);
		return;
	}

	const selected = frm.doc.imagem_produto || "";
	const $picker = $('<div class="qi-image-picker"></div>');

	images.forEach((url) => {
		const $button = $('<button type="button" class="qi-image-option"></button>');
		if (url === selected) {
			$button.addClass("is-selected");
		}

		$button.attr("title", url);
		$button.append($("<img>").attr("src", url).attr("alt", __("Imagem do Produto")));
		$button.on("click", () => {
			frm.set_value("imagem_produto", url);
		});

		$picker.append($button);
	});

	const $refresh_button = $(
		'<button class="btn btn-xs btn-default btn-change-image" style="margin-top:8px;">Atualizar Imagens</button>'
	);
	$refresh_button.on("click", () => open_image_picker(frm, true));

	$host.append($picker);
	$host.append($refresh_button);
}

function open_image_picker(frm, force_reload = false) {
	ensure_image_picker_styles();

	if (!frm.doc.item) {
		render_inline_image_picker(frm, []);
		return;
	}

	if (!force_reload && frm.__item_images_cache && frm.__item_images_cache.item === frm.doc.item) {
		render_inline_image_picker(frm, frm.__item_images_cache.images || []);
		return;
	}

	fetch_item_images(frm).then((images) => {
		frm.__item_images_cache = { item: frm.doc.item, images };
		render_inline_image_picker(frm, images);
	});
}

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

		open_image_picker(frm);
	},

	item(frm) {
		frm.__item_images_cache = null;
		frm.set_value("imagem_produto", "");
		open_image_picker(frm, true);
	},

	imagem_produto(frm) {
		const cached = frm.__item_images_cache;
		if (cached && cached.item === frm.doc.item) {
			render_inline_image_picker(frm, cached.images || []);
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
								frappe.model.set_value(
									row.doctype,
									row.name,
									"descricao",
									r.message.descricao
								);
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
