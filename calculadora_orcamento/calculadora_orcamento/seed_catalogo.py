# Copyright (c) 2026, Strategitech and contributors
# Seed script for OmniTek engraving price catalog.
# Run: bench --site SITE execute calculadora_orcamento.calculadora_orcamento.seed_catalogo.seed

import frappe


CATALOGO_DATA = [
	# ──────────────────────────────────────────────────────────
	# GRAVAÇÃO A LASER
	# ──────────────────────────────────────────────────────────
	{
		"metodo_gravacao": "Gravacao a Laser",
		"categoria_produto": "Canetas e Lapiseiras",
		"notas": "Colorido: R$0,55/und (101-1000 pecas)",
		"faixas": [
			{"qty_min": 0, "qty_max": 100, "tipo": "Minimo", "preco": 80.00},
			{"qty_min": 101, "qty_max": 1000, "tipo": "Unitario", "preco": 0.60},
			{"qty_min": 1001, "qty_max": 0, "tipo": "Unitario", "preco": 0.50},
		],
	},
	{
		"metodo_gravacao": "Gravacao a Laser",
		"categoria_produto": "Canetas Luxo",
		"faixas": [
			{"qty_min": 0, "qty_max": 0, "tipo": "Unitario", "preco": 15.00},
		],
	},
	{
		"metodo_gravacao": "Gravacao a Laser",
		"categoria_produto": "Mochila e Necessaire",
		"faixas": [
			{"qty_min": 0, "qty_max": 50, "tipo": "Minimo", "preco": 100.00},
			{"qty_min": 51, "qty_max": 100, "tipo": "Minimo", "preco": 200.00},
			{"qty_min": 101, "qty_max": 0, "tipo": "Unitario", "preco": 1.85},
		],
	},
	{
		"metodo_gravacao": "Gravacao a Laser",
		"categoria_produto": "Chaveiro, Porta Cartao, Lanterna, Plaquinha, Talheres, Pendrive",
		"faixas": [
			{"qty_min": 0, "qty_max": 100, "tipo": "Minimo", "preco": 100.00},
			{"qty_min": 101, "qty_max": 1000, "tipo": "Unitario", "preco": 0.90},
			{"qty_min": 1001, "qty_max": 0, "tipo": "Unitario", "preco": 0.75},
		],
	},
	{
		"metodo_gravacao": "Gravacao a Laser",
		"categoria_produto": "Chaveiro Abridor",
		"faixas": [
			{"qty_min": 0, "qty_max": 100, "tipo": "Minimo", "preco": 70.00},
			{"qty_min": 101, "qty_max": 1000, "tipo": "Unitario", "preco": 0.45},
			{"qty_min": 1001, "qty_max": 0, "tipo": "Unitario", "preco": 0.35},
		],
	},
	{
		"metodo_gravacao": "Gravacao a Laser UV",
		"categoria_produto": "Vidro, Copo, Caneca, Taca",
		"notas": "Gravacao 360 ate 4,5cm: R$2,50/und",
		"faixas": [
			{"qty_min": 0, "qty_max": 50, "tipo": "Minimo", "preco": 110.00},
			{"qty_min": 51, "qty_max": 0, "tipo": "Unitario", "preco": 2.20},
		],
	},
	{
		"metodo_gravacao": "Gravacao a Laser",
		"categoria_produto": "Copo Stanley, Garrafa Termica, Cantil, Caneca Termica",
		"faixas": [
			{"qty_min": 0, "qty_max": 100, "tipo": "Minimo", "preco": 180.00},
			{"qty_min": 101, "qty_max": 0, "tipo": "Unitario", "preco": 1.50},
		],
	},
	{
		"metodo_gravacao": "Gravacao a Laser",
		"categoria_produto": "Squeeze, Garrafa, Caneca P",
		"faixas": [
			{"qty_min": 0, "qty_max": 100, "tipo": "Minimo", "preco": 120.00},
			{"qty_min": 101, "qty_max": 0, "tipo": "Unitario", "preco": 1.00},
		],
	},
	# ──────────────────────────────────────────────────────────
	# GRAVAÇÃO ROTACIONADA
	# ──────────────────────────────────────────────────────────
	{
		"metodo_gravacao": "Gravacao Rotacionada",
		"categoria_produto": "Garrafa, Squeeze, Caneca",
		"notas": "Acima de 35 pecas: consultar. Amostra fisica a partir de R$70,00",
		"faixas": [
			{"qty_min": 0, "qty_max": 35, "tipo": "Minimo", "preco": 120.00},
			{"qty_min": 36, "qty_max": 0, "tipo": "Unitario", "preco": 3.50},
		],
	},
	# ──────────────────────────────────────────────────────────
	# GRAVAÇÃO A LASER CO2
	# ──────────────────────────────────────────────────────────
	{
		"metodo_gravacao": "Gravacao a Laser CO2",
		"categoria_produto": "Madeira, Couro, Silicone, Placa",
		"notas": "80x80mm. Tamanho maior favor consultar valor",
		"faixas": [
			{"qty_min": 0, "qty_max": 100, "tipo": "Minimo", "preco": 140.00},
			{"qty_min": 101, "qty_max": 1000, "tipo": "Unitario", "preco": 1.20},
			{"qty_min": 1001, "qty_max": 0, "tipo": "Unitario", "preco": 1.10},
		],
	},
	{
		"metodo_gravacao": "Gravacao a Laser CO2",
		"categoria_produto": "Caneta, Lapis, Chaveiro, Abridor",
		"faixas": [
			{"qty_min": 0, "qty_max": 100, "tipo": "Minimo", "preco": 100.00},
			{"qty_min": 101, "qty_max": 1000, "tipo": "Unitario", "preco": 0.90},
			{"qty_min": 1001, "qty_max": 0, "tipo": "Unitario", "preco": 0.80},
		],
	},
	# ──────────────────────────────────────────────────────────
	# TAMPOGRAFIA
	# ──────────────────────────────────────────────────────────
	{
		"metodo_gravacao": "Tampografia",
		"categoria_produto": "Caneta Plastica, Lapis, Lapiseira",
		"notas": "1 cor/batida, emb. 50 pecas. Promotor +R$40/milheiro. Embalagem individual +R$55/milheiro",
		"faixas": [
			{"qty_min": 0, "qty_max": 1000, "tipo": "Milheiro", "preco": 130.00},
			{"qty_min": 1001, "qty_max": 10000, "tipo": "Milheiro", "preco": 120.00},
			{"qty_min": 10001, "qty_max": 0, "tipo": "Milheiro", "preco": 115.00},
		],
	},
	{
		"metodo_gravacao": "Tampografia",
		"categoria_produto": "Bloco P, Trena, Espelho, Mouse, Pop Socket, Power Bank, Chaveiro, Kit Manicure",
		"notas": "1 cor/batida",
		"faixas": [
			{"qty_min": 0, "qty_max": 100, "tipo": "Minimo", "preco": 185.00},
			{"qty_min": 101, "qty_max": 300, "tipo": "Minimo", "preco": 300.00},
			{"qty_min": 301, "qty_max": 700, "tipo": "Minimo", "preco": 370.00},
			{"qty_min": 701, "qty_max": 0, "tipo": "Unitario", "preco": 0.75},
		],
	},
	# ──────────────────────────────────────────────────────────
	# SILK
	# ──────────────────────────────────────────────────────────
	{
		"metodo_gravacao": "Silk",
		"categoria_produto": "Lixo Car, Agenda, Moleskine P, Kit Queijo, Kit Vinho, Estojo, Risque Rabisque",
		"notas": "1 cor/batida. Para Kits favor consultar valor de manuseio",
		"faixas": [
			{"qty_min": 0, "qty_max": 100, "tipo": "Minimo", "preco": 200.00},
			{"qty_min": 101, "qty_max": 300, "tipo": "Minimo", "preco": 264.00},
			{"qty_min": 301, "qty_max": 500, "tipo": "Minimo", "preco": 350.00},
			{"qty_min": 501, "qty_max": 700, "tipo": "Minimo", "preco": 400.00},
			{"qty_min": 701, "qty_max": 0, "tipo": "Unitario", "preco": 0.70},
		],
	},
	{
		"metodo_gravacao": "Silk 180",
		"categoria_produto": "Garrafa, Copo, Squeeze, Caneca, Copo Longdrink, Taca",
		"notas": "1 cor/batida. Acima de 2 cores consultar valor",
		"faixas": [
			{"qty_min": 0, "qty_max": 100, "tipo": "Minimo", "preco": 200.00},
			{"qty_min": 101, "qty_max": 300, "tipo": "Minimo", "preco": 320.00},
			{"qty_min": 301, "qty_max": 500, "tipo": "Minimo", "preco": 380.00},
			{"qty_min": 501, "qty_max": 0, "tipo": "Unitario", "preco": 0.90},
		],
	},
	{
		"metodo_gravacao": "Silk 360",
		"categoria_produto": "Garrafa, Copo, Squeeze, Caneca, Copo Longdrink, Taca",
		"notas": "1 cor/batida. Acima de 2 cores consultar valor",
		"faixas": [
			{"qty_min": 0, "qty_max": 100, "tipo": "Minimo", "preco": 360.00},
			{"qty_min": 101, "qty_max": 300, "tipo": "Minimo", "preco": 506.00},
			{"qty_min": 301, "qty_max": 500, "tipo": "Minimo", "preco": 638.00},
			{"qty_min": 501, "qty_max": 0, "tipo": "Unitario", "preco": 1.21},
		],
	},
	{
		"metodo_gravacao": "Silk em Vidro",
		"categoria_produto": "Garrafa, Copo, Caneca",
		"notas": "1 cor/batida",
		"faixas": [
			{"qty_min": 0, "qty_max": 100, "tipo": "Minimo", "preco": 308.00},
			{"qty_min": 101, "qty_max": 0, "tipo": "Unitario", "preco": 3.10},
		],
	},
	{
		"metodo_gravacao": "Silk em Tecido",
		"categoria_produto": "Capa de Garrafa, Almofada de Pescoco, Mouse Pad",
		"notas": "1 cor/batida. Logo ate 100mm/largura",
		"faixas": [
			{"qty_min": 0, "qty_max": 150, "tipo": "Minimo", "preco": 240.00},
			{"qty_min": 151, "qty_max": 0, "tipo": "Unitario", "preco": 1.45},
		],
	},
	{
		"metodo_gravacao": "Silk",
		"categoria_produto": "Pasta Zipzap, Squeeze Dobravel, Necessaire",
		"notas": "1 cor/batida",
		"faixas": [
			{"qty_min": 0, "qty_max": 150, "tipo": "Minimo", "preco": 230.00},
			{"qty_min": 151, "qty_max": 0, "tipo": "Unitario", "preco": 1.45},
		],
	},
	{
		"metodo_gravacao": "Silk em Tecido",
		"categoria_produto": "Sacola, Sacochila, Ecobag, Pasta",
		"notas": "1 cor/batida. Logo ate 120mm/largura",
		"faixas": [
			{"qty_min": 0, "qty_max": 100, "tipo": "Minimo", "preco": 187.00},
			{"qty_min": 101, "qty_max": 0, "tipo": "Unitario", "preco": 1.65},
		],
	},
	{
		"metodo_gravacao": "Silk",
		"categoria_produto": "Bolsa Termica, Guarda Chuva",
		"notas": "1 cor/batida/por gravacao",
		"faixas": [
			{"qty_min": 0, "qty_max": 100, "tipo": "Minimo", "preco": 220.00},
			{"qty_min": 101, "qty_max": 0, "tipo": "Unitario", "preco": 2.10},
		],
	},
	{
		"metodo_gravacao": "Silk",
		"categoria_produto": "Mochila, Mala de Viagem, Sacola Metalizada",
		"notas": "1 cor/batida",
		"faixas": [
			{"qty_min": 0, "qty_max": 100, "tipo": "Minimo", "preco": 260.00},
			{"qty_min": 101, "qty_max": 0, "tipo": "Unitario", "preco": 2.40},
		],
	},
	# ──────────────────────────────────────────────────────────
	# SUBLIMAÇÃO
	# ──────────────────────────────────────────────────────────
	{
		"metodo_gravacao": "Sublimacao",
		"categoria_produto": "Caneca, Squeeze",
		"notas": "Squeeze: R$5,50/und. Frente/Verso 360: Caneca R$4,95, Squeeze R$6,60. Dados variaveis +R$1,10/und",
		"faixas": [
			{"qty_min": 0, "qty_max": 28, "tipo": "Minimo", "preco": 110.00},
			{"qty_min": 29, "qty_max": 0, "tipo": "Unitario", "preco": 3.85},
		],
	},
	# ──────────────────────────────────────────────────────────
	# TRANSFER
	# ──────────────────────────────────────────────────────────
	{
		"metodo_gravacao": "Transfer",
		"categoria_produto": "Copos, Long Drink, Squeeze, Caneca (Pequena ate 30mm)",
		"notas": "Gravacao pequena ate 30mm. Dados variaveis +R$1,10/und",
		"faixas": [
			{"qty_min": 0, "qty_max": 26, "tipo": "Minimo", "preco": 100.00},
			{"qty_min": 27, "qty_max": 0, "tipo": "Unitario", "preco": 3.85},
		],
	},
	{
		"metodo_gravacao": "Transfer",
		"categoria_produto": "Copos, Long Drink, Squeeze, Caneca (Media ate 80mm)",
		"notas": "Gravacao media ate 80mm. Dados variaveis +R$1,10/und",
		"faixas": [
			{"qty_min": 0, "qty_max": 20, "tipo": "Minimo", "preco": 100.00},
			{"qty_min": 21, "qty_max": 0, "tipo": "Unitario", "preco": 4.95},
		],
	},
	{
		"metodo_gravacao": "Transfer",
		"categoria_produto": "Copos, Long Drink, Squeeze, Caneca (Acima 80mm)",
		"notas": "Gravacao acima de 80mm. Dados variaveis +R$1,10/und",
		"faixas": [
			{"qty_min": 0, "qty_max": 16, "tipo": "Minimo", "preco": 100.00},
			{"qty_min": 17, "qty_max": 0, "tipo": "Unitario", "preco": 6.00},
		],
	},
	# ──────────────────────────────────────────────────────────
	# DIGITAL UV
	# ──────────────────────────────────────────────────────────
	{
		"metodo_gravacao": "Digital UV",
		"categoria_produto": "Caneta Plastica, Lapis, Lapiseira",
		"notas": "Acima de 5001 pecas: consultar. Nome a Nome: min R$55 / a partir de 30 pecas R$1,65/und",
		"faixas": [
			{"qty_min": 0, "qty_max": 399, "tipo": "Minimo", "preco": 110.00},
			{"qty_min": 400, "qty_max": 2010, "tipo": "Unitario", "preco": 0.28},
			{"qty_min": 2011, "qty_max": 5000, "tipo": "Unitario", "preco": 0.25},
		],
	},
	{
		"metodo_gravacao": "Digital UV",
		"categoria_produto": "Caneta Metal e/ou Gravacao no Clip",
		"notas": "Acima de 5001 pecas: consultar. Nome a Nome: min R$55 / a partir de 30 pecas R$1,65/und",
		"faixas": [
			{"qty_min": 0, "qty_max": 399, "tipo": "Minimo", "preco": 220.00},
			{"qty_min": 400, "qty_max": 2010, "tipo": "Unitario", "preco": 0.55},
			{"qty_min": 2011, "qty_max": 5000, "tipo": "Unitario", "preco": 0.52},
		],
	},
	{
		"metodo_gravacao": "Digital UV",
		"categoria_produto": "Pop Socket, Trena, Pendrive, Spray",
		"notas": "Acima de 10001 pecas: consultar. Nome a Nome: min R$55 / a partir de 30 pecas R$1,65/und",
		"faixas": [
			{"qty_min": 0, "qty_max": 249, "tipo": "Minimo", "preco": 143.00},
			{"qty_min": 250, "qty_max": 510, "tipo": "Unitario", "preco": 0.60},
			{"qty_min": 511, "qty_max": 5010, "tipo": "Unitario", "preco": 0.53},
			{"qty_min": 5011, "qty_max": 10000, "tipo": "Unitario", "preco": 0.44},
		],
	},
	{
		"metodo_gravacao": "Digital UV",
		"categoria_produto": "Porta Cartao, Carregador, Regua 20cm, Chaveiro, Fone de Ouvido",
		"notas": "Acima de 5011 pecas: consultar. Nome a Nome: min R$55 / a partir de 30 pecas R$1,65/und",
		"faixas": [
			{"qty_min": 0, "qty_max": 149, "tipo": "Minimo", "preco": 148.50},
			{"qty_min": 150, "qty_max": 1010, "tipo": "Unitario", "preco": 1.00},
			{"qty_min": 1011, "qty_max": 5010, "tipo": "Unitario", "preco": 0.90},
		],
	},
	{
		"metodo_gravacao": "Digital UV",
		"categoria_produto": "Bloco P (Logo 7x7cm), Caixa de Som P, Carregador G, Regua 30cm, Estojo Caneta",
		"notas": "Acima de 2011 pecas: consultar. Nome a Nome: min R$55 / a partir de 30 pecas R$2,20/und",
		"faixas": [
			{"qty_min": 0, "qty_max": 49, "tipo": "Minimo", "preco": 143.00},
			{"qty_min": 50, "qty_max": 1010, "tipo": "Unitario", "preco": 2.85},
			{"qty_min": 1011, "qty_max": 2010, "tipo": "Unitario", "preco": 2.65},
		],
	},
	{
		"metodo_gravacao": "Digital UV",
		"categoria_produto": "Kit Vinho, Porta Documento (Logo 10x10cm), Caderno P, Agenda, Bloco G",
		"notas": "Acima de 1006 pecas: consultar. Nome a Nome: min R$55 / a partir de 30 pecas R$2,75/und",
		"faixas": [
			{"qty_min": 0, "qty_max": 49, "tipo": "Minimo", "preco": 165.00},
			{"qty_min": 50, "qty_max": 1005, "tipo": "Unitario", "preco": 3.20},
		],
	},
	{
		"metodo_gravacao": "Digital UV",
		"categoria_produto": "Bloco G, Caderno G (Logo 10x10cm), Estojo",
		"notas": "Blocos com espiral, irregular, kraft: consultar manuseio. Acima de 501 pecas: consultar. Nome a Nome: min R$55 / a partir de 30 pecas R$2,75/und",
		"faixas": [
			{"qty_min": 0, "qty_max": 20, "tipo": "Minimo", "preco": 165.00},
			{"qty_min": 21, "qty_max": 500, "tipo": "Unitario", "preco": 7.70},
		],
	},
	{
		"metodo_gravacao": "Digital UV",
		"categoria_produto": "Garrafa, Squeeze, Copo",
		"notas": "Maximo 3,5cm na horizontal. Acima de 501 pecas: consultar. Nome a Nome: min R$55 / a partir de 30 pecas R$2,75/und",
		"faixas": [
			{"qty_min": 0, "qty_max": 35, "tipo": "Minimo", "preco": 165.00},
			{"qty_min": 36, "qty_max": 500, "tipo": "Unitario", "preco": 4.40},
		],
	},
	{
		"metodo_gravacao": "Digital UV",
		"categoria_produto": "Caixa de Som com Ventosa",
		"notas": "Nome a Nome: min R$77 / a partir de 30 pecas R$3,85/und",
		"faixas": [
			{"qty_min": 0, "qty_max": 50, "tipo": "Minimo", "preco": 160.00},
			{"qty_min": 51, "qty_max": 500, "tipo": "Unitario", "preco": 1.50},
			{"qty_min": 501, "qty_max": 1000, "tipo": "Unitario", "preco": 1.45},
			{"qty_min": 1001, "qty_max": 0, "tipo": "Unitario", "preco": 1.40},
		],
	},
	{
		"metodo_gravacao": "Digital UV",
		"categoria_produto": "Caixa de Som Grande",
		"notas": "Nome a Nome: min R$77 / a partir de 30 pecas R$3,85/und",
		"faixas": [
			{"qty_min": 0, "qty_max": 50, "tipo": "Minimo", "preco": 165.00},
			{"qty_min": 51, "qty_max": 500, "tipo": "Unitario", "preco": 4.00},
			{"qty_min": 501, "qty_max": 1000, "tipo": "Unitario", "preco": 3.85},
			{"qty_min": 1001, "qty_max": 0, "tipo": "Unitario", "preco": 3.50},
		],
	},
	{
		"metodo_gravacao": "Digital UV",
		"categoria_produto": "Bloco P, Bloco M",
		"notas": "Blocos com espiral, irregular, kraft: consultar manuseio. Acima de 501 pecas: consultar. Nome a Nome: min R$77 / a partir de 30 pecas R$3,85/und",
		"faixas": [
			{"qty_min": 0, "qty_max": 20, "tipo": "Minimo", "preco": 154.00},
			{"qty_min": 21, "qty_max": 500, "tipo": "Unitario", "preco": 7.15},
		],
	},
	{
		"metodo_gravacao": "Digital UV",
		"categoria_produto": "Moleskine, Bloco, Caderno P Capa Inteira",
		"notas": "Blocos com espiral, irregular, kraft: consultar manuseio. Nome a Nome: min R$77 / a partir de 30 pecas R$3,85/und",
		"faixas": [
			{"qty_min": 0, "qty_max": 50, "tipo": "Minimo", "preco": 275.00},
			{"qty_min": 51, "qty_max": 0, "tipo": "Unitario", "preco": 6.05},
		],
	},
	# ──────────────────────────────────────────────────────────
	# BAIXO RELEVO
	# ──────────────────────────────────────────────────────────
	{
		"metodo_gravacao": "Baixo Relevo",
		"categoria_produto": "Geral",
		"notas": "Gravacao maxima 90x70mm. Cliche Baixo Relevo: R$215,00 (custo adicional unico)",
		"faixas": [
			{"qty_min": 0, "qty_max": 100, "tipo": "Minimo", "preco": 121.00},
			{"qty_min": 101, "qty_max": 0, "tipo": "Unitario", "preco": 1.10},
		],
	},
]


def seed():
	"""Seed the Catalogo Gravacao DocType with OmniTek price catalog data."""
	count_created = 0
	count_skipped = 0

	for entry in CATALOGO_DATA:
		title = f"{entry['metodo_gravacao']} - {entry['categoria_produto']}"

		if frappe.db.exists("Catalogo Gravacao", title):
			count_skipped += 1
			continue

		doc = frappe.new_doc("Catalogo Gravacao")
		doc.metodo_gravacao = entry["metodo_gravacao"]
		doc.categoria_produto = entry["categoria_produto"]
		doc.notas = entry.get("notas", "")

		for faixa in entry["faixas"]:
			doc.append("faixas", {
				"qty_min": faixa["qty_min"],
				"qty_max": faixa.get("qty_max", 0),
				"tipo": faixa["tipo"],
				"preco": faixa["preco"],
			})

		doc.insert(ignore_permissions=True)
		count_created += 1

	frappe.db.commit()
	print(f"Seed complete: {count_created} created, {count_skipped} skipped (already exist)")


TABELA_DATA = [
	{"label": "%1",  "margem_lucro": 29, "comissao": 1},
	{"label": "%2",  "margem_lucro": 32, "comissao": 2},
	{"label": "%3",  "margem_lucro": 33, "comissao": 3},
	{"label": "%4",  "margem_lucro": 34, "comissao": 4},
	{"label": "%5",  "margem_lucro": 35, "comissao": 5},
	{"label": "%6",  "margem_lucro": 36, "comissao": 6},
	{"label": "%7",  "margem_lucro": 37, "comissao": 7},
	{"label": "%8",  "margem_lucro": 38, "comissao": 8},
	{"label": "%9",  "margem_lucro": 39, "comissao": 9},
	{"label": "%10", "margem_lucro": 40, "comissao": 10},
]


def seed_tabelas():
	"""Seed the Tabela Comissao DocType with VBA commission/margin tables."""
	count_created = 0
	count_skipped = 0

	for entry in TABELA_DATA:
		if frappe.db.exists("Tabela Comissao", entry["label"]):
			count_skipped += 1
			continue

		doc = frappe.new_doc("Tabela Comissao")
		doc.label = entry["label"]
		doc.margem_lucro = entry["margem_lucro"]
		doc.comissao = entry["comissao"]
		doc.insert(ignore_permissions=True)
		count_created += 1

	frappe.db.commit()
	print(f"Tabelas seed complete: {count_created} created, {count_skipped} skipped (already exist)")


def seed_embalagem():
	"""Ensure Embalagem Config Single exists with default values."""
	doc = frappe.get_doc("Embalagem Config")
	if not doc.custo_p:
		doc.custo_p = 4
	if not doc.custo_m:
		doc.custo_m = 6
	if not doc.custo_g:
		doc.custo_g = 8
	if not doc.custo_xg:
		doc.custo_xg = 10
	if not doc.custo_xxg:
		doc.custo_xxg = 12
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	print("Embalagem Config seeded with default values")
