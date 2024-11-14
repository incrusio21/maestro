# Copyright (c) 2024, DAS and Contributors
# License: GNU General Public License v3. See license.txt

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
        
        real_qty = i.custom_quantity
        if i.item_group in ["Hotels"]:
            i.custom_entities = date_diff(i.custom_check_out, i.custom_check_in) or 1
            real_qty *= i.custom_entities

        i.qty = flt(real_qty, i.precision("qty"))

@frappe.whitelist()
def make_additional_sales_order(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.run_method("set_missing_values")
        target.run_method("calculate_taxes_and_totals")

    doc = get_mapped_doc(
        "Sales Order",
        source_name,
        {
            "Sales Order": {
                "doctype": "Sales Order",
                "field_map": {"name": "custom_prev_so"},
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