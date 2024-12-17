# Copyright (c) 2024, DAS and Contributors
# License: GNU General Public License v3. See license.txt

import json
from erpnext.selling.doctype.sales_order.sales_order import is_product_bundle, set_delivery_date
import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cint, date_diff, flt

def additional_sales_order_autoname(self, method=None):
    if not self.custom_prev_so:
        return

    am_id = 1
    am_prefix = self.custom_prev_so
    if frappe.db.get_value(self.doctype, self.custom_prev_so, "custom_prev_so"):
        am_id = cint(self.custom_prev_so.split("-")[-1]) + 1
        am_prefix = "-".join(self.custom_prev_so.split("-")[:-1])  # except the last hyphen

    self.name = am_prefix + "-" + str(am_id)

def real_qty_and_entities_items(self, method=None):
    for i in self.items:
        if not i.custom_quantity:
            i.custom_quantity = i.qty
        
        # menghitung qty asli hanya jika item group hotels
        real_qty = i.custom_quantity
        if i.item_group in ["Hotels"]:
            i.custom_entities = date_diff(i.custom_check_out, i.custom_check_in) or 1
            real_qty *= i.custom_entities

        i.qty = flt(real_qty, i.precision("qty"))

@frappe.whitelist()
def make_additional_sales_order(source_name, target_doc=None):
    def set_missing_values(source, target):
        if not source.custom_prev_so:
            target.custom_prev_so = source.name

        target.run_method("set_missing_values")
        target.run_method("calculate_taxes_and_totals")

    doc = get_mapped_doc(
        "Sales Order",
        source_name,
        {
            "Sales Order": {
                "doctype": "Sales Order",
                "field_no_map": ["taxes_and_charges"],
                "validation": {
                    "docstatus": ["=", 1],
                },
            }
        },
        target_doc,
        set_missing_values,
        ignore_child_tables=True
    )

    return doc

@frappe.whitelist()
def make_purchase_order(source_name, selected_items=None, target_doc=None):
	if not selected_items:
		return

	if isinstance(selected_items, str):
		selected_items = json.loads(selected_items)

	items_to_map = [
		item.get("item_code") for item in selected_items if item.get("item_code") and item.get("item_code")
	]
	items_to_map = list(set(items_to_map))

	def is_drop_ship_order(target):
		drop_ship = True
		for item in target.items:
			if not item.delivered_by_supplier:
				drop_ship = False
				break

		return drop_ship

	def set_missing_values(source, target):
		target.supplier = ""
		target.apply_discount_on = ""
		target.additional_discount_percentage = 0.0
		target.discount_amount = 0.0
		target.inter_company_order_reference = ""
		target.shipping_rule = ""
		target.tc_name = ""
		target.terms = ""
		target.payment_terms_template = ""
		target.payment_schedule = []

		if is_drop_ship_order(target):
			if source.shipping_address_name:
				target.shipping_address = source.shipping_address_name
				target.shipping_address_display = source.shipping_address
			else:
				target.shipping_address = source.customer_address
				target.shipping_address_display = source.address_display

			target.customer_contact_person = source.contact_person
			target.customer_contact_display = source.contact_display
			target.customer_contact_mobile = source.contact_mobile
			target.customer_contact_email = source.contact_email
		else:
			target.customer = target.customer_name = target.shipping_address = None

		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")

	def update_item(source, target, source_parent):
		target.schedule_date = source.delivery_date
		target.qty = flt(source.qty) - (flt(source.ordered_qty) / flt(source.conversion_factor))
		target.stock_qty = flt(source.stock_qty) - flt(source.ordered_qty)
		target.project = source_parent.project

	def update_item_for_packed_item(source, target, source_parent):
		target.qty = flt(source.qty) - flt(source.ordered_qty)

	# po = frappe.get_list("Purchase Order", filters={"sales_order":source_name, "supplier":supplier, "docstatus": ("<", "2")})
	doc = get_mapped_doc(
		"Sales Order",
		source_name,
		{
			"Sales Order": {
				"doctype": "Purchase Order",
				"field_map": { "name": "custom_sales_order" },
				"field_no_map": [
					"address_display",
					"contact_display",
					"contact_mobile",
					"contact_email",
					"contact_person",
					"taxes_and_charges",
					"shipping_address",
				],
				"validation": {"docstatus": ["=", 1]},
			},
			"Sales Order Item": {
				"doctype": "Purchase Order Item",
				"field_map": [
					["name", "sales_order_item"],
					["parent", "sales_order"],
					["stock_uom", "stock_uom"],
					["uom", "uom"],
					["conversion_factor", "conversion_factor"],
					["delivery_date", "schedule_date"],
				],
				"field_no_map": [
					"rate",
					"price_list_rate",
					"item_tax_template",
					"discount_percentage",
					"discount_amount",
					"supplier",
					"pricing_rules",
				],
				"postprocess": update_item,
				"condition": lambda doc: doc.ordered_qty < doc.stock_qty
				and doc.item_code in items_to_map
				and not is_product_bundle(doc.item_code),
			},
			"Packed Item": {
				"doctype": "Purchase Order Item",
				"field_map": [
					["name", "sales_order_packed_item"],
					["parent", "sales_order"],
					["uom", "uom"],
					["conversion_factor", "conversion_factor"],
					["parent_item", "product_bundle"],
					["rate", "rate"],
				],
				"field_no_map": [
					"price_list_rate",
					"item_tax_template",
					"discount_percentage",
					"discount_amount",
					"supplier",
					"pricing_rules",
				],
				"postprocess": update_item_for_packed_item,
				"condition": lambda doc: doc.parent_item in items_to_map,
			},
		},
		target_doc,
		set_missing_values,
	)

	set_delivery_date(doc.items, source_name)

	return doc

@frappe.whitelist()
def make_project(source_name, target_doc=None):
    def postprocess(source, doc):
        doc.project_type = "External"
        doc.project_name = source.name
        
        doc.create_summary_list(source.currency, source.rounded_total)

    doc = get_mapped_doc(
        "Sales Order",
        source_name,
        {
            "Sales Order": {
                "doctype": "Project",
                "validation": {"docstatus": ["=", 1]},
                "field_map": {
                    "name": "sales_order",
                    "base_grand_total": "estimated_costing",
                    "net_total": "total_sales_amount",
                },
            },
        },
        target_doc,
        postprocess,
    )

    return doc