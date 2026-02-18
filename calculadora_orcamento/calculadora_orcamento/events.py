import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from calculadora_orcamento.hooks import custom_fields


def set_orcamento_on_shipment(doc, method):
    """Auto-populate orcamento from linked Delivery Note."""
    if doc.delivery_note and not doc.get("orcamento"):
        orcamento = frappe.db.get_value("Delivery Note", doc.delivery_note, "orcamento")
        if orcamento:
            doc.orcamento = orcamento


def sync_custom_fields():
    """Create/update custom fields defined in hooks.py."""
    create_custom_fields(custom_fields)
