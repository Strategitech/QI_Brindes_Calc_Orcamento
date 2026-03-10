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

		.qi-image-picker-host .qi-image-picker-actions {
			display: flex;
			gap: 8px;
			margin-top: 8px;
		}

		.qi-image-picker-host .qi-image-picker-status {
			font-size: 12px;
			margin-top: 6px;
			color: #475467;
		}

		.qi-row-image-pickers {
			margin-top: 12px;
		}

		.qi-row-image-picker-host {
			border: 1px solid #e4e7ec;
			border-radius: 8px;
			padding: 8px;
			margin-bottom: 8px;
			background: #f8fafc;
		}

		.qi-row-image-picker-title {
			font-size: 12px;
			font-weight: 700;
			color: #344054;
			margin: 0 0 6px 0;
		}
	`;

	document.head.appendChild(style);
}

function fetch_item_images(frm) {
	return fetch_item_images_for_item(frm.doc.item, frm.doc.imagem_produto);
}

function fetch_item_images_for_item(item_code, selected_image = "") {
	if (!item_code) return Promise.resolve([]);

	return Promise.all([
		frappe.db
			.get_value("Item", item_code, "image")
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
						attached_to_name: item_code,
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
		add_image_url(urls, selected_image, true);
		return Array.from(urls);
	});
}

function get_row_image_picker_host(frm, cdn) {
	const produtos_field = frm.fields_dict.produtos;
	const $wrapper = produtos_field && produtos_field.$wrapper;
	if (!$wrapper || !$wrapper.length) {
		return null;
	}

	let $container = $wrapper.find("> .qi-row-image-pickers");
	if (!$container.length) {
		$container = $('<div class="qi-row-image-pickers"></div>');
		$wrapper.append($container);
	}

	let $host = $container.find(`.qi-row-image-picker-host[data-row-cdn="${cdn}"]`);
	if (!$host.length) {
		$host = $('<div class="qi-row-image-picker-host qi-image-picker-host"></div>');
		$host.attr("data-row-cdn", cdn);
		$container.append($host);
	}

	$host.empty();
	return $host;
}

function render_row_image_picker(frm, cdt, cdn, images) {
	const row = locals[cdt] && locals[cdt][cdn];
	if (!row) {
		return;
	}

	const $host = get_row_image_picker_host(frm, cdn);
	if (!$host) {
		return;
	}

	const row_title = row.item
		? __("Linha {0}: {1}", [row.idx || "-", row.item])
		: __("Linha {0}", [row.idx || "-"]);
	$host.append(`<div class="qi-row-image-picker-title">${row_title}</div>`);

	if (!row.item) {
		$host.append(
			`<div class="qi-image-picker-help">${__("Selecione o item nesta linha para ver as imagens disponíveis.")}</div>`
		);
		return;
	}

	if (!images.length) {
		$host.append(
			`<div class="qi-image-picker-help">${__("Nenhuma imagem encontrada para este item nesta linha.")}</div>`
		);
		return;
	}

	const selected = row.imagem_produto || "";
	const $picker = $('<div class="qi-image-picker"></div>');

	images.forEach((url) => {
		const $button = $('<button type="button" class="qi-image-option"></button>');
		if (url === selected) {
			$button.addClass("is-selected");
		}

		$button.attr("title", url);
		$button.append($("<img>").attr("src", url).attr("alt", __("Imagem do Produto")));
		$button.on("click", () => {
			frappe.model.set_value(cdt, cdn, "imagem_produto", url);
		});

		$picker.append($button);
	});

	const $actions = $('<div class="qi-image-picker-actions"></div>');
	const $refresh_button = $(
		'<button class="btn btn-xs btn-default btn-change-image" type="button">Atualizar Imagens desta Linha</button>'
	);
	$refresh_button.on("click", () => open_row_image_picker(frm, cdt, cdn, true));
	$actions.append($refresh_button);

	const status_text = selected
		? __("Imagem selecionada para esta linha.")
		: __("Selecione uma imagem para esta linha.");

	$host.append($picker);
	$host.append($actions);
	$host.append(`<div class="qi-image-picker-status">${status_text}</div>`);
}

function open_row_image_picker(frm, cdt, cdn, force_reload = false) {
	const row = locals[cdt] && locals[cdt][cdn];
	if (!row) {
		return;
	}

	if (!row.item) {
		render_row_image_picker(frm, cdt, cdn, []);
		return;
	}

	const cache_by_row = frm.__row_item_images_cache || {};
	const cache_key = `${cdn}:${row.item}`;

	if (!force_reload && Array.isArray(cache_by_row[cache_key])) {
		render_row_image_picker(frm, cdt, cdn, cache_by_row[cache_key]);
		return;
	}

	fetch_item_images_for_item(row.item, row.imagem_produto).then((images) => {
		const prefix = `${cdn}:`;
		Object.keys(cache_by_row).forEach((key) => {
			if (key.startsWith(prefix) && key !== cache_key) {
				delete cache_by_row[key];
			}
		});

		cache_by_row[cache_key] = images;
		frm.__row_item_images_cache = cache_by_row;
		render_row_image_picker(frm, cdt, cdn, images);
	});
}

function render_all_row_image_pickers(frm, force_reload = false) {
	const rows = Array.isArray(frm.doc.produtos) ? frm.doc.produtos : [];
	const produtos_field = frm.fields_dict.produtos;
	const $wrapper = produtos_field && produtos_field.$wrapper;
	if (!$wrapper || !$wrapper.length) {
		return;
	}

	const $container = $wrapper.find("> .qi-row-image-pickers");
	if (!rows.length) {
		$container.remove();
		return;
	}

	if ($container.length) {
		const active_cdns = new Set(rows.map((row) => row.name));
		$container.find(".qi-row-image-picker-host").each((_, el) => {
			const cdn = $(el).attr("data-row-cdn");
			if (!active_cdns.has(cdn)) {
				$(el).remove();
			}
		});
	}

	rows.forEach((row) => {
		open_row_image_picker(frm, row.doctype, row.name, force_reload);
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

	const $actions = $('<div class="qi-image-picker-actions"></div>');
	const $lock_button = $(
		'<button class="btn btn-xs btn-primary btn-lock-image" type="button">Fixar Imagem no Orcamento</button>'
	);
	if (!selected) {
		$lock_button.prop("disabled", true);
	}
	$lock_button.on("click", () => {
		if (!frm.doc.imagem_produto) {
			frappe.msgprint(__("Selecione uma imagem antes de fixar."));
			return;
		}

		$lock_button.prop("disabled", true);
		frm
			.save()
			.then(() => {
				frappe.show_alert({
					message: __("Imagem fixada e salva para impressao."),
					indicator: "green",
				});
				open_image_picker(frm, true);
			})
			.catch(() => {
				$lock_button.prop("disabled", false);
			});
	});
	$actions.append($lock_button);

	const $refresh_button = $(
		'<button class="btn btn-xs btn-default btn-change-image" style="margin-top:8px;">Atualizar Imagens</button>'
	);
	$refresh_button.on("click", () => open_image_picker(frm, true));
	$actions.append($refresh_button);

	const status_text = selected
		? frm.is_dirty()
			? __("Imagem selecionada, clique em Fixar para garantir no PDF.")
			: __("Imagem ja fixada e salva para o PDF.")
		: __("Selecione uma imagem e clique em Fixar Imagem no Orcamento.");

	$host.append($picker);
	$host.append($actions);
	$host.append(`<div class="qi-image-picker-status">${status_text}</div>`);
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

function normalize_numeric(value) {
	const parsed = Number(value || 0);
	return Number.isFinite(parsed) ? parsed : 0;
}

function get_active_product_rows(frm) {
	return (frm.doc.produtos || []).filter(
		(row) =>
			row.item ||
			row.descricao ||
			normalize_numeric(row.quantidade) > 0 ||
			normalize_numeric(row.valor_unitario) > 0 ||
			normalize_numeric(row.valor_total) > 0
	);
}

function update_row_total(row) {
	const quantidade = normalize_numeric(row.quantidade);
	const valor_unitario = normalize_numeric(row.valor_unitario);
	row.valor_total = quantidade * valor_unitario;
	return row.valor_total;
}

function ensure_primary_product_line(frm) {
	const hasRows = Array.isArray(frm.doc.produtos) && frm.doc.produtos.length > 0;
	if (hasRows || (!frm.doc.item && !frm.doc.quantidade && !frm.doc["descrição"] && !frm.doc.descricao)) {
		return;
	}

	const row = frm.add_child("produtos", {
		item: frm.doc.item || "",
		imagem_produto: frm.doc.imagem_produto || "",
		descricao: frm.doc["descrição"] || frm.doc.descricao || "",
		quantidade: frm.doc.quantidade || 0,
		valor_unitario: frm.doc.valor_final_unitario || 0,
		valor_total: frm.doc.valor_final_total || 0,
	});

	if (row) {
		update_row_total(row);
		frm.refresh_field("produtos");
	}
}

function sync_primary_product_line(frm) {
	if (!Array.isArray(frm.doc.produtos) || frm.doc.produtos.length === 0) {
		return;
	}

	const row = frm.doc.produtos[0];
	if (!row.item && frm.doc.item) {
		row.item = frm.doc.item;
	}
	if (!row.imagem_produto && frm.doc.imagem_produto) {
		row.imagem_produto = frm.doc.imagem_produto;
	}
	if (!row.descricao && (frm.doc["descrição"] || frm.doc.descricao)) {
		row.descricao = frm.doc["descrição"] || frm.doc.descricao;
	}
	if (!normalize_numeric(row.quantidade) && normalize_numeric(frm.doc.quantidade)) {
		row.quantidade = normalize_numeric(frm.doc.quantidade);
	}
	if (!normalize_numeric(row.valor_unitario) && normalize_numeric(frm.doc.valor_final_unitario)) {
		row.valor_unitario = normalize_numeric(frm.doc.valor_final_unitario);
	}
	update_row_total(row);
	frm.refresh_field("produtos");
}

function sync_legacy_fields_from_product_rows(frm) {
	const rows = get_active_product_rows(frm);
	if (!rows.length) {
		return;
	}

	rows.forEach((row) => {
		update_row_total(row);
	});

	const primary = rows[0];
	const total_qty = rows.reduce((sum, row) => sum + normalize_numeric(row.quantidade), 0);
	const total_value = rows.reduce((sum, row) => sum + normalize_numeric(row.valor_total), 0);

	frm.doc.item = primary.item || frm.doc.item || "";
	if (primary.imagem_produto) {
		frm.doc.imagem_produto = primary.imagem_produto;
	}
	if (primary.descricao) {
		frm.doc["descrição"] = primary.descricao;
		frm.doc.descricao = primary.descricao;
	}
	frm.doc.quantidade = total_qty;
	frm.doc.valor_final_total = total_value;
	frm.doc.valor_final_unitario = total_qty > 0 ? total_value / total_qty : 0;

	[
		"produtos",
		"item",
		"imagem_produto",
		"descrição",
		"quantidade",
		"valor_final_total",
		"valor_final_unitario",
	].forEach((fieldname) => {
		frm.refresh_field(fieldname);
	});
}

function refresh_gravacoes_from_total_quantity(frm) {
	if (!frm.doc.gravacoes || frm.doc.gravacoes.length === 0) {
		return;
	}

	const qty = normalize_numeric(frm.doc.quantidade);
	frm.doc.gravacoes.forEach((row) => {
		if (!row.catalogo_gravacao) {
			return;
		}

		frappe.call({
			method:
				"calculadora_orcamento.calculadora_orcamento.doctype.catalogo_gravacao.catalogo_gravacao.get_custo_gravacao",
			args: { catalogo_name: row.catalogo_gravacao, qty },
			callback: (response) => {
				if (!response.message) {
					return;
				}

				frappe.model.set_value(row.doctype, row.name, "custo_unitario", response.message.custo_unitario || 0);
				frappe.model.set_value(row.doctype, row.name, "total", response.message.custo || 0);
				frappe.model.set_value(row.doctype, row.name, "descricao", response.message.descricao || "");
			},
		});
	});
}

frappe.ui.form.on("Calculadora Orcamento", {
	refresh(frm) {
		ensure_primary_product_line(frm);
		sync_legacy_fields_from_product_rows(frm);
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
		render_all_row_image_pickers(frm);
	},

	item(frm) {
		frm.__item_images_cache = null;
		frm.__row_item_images_cache = null;
		frm.set_value("imagem_produto", "");
		sync_primary_product_line(frm);
		sync_legacy_fields_from_product_rows(frm);
		open_image_picker(frm, true);
		render_all_row_image_pickers(frm, true);
	},

	imagem_produto(frm) {
		sync_primary_product_line(frm);
		sync_legacy_fields_from_product_rows(frm);
		const cached = frm.__item_images_cache;
		if (cached && cached.item === frm.doc.item) {
			render_inline_image_picker(frm, cached.images || []);
		}
		render_all_row_image_pickers(frm, true);
	},

	produtos_add(frm) {
		sync_legacy_fields_from_product_rows(frm);
		refresh_gravacoes_from_total_quantity(frm);
		render_all_row_image_pickers(frm, true);
	},

	produtos_remove(frm) {
		sync_legacy_fields_from_product_rows(frm);
		refresh_gravacoes_from_total_quantity(frm);
		render_all_row_image_pickers(frm, true);
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
		sync_primary_product_line(frm);
		sync_legacy_fields_from_product_rows(frm);
		refresh_gravacoes_from_total_quantity(frm);
	},
});

frappe.ui.form.on("Orcamento Produto Item", {
	item(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		const update_after_row_change = () => {
			update_row_total(row);
			sync_legacy_fields_from_product_rows(frm);
			refresh_gravacoes_from_total_quantity(frm);
			open_row_image_picker(frm, cdt, cdn, true);
		};

		if (!row.item) {
			frappe.model.set_value(cdt, cdn, "imagem_produto", "");
			const cache_by_row = frm.__row_item_images_cache || {};
			const prefix = `${cdn}:`;
			Object.keys(cache_by_row).forEach((key) => {
				if (key.startsWith(prefix)) {
					delete cache_by_row[key];
				}
			});
			frm.__row_item_images_cache = cache_by_row;
			update_after_row_change();
			return;
		}

		frappe.db
			.get_value("Item", row.item, "image")
			.then((response) => {
				const image =
					(response && response.message && response.message.image) ||
					(response && response.image) ||
					"";
				frappe.model.set_value(cdt, cdn, "imagem_produto", image);
			})
			.catch(() => {
				frappe.model.set_value(cdt, cdn, "imagem_produto", "");
			})
			.finally(() => {
				update_after_row_change();
			});
	},

	quantidade(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		update_row_total(row);
		sync_legacy_fields_from_product_rows(frm);
		refresh_gravacoes_from_total_quantity(frm);
		open_row_image_picker(frm, cdt, cdn, false);
	},

	valor_unitario(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		update_row_total(row);
		sync_legacy_fields_from_product_rows(frm);
		open_row_image_picker(frm, cdt, cdn, false);
	},

	imagem_produto(frm, cdt, cdn) {
		sync_legacy_fields_from_product_rows(frm);
		open_row_image_picker(frm, cdt, cdn, true);
		render_all_row_image_pickers(frm, false);
	},

	form_render(frm, cdt, cdn) {
		open_row_image_picker(frm, cdt, cdn, true);
		render_all_row_image_pickers(frm, false);
	},
});

frappe.ui.form.on("Gravacao Item", {
	catalogo_gravacao(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		const qty = normalize_numeric(frm.doc.quantidade);

		if (!row.catalogo_gravacao) {
			frappe.model.set_value(cdt, cdn, "descricao", "");
			frappe.model.set_value(cdt, cdn, "custo_unitario", 0);
			frappe.model.set_value(cdt, cdn, "total", 0);
			return;
		}

		if (qty <= 0) {
			frappe.model.set_value(cdt, cdn, "descricao", "Informe a quantidade");
			frappe.model.set_value(cdt, cdn, "custo_unitario", 0);
			frappe.model.set_value(cdt, cdn, "total", 0);
			return;
		}

		frappe.call({
			method:
				"calculadora_orcamento.calculadora_orcamento.doctype.catalogo_gravacao.catalogo_gravacao.get_custo_gravacao",
			args: { catalogo_name: row.catalogo_gravacao, qty: qty },
			callback: function (r) {
				if (r.message) {
					frappe.model.set_value(cdt, cdn, "custo_unitario", r.message.custo_unitario || 0);
					frappe.model.set_value(cdt, cdn, "total", r.message.custo || 0);
					frappe.model.set_value(cdt, cdn, "descricao", r.message.descricao);
				}
			},
		});
	},
});
