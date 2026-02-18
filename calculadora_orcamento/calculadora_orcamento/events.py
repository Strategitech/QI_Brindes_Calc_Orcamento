import frappe


def set_orcamento_on_shipment(doc, method):
    """Auto-populate orcamento from linked Delivery Note."""
    if doc.delivery_note and not doc.get("orcamento"):
        orcamento = frappe.db.get_value("Delivery Note", doc.delivery_note, "orcamento")
        if orcamento:
            doc.orcamento = orcamento
