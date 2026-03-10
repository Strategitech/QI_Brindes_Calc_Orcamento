from types import SimpleNamespace
from unittest.mock import patch
import unittest

from calculadora_orcamento.calculadora_orcamento.doctype.calculadora_orcamento import calculadora_orcamento as orcamento_module
from calculadora_orcamento.calculadora_orcamento.doctype.calculadora_orcamento.calculadora_orcamento import (
	build_confirmacao_resumo,
	distribute_total_across_lines,
	get_orcamento_product_lines,
	get_primary_product_line,
)


class DummyDoc(dict[str, object]):
	def get(self, key: str, default: object = None):
		return super().get(key, default)


class TestCalculadoraOrcamento(unittest.TestCase):
	def test_prefers_product_lines_over_legacy_fields(self):
		doc = DummyDoc(
			{
				"produtos": [
					{
						"item": "ITEM-LINHA",
						"descricao": "Linha 1",
						"quantidade": 25,
						"valor_unitario": 12.5,
						"valor_total": 312.5,
					}
				],
				"item": "ITEM-LEGADO",
				"quantidade": 10,
				"valor_final_unitario": 9.0,
				"valor_final_total": 90.0,
			}
		)

		lines = get_orcamento_product_lines(doc)
		self.assertEqual(len(lines), 1)
		self.assertEqual(lines[0]["item"], "ITEM-LINHA")
		self.assertEqual(lines[0]["quantidade"], 25)

	def test_falls_back_to_legacy_fields_when_lines_are_missing(self):
		doc = DummyDoc(
			{
				"item": "ITEM-LEGADO",
				"descrição": "Produto legado",
				"quantidade": 80,
				"valor_final_unitario": 7.0,
				"valor_final_total": 560.0,
			}
		)

		lines = get_orcamento_product_lines(doc)
		self.assertEqual(len(lines), 1)
		self.assertEqual(lines[0]["descricao"], "Produto legado")
		self.assertEqual(lines[0]["valor_total"], 560.0)

	def test_primary_line_returns_none_without_any_product_data(self):
		doc = DummyDoc({})
		self.assertIsNone(get_primary_product_line(doc))

	def test_distributes_total_across_multiple_lines_with_weights(self):
		lines = [
			{"item": "A", "quantidade": 10, "base_total": 100.0, "valor_unitario": 0, "valor_total": 0},
			{"item": "B", "quantidade": 20, "base_total": 300.0, "valor_unitario": 0, "valor_total": 0},
		]

		distributed = distribute_total_across_lines(lines, 550.0)
		total = sum(line["valor_total"] for line in distributed)
		self.assertEqual(round(total, 2), 550.0)
		self.assertEqual(round(distributed[0]["valor_total"], 2), 137.5)
		self.assertEqual(round(distributed[1]["valor_total"], 2), 412.5)

	def test_build_confirmacao_resumo_for_multiple_products(self):
		doc = DummyDoc(
			{
				"produtos": [
					{"item": "ITEM-A", "quantidade": 10, "valor_total": 150.0},
					{"item": "ITEM-B", "quantidade": 5, "valor_total": 50.0},
				],
			}
		)

		def fake_get_value(doctype, name, field):
			if doctype == "Item" and field == "item_name":
				if name == "ITEM-A":
					return "Caneta"
				if name == "ITEM-B":
					return "Copo"
			return None

		fake_frappe = SimpleNamespace(db=SimpleNamespace(get_value=fake_get_value))

		with patch.object(orcamento_module, "frappe", fake_frappe):
			resumo = build_confirmacao_resumo(doc)

		self.assertEqual(resumo["item"], "Pedido com 2 itens")
		self.assertEqual(resumo["quantidade"], 15)
		self.assertEqual(round(float(resumo["valor_total"]), 2), 200.0)
		self.assertIn("Caneta", resumo["descricao"])
		self.assertIn("Copo", resumo["descricao"])

	def test_build_confirmacao_resumo_appends_gravacao_methods_to_explicit_description(self):
		doc = DummyDoc(
			{
				"produtos": [
					{
						"item": "ITEM-A",
						"descricao": "Caneta metalica",
						"quantidade": 10,
						"valor_total": 150.0,
					}
				],
				"gravacoes": [
					{"catalogo_gravacao": "GRAV-UV"},
					{"catalogo_gravacao": "GRAV-LASER"},
				],
			}
		)

		def fake_get_value(doctype, name, field):
			if doctype == "Item" and field == "item_name" and name == "ITEM-A":
				return "Caneta"
			if doctype == "Item" and field == "description" and name == "ITEM-A":
				return "Descricao do item"
			if doctype == "Catalogo Gravacao" and field == "metodo_gravacao":
				if name == "GRAV-UV":
					return "UV Digital"
				if name == "GRAV-LASER":
					return "Laser"
			return None

		fake_frappe = SimpleNamespace(db=SimpleNamespace(get_value=fake_get_value))

		with patch.object(orcamento_module, "frappe", fake_frappe):
			resumo = build_confirmacao_resumo(doc)

		self.assertEqual(resumo["item"], "Caneta")
		self.assertIn("Caneta metalica", resumo["descricao"])
		self.assertIn("personalizada a uv digital, laser", resumo["descricao"].lower())
