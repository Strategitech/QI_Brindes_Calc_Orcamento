// Copyright (c) 2026, Strategitech and contributors
// For license information, please see license.txt

frappe.ui.form.on("Importacao Produtos", {
	refresh(frm) {
		if (frm.doc.status === "Processando") {
			frm.add_custom_button(__("Atualizar Status"), function () {
				frm.reload_doc();
			});
		}

		frm.add_custom_button(__("Baixar Template"), function () {
			const header = "ref_produto_interno;nome;preco;descricao;marca;url_imagem";
			const example = "ABC-123;Caneta Azul;12.50;Caneta esferografica azul;BIC;https://exemplo.com/img.jpg";
			const csv = header + "\n" + example + "\n";
			const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8;" });
			const url = URL.createObjectURL(blob);
			const a = document.createElement("a");
			a.href = url;
			a.download = "template_importacao_produtos.csv";
			a.click();
			URL.revokeObjectURL(url);
		}, __("Ferramentas"));
	},
});
