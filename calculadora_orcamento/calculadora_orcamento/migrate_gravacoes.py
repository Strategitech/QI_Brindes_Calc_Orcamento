# Copyright (c) 2026, Strategitech and contributors
# One-time migration: convert grav_1/grav_2 fields to gravacoes child table.
# Run: bench --site SITE execute calculadora_orcamento.calculadora_orcamento.migrate_gravacoes.migrate

import frappe


def migrate():
    """Migrate existing grav_1/grav_2 data to the gravacoes child table."""
    count_migrated = 0
    count_skipped = 0

    docs = frappe.get_all(
        "Calculadora Orcamento",
        filters={},
        fields=["name"],
    )

    for entry in docs:
        doc = frappe.get_doc("Calculadora Orcamento", entry.name)

        # Skip if already has gravacoes child rows
        if doc.gravacoes and len(doc.gravacoes) > 0:
            count_skipped += 1
            continue

        has_grav_data = False

        # Migrate grav_1
        if doc.catalogo_grav_1 or (doc.unit_cost_grav_1 and doc.unit_cost_grav_1 > 0):
            has_grav_data = True
            doc.append("gravacoes", {
                "catalogo_gravacao": doc.catalogo_grav_1 or None,
                "unidade": doc.unit_qtd_grav_1 or "Unitario",
                "custo_unitario": doc.unit_cost_grav_1 or 0,
                "descricao": doc.desc_grav_1 or "",
                "total": doc.total_grav_1 or 0,
            })

        # Migrate grav_2
        if doc.catalogo_grav_2 or (doc.unit_cost_grav_2 and doc.unit_cost_grav_2 > 0):
            has_grav_data = True
            doc.append("gravacoes", {
                "catalogo_gravacao": doc.catalogo_grav_2 or None,
                "unidade": doc.unit_qtd_grav_2 or "Unitario",
                "custo_unitario": doc.unit_cost_grav_2 or 0,
                "descricao": doc.desc_grav_2 or "",
                "total": doc.total_grav_2 or 0,
            })

        if has_grav_data:
            doc.total_gravacao = (doc.total_grav_1 or 0) + (doc.total_grav_2 or 0)
            doc.flags.ignore_validate = True
            doc.save(ignore_permissions=True)
            count_migrated += 1
        else:
            count_skipped += 1

    frappe.db.commit()
    print(f"Migration complete: {count_migrated} migrated, {count_skipped} skipped")
