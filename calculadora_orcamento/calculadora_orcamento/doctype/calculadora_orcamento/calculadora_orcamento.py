# Copyright (c) 2025, Strategitech and contributors
# For license information, please see license.txt

import json
import math

import frappe
from frappe.model.document import Document


def get_scale_price(item_code, qty):
    """Get price from scale_prices JSON if available, else fall back to Item Price."""
    scale_json = frappe.db.get_value("Item", item_code, "scale_prices")
    if scale_json:
        try:
            tiers = json.loads(scale_json)
            if isinstance(tiers, list) and tiers:
                # Sort by MinQt descending, pick first where qty >= MinQt
                tiers_sorted = sorted(tiers, key=lambda t: t.get("MinQt", 0), reverse=True)
                for tier in tiers_sorted:
                    if qty >= tier.get("MinQt", 0):
                        return tier.get("Price", 0.0)
        except (json.JSONDecodeError, TypeError, KeyError):
            pass

    # Fallback to flat Item Price
    filters = {"item_code": item_code, "selling": 1}
    rate = frappe.db.get_value("Item Price", filters, "price_list_rate")
    return rate if rate else 0.0


class CalculadoraOrcamento(Document):
    def validate(self):
        self.calculate_all()

    def calculate_all(self):
        # 1. Base Product Cost (scale prices with Item Price fallback)
        self.custo_base = 0.0
        if self.item:
            self.custo_base = get_scale_price(self.item, self.quantidade or 0)

        main_qty = self.quantidade or 0
        base_cost_total = (main_qty * (self.custo_base or 0.0))

        # 1b. Aliquota on Base Cost (VBA: dAliquotaCalculada)
        aliquota_on_base = 0.0
        if self.aplicar_aliquota:
            aliquota_on_base = base_cost_total * ((self.tax_rate or 0.0) / 100.0)
        self.aliquota_calculada = aliquota_on_base

        # 2. Fotolito Logic
        fotolito_cost = 0.0
        if self.fotolito_value and self.fotolito_value != "N/A":
            try:
                fotolito_cost = float(self.fotolito_value)
            except ValueError:
                fotolito_cost = 0.0

        # 3. Gravacoes (Child Table) — iterate over all engraving rows
        from calculadora_orcamento.calculadora_orcamento.doctype.catalogo_gravacao.catalogo_gravacao import calcular_custo_gravacao

        total_grav_cost = 0.0
        for row in self.gravacoes:
            if row.catalogo_gravacao:
                result = calcular_custo_gravacao(row.catalogo_gravacao, main_qty)
                row.total = result["custo"]
                row.descricao = result["descricao"]
            else:
                unit_cost = row.custo_unitario or 0.0
                if row.unidade == "Milheiro":
                    milheiros = math.ceil(main_qty / 1000.0)
                    row.total = milheiros * unit_cost
                else:
                    row.total = main_qty * unit_cost
                row.descricao = ""

            total_grav_cost += row.total

        self.total_gravacao = total_grav_cost

        # 5. Embalagens (Packaging) — read per-size costs from Embalagem Config
        embal_config = frappe.get_cached_doc("Embalagem Config")
        cost_standard_pack = (
            (self.qtd_p or 0) * (embal_config.custo_p or 0) +
            (self.qtd_m or 0) * (embal_config.custo_m or 0) +
            (self.qtd_g or 0) * (embal_config.custo_g or 0) +
            (self.qtd_xg or 0) * (embal_config.custo_xg or 0) +
            (self.qtd_xxg or 0) * (embal_config.custo_xxg or 0)
        )

        # Custom Packaging
        cost_custom_pack = 0.0
        if self.embal_custom:
            cost_custom_pack = (self.qtd_customizada or 0) * (self.valor_customizada or 0)

        total_embal_cost = cost_standard_pack + cost_custom_pack
        self.custo_total_embalagens = total_embal_cost

        # 6. Outras Despesas
        total_despesas = (self.mao_de_obra or 0) + \
                         (self.gasoline or 0) + \
                         (self.motoboy or 0) + \
                         (self.frete or 0) + \
                         (self.cliche or 0) + \
                         (self.extras or 0)
        self.total_despesas = total_despesas

        # 7. Tabela Comissao — auto-fill margin and commission from linked doc
        if self.tabela_comissao:
            tabela = frappe.get_cached_doc("Tabela Comissao", self.tabela_comissao)
            self.margin = tabela.margem_lucro
            if not self.custom_commission:
                comissao_percent = tabela.comissao
            else:
                comissao_percent = self.comis_custom or 0.0
        else:
            comissao_percent = 0.0

        # Commission overrides
        if self.comis_0:
            comissao_percent = 0.0
        elif not self.tabela_comissao:
            if self.custom_commission:
                comissao_percent = self.comis_custom or 0.0

        if "System Manager" in frappe.get_roles(frappe.session.user):
            pass
        else:
            # Sales Person Limit Logic
            sales_person_limit = 0.0
            employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
            if employee:
                sales_person = frappe.db.get_value("Sales Person", {"employee": employee}, ["name", "custom_max_commission_percent"], as_dict=True)
                if sales_person:
                    sales_person_limit = sales_person.custom_max_commission_percent

            if sales_person_limit > 0 and comissao_percent > sales_person_limit:
                 frappe.throw(f"Limite de comissão excedido! Seu limite é {sales_person_limit}%.")

        # 8. Total Hard Cost (includes aliquota on base)
        total_hard_cost = base_cost_total + aliquota_on_base + fotolito_cost + total_grav_cost + total_embal_cost + total_despesas

        # 9. Target Revenue (Cost + Margin)
        margin_rate = (self.margin or 0.0) / 100.0
        target_revenue = total_hard_cost * (1.0 + margin_rate)

        # 10. Gross Up (Add BV + Commission + Tax on top of Sale Price)
        bv_rate = (self.porcentagem or 0.0) / 100.0
        com_rate = comissao_percent / 100.0
        tax_rate = (self.tax_rate or 0.0) / 100.0

        total_fees_rate = bv_rate + com_rate + tax_rate

        valor_final_total = 0.0
        if total_fees_rate < 1.0:
            valor_final_total = target_revenue / (1.0 - total_fees_rate)
        else:
            frappe.throw("A soma de BV, Comissão e Imposto não pode ser 100% ou mais (Divisão por zero).")

        # 11. Calculate Derived Values
        valor_bv = valor_final_total * bv_rate
        valor_comissao = valor_final_total * com_rate
        valor_imposto = valor_final_total * tax_rate
        valor_unitario = 0.0
        if main_qty > 0:
            valor_unitario = valor_final_total / main_qty

        # 12. Save to Fields
        self.total_bv = valor_bv
        self.comissao_receber = valor_comissao
        self.total_tax = valor_imposto
        self.valor_final_total = valor_final_total
        self.valor_final_unitario = valor_unitario


@frappe.whitelist()
def make_delivery_note(source_name):
    doc = frappe.get_doc("Calculadora Orcamento", source_name)

    company = frappe.defaults.get_defaults().get("company")
    warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")

    dn = frappe.new_doc("Delivery Note")
    dn.customer = doc.nome
    dn.company = company
    dn.orcamento = doc.name
    dn.append("items", {
        "item_code": doc.item,
        "qty": doc.quantidade,
        "rate": doc.valor_final_unitario,
        "warehouse": warehouse,
    })
    dn.insert()

    return dn.name


@frappe.whitelist()
def make_confirmacao_pedido(source_name):
    doc = frappe.get_doc("Calculadora Orcamento", source_name)
    item_name = frappe.db.get_value("Item", doc.item, "item_name") if doc.item else None
    item_description = frappe.db.get_value("Item", doc.item, "description") if doc.item else None

    conf = frappe.new_doc("Confirmacao Pedido")
    conf.orcamento = doc.name
    conf.cliente = doc.nome
    conf.telefone = doc.telefone_whatsapp
    conf.item = item_name or (doc.get("descrição") or doc.get("descricao") or "Produto personalizado")
    conf.descricao = doc.get("descrição") or doc.get("descricao") or item_description or ""
    conf.quantidade = doc.quantidade
    conf.valor_unitario = doc.valor_final_unitario
    conf.valor_total = doc.valor_final_total

    # Auto-populate address from Customer
    from frappe.contacts.doctype.address.address import get_default_address
    address_name = get_default_address("Customer", doc.nome)
    if address_name:
        addr = frappe.get_doc("Address", address_name)
        conf.endereco_logradouro = addr.address_line1
        conf.endereco_complemento = addr.address_line2
        conf.endereco_bairro = addr.county
        conf.endereco_cidade = addr.city
        conf.endereco_estado = addr.state
        conf.endereco_cep = addr.pincode

    conf.insert()

    return conf.name
