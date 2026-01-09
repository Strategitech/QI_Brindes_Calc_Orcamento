# Copyright (c) 2025, Strategitech and contributors
# For license information, please see license.txt

import math

import frappe
from frappe.model.document import Document


class CalculadoraOrcamento(Document):
    def validate(self):
        self.calculate_all()

    def calculate_all(self):
        # 1. Base Product Cost
        self.custo_base = 0.0
        if self.item:
            # Fetch from 'Item Price' DocType where Item Code matches
            # You might need to specify the price list (e.g., 'Standard Selling' or 'Standard Buying')
            # I will assume 'Standard Selling' as a default, or just grab the first one found.

            filters = {"item_code": self.item, "selling": 1} # Get any selling price

            # If you have a specific list, use: filters = {"item_code": self.item, "price_list": "Standard Selling"}

            rate = frappe.db.get_value("Item Price", filters, "price_list_rate")
            self.custo_base = rate if rate else 0.0


        main_qty = self.quantidade or 0
        base_cost_total = (main_qty * (self.custo_base or 0.0))

        # 2. Fotolito Logic
        # Field is Select: "N/A", "20", "30". Need to parse string to float.
        fotolito_cost = 0.0
        if self.fotolito_value and self.fotolito_value != "N/A":
            try:
                fotolito_cost = float(self.fotolito_value)
            except ValueError:
                fotolito_cost = 0.0

        # 3. Gravacao 1 Logic
        # Logic: If Milheiro -> ceil(qty/1000) * cost. If Unitario -> qty * cost.
        cost_grav_1 = 0.0
        unit_cost_1 = self.unit_cost_grav_1 or 0.0

        if self.unit_qtd_grav_1 == "Milheiro":
            milheiros = math.ceil(main_qty / 1000.0)
            cost_grav_1 = milheiros * unit_cost_1
        else: # "Unitário" or None
            cost_grav_1 = main_qty * unit_cost_1

        self.total_grav_1 = cost_grav_1

        # 4. Gravacao 2 Logic (Same logic)
        cost_grav_2 = 0.0
        unit_cost_2 = self.unit_cost_grav_2 or 0.0

        if self.unit_qtd_grav_2 == "Milheiro":
            milheiros = math.ceil(main_qty / 1000.0)
            cost_grav_2 = milheiros * unit_cost_2
        else:
            cost_grav_2 = main_qty * unit_cost_2

        self.total_grav_2 = cost_grav_2

        total_grav_cost = cost_grav_1 + cost_grav_2

        # 5. Embalagens (Packaging)
        # Assuming P/M/G/XG/XXG have a fixed cost per unit?
        # Your JSON doesn't have a "Cost per Packaging Unit" field.
        # I will assume R$ 0.00 for now unless you hardcode it or add a field.
        # Let's say cost is 0 since it's not in the JSON.
        pack_qty_standard = (self.qtd_p or 0) + (self.qtd_m or 0) + (self.qtd_g or 0) + (self.qtd_xg or 0) + (self.qtd_xxg or 0)
        cost_standard_pack = pack_qty_standard * 0.0 # TODO: Add a field for this cost or hardcode it

        # Custom Packaging
        cost_custom_pack = 0.0
        if self.embal_custom: # Checkbox is checked
            cost_custom_pack = (self.qtd_customizada or 0) * (self.valor_customizada or 0)

        total_embal_cost = cost_standard_pack + cost_custom_pack
        self.custo_total_embalagens = total_embal_cost

        # 6. Outras Despesas
        total_despesas = (self.mao_de_obra or 0) + \
                         (self.gasoline or 0) + \
                         (self.motoboy or 0) + \
                         (self.frete or 0) + \
                         (self.extras or 0)
        self.total_despesas = total_despesas

        # 7. Calculate Commission Rate (Sales Rep)
        # Determine the percentage based on the radio/select logic

        comissao_percent = 0.0

        if self.comis_0: # "Não aplicar comissão" checked
            comissao_percent = 0.0
        elif self.custom_commission: # "Comissão Customizada" checked
            comissao_percent = self.comis_custom or 0.0
        elif self.comis_per and self.comis_per != "Customizada":
            # Field options are "10", "9", etc. Parse string.
            try:
                comissao_percent = float(self.comis_per)
            except ValueError:
                comissao_percent = 0.0

        if "System Manager" in frappe.get_roles(frappe.session.user):
            # Bypass limit check entirely
            pass
        else:
            # Sales Person Limit Logic
            sales_person_limit = 0.0

            # 1. Find Employee & Sales Person
            employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
            if employee:
                sales_person = frappe.db.get_value("Sales Person", {"employee": employee}, ["name", "custom_max_commission_percent"], as_dict=True)
                if sales_person:
                    sales_person_limit = sales_person.custom_max_commission_percent

            # 2. Validation
            # Only validate if a limit is set (>0) AND user is exceeding it
            if sales_person_limit > 0 and comissao_percent > sales_person_limit:
                 frappe.throw(f"Limite de comissão excedido! Seu limite é {sales_person_limit}%.")

        # 8. Total Hard Cost
        # Sum everything up
        total_hard_cost = base_cost_total + fotolito_cost + total_grav_cost + total_embal_cost + total_despesas

        # 9. Target Revenue (Cost + Margin)
        # Margin is a markup on cost. E.g. Cost 100 + Margin 50% = 150 Target
        margin_rate = (self.margin or 0.0) / 100.0
        target_revenue = total_hard_cost * (1.0 + margin_rate)

        # 10. Gross Up (Add BV + Commission on top of Sale Price)
        # Formula: Sale Price = Target Revenue / (1 - (BV% + Com%))
        bv_rate = (self.porcentagem or 0.0) / 100.0
        com_rate = comissao_percent / 100.0
        tax_rate = self.tax_rate / 100.0

        total_fees_rate = bv_rate + com_rate + tax_rate

        valor_final_total = 0.0
        if total_fees_rate < 1.0:
            valor_final_total = target_revenue / (1.0 - total_fees_rate)
        else:
            frappe.throw("A soma de BV e Comissão não pode ser 100% ou mais (Divisão por zero).")

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


