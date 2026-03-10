// Copyright (c) 2026, Strategitech and contributors
// For license information, please see license.txt

function toNumber(value) {
	const parsed = Number(value || 0);
	return Number.isFinite(parsed) ? parsed : 0;
}

function getGravacaoMethods(orc) {
	const catalogNames = [...new Set((orc.gravacoes || []).map((row) => row.catalogo_gravacao).filter(Boolean))];
	if (catalogNames.length === 0) {
		return Promise.resolve([]);
	}

	return Promise.all(
		catalogNames.map((catalogName) =>
			frappe.db
				.get_value("Catalogo Gravacao", catalogName, "metodo_gravacao")
				.then((result) => (result && result.message && result.message.metodo_gravacao) || "")
				.catch(() => "")
		)
	).then((methods) => [...new Set(methods.filter(Boolean))]);
}

function appendGravacaoMethods(description, gravacaoMethods) {
	const base = String(description || "").trim();
	if (!gravacaoMethods || gravacaoMethods.length === 0) {
		return base;
	}

	const suffix = `personalizada a ${gravacaoMethods.join(", ").toLowerCase()}`;
	if (base.toLowerCase().includes(suffix)) {
		return base;
	}
	if (base) {
		return `${base}, ${suffix}`;
	}
	return suffix.charAt(0).toUpperCase() + suffix.slice(1);
}

function getOrcamentoLines(orc) {
	const lines = (orc.produtos || [])
		.map((row) => ({
			item: row.item || "",
			descricao: row.descricao || "",
			quantidade: toNumber(row.quantidade),
			valor_unitario: toNumber(row.valor_unitario),
			valor_total: toNumber(row.valor_total),
		}))
		.filter(
			(row) => row.item || row.descricao || row.quantidade > 0 || row.valor_unitario > 0 || row.valor_total > 0
		);

	if (lines.length > 0) {
		return lines;
	}

	return [
		{
			item: orc.item || "",
			descricao: orc.descrição || orc.descricao || "",
			quantidade: toNumber(orc.quantidade),
			valor_unitario: toNumber(orc.valor_final_unitario),
			valor_total: toNumber(orc.valor_final_total),
		},
	];
}

function buildResumo(orc, itemNamesByCode, gravacaoMethods) {
	const lines = getOrcamentoLines(orc);
	const totalQuantidade = lines.reduce((sum, row) => sum + toNumber(row.quantidade), 0);
	let totalValor = lines.reduce((sum, row) => sum + toNumber(row.valor_total), 0);
	if (totalValor <= 0) {
		totalValor = toNumber(orc.valor_final_total);
	}

	if (lines.length === 1) {
		const line = lines[0];
		const itemNome = itemNamesByCode[line.item] || "";
		const item = itemNome || line.descricao || "Produto personalizado";
		const quantidade = toNumber(line.quantidade) || toNumber(orc.quantidade);
		const valorTotal = toNumber(line.valor_total) || totalValor;
		const valorUnitario =
			toNumber(line.valor_unitario) || (quantidade > 0 ? valorTotal / quantidade : toNumber(orc.valor_final_unitario));

		return {
			item,
			descricao: appendGravacaoMethods(
				line.descricao || orc.descrição || orc.descricao || "",
				gravacaoMethods
			),
			quantidade,
			valorUnitario,
			valorTotal,
		};
	}

	const descricao = lines
		.map((line) => {
			const itemNome = appendGravacaoMethods(
				itemNamesByCode[line.item] || line.descricao || "Produto",
				gravacaoMethods
			);
			return `${itemNome} (Qtd: ${toNumber(line.quantidade)})`;
		})
		.join("\n");

	const quantidade = totalQuantidade || toNumber(orc.quantidade);
	const valorUnitario = quantidade > 0 ? totalValor / quantidade : 0;

	return {
		item: `Pedido com ${lines.length} itens`,
		descricao,
		quantidade,
		valorUnitario,
		valorTotal: totalValor,
	};
}

function populateCustomerAddress(frm, customerName) {
	if (!customerName) {
		return;
	}

	frappe.call({
		method: "frappe.contacts.doctype.address.address.get_default_address",
		args: { doctype: "Customer", name: customerName },
		callback: (response) => {
			if (!response.message) {
				return;
			}

			frappe.db.get_doc("Address", response.message).then((addr) => {
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
		},
	});
}

frappe.ui.form.on("Confirmacao Pedido", {
	orcamento(frm) {
		if (!frm.doc.orcamento) {
			return;
		}

		frappe.db.get_doc("Calculadora Orcamento", frm.doc.orcamento).then((orc) => {
			frm.set_value("cliente", orc.nome);
			frm.set_value("telefone", orc.telefone_whatsapp);

			const lines = getOrcamentoLines(orc);
			const itemCodes = [...new Set(lines.map((line) => line.item).filter(Boolean))];
			const itemFetches = itemCodes.map((itemCode) =>
				frappe.db
					.get_value("Item", itemCode, "item_name")
					.then((result) => ({ itemCode, itemName: (result && result.message && result.message.item_name) || "" }))
					.catch(() => ({ itemCode, itemName: "" }))
			);

			Promise.all([Promise.all(itemFetches), getGravacaoMethods(orc)]).then(([results, gravacaoMethods]) => {
				const itemNamesByCode = {};
				results.forEach((entry) => {
					itemNamesByCode[entry.itemCode] = entry.itemName;
				});

				const resumo = buildResumo(orc, itemNamesByCode, gravacaoMethods);
				frm.set_value("item", resumo.item);
				frm.set_value("descricao", resumo.descricao);
				frm.set_value("quantidade", resumo.quantidade);
				frm.set_value("valor_unitario", resumo.valorUnitario);
				frm.set_value("valor_total", resumo.valorTotal);
			});

			populateCustomerAddress(frm, orc.nome);
		});
	},
});
