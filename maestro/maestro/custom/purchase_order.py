# Copyright (c) 2024, DAS and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe.model.mapper import get_mapped_doc, make_mapped_doc

def update_project_daily_operation(self, method=None):
    # skip jika blum memiliki project
    if not self.project:
        return

    project = frappe.get_doc("Project", self.project, for_update=1)
    project.update_daily_operation_by_purchase_order()
    project.calculate_summary()
    project.save()

def create_daily_operation(self, method):
    if not self.get("custom_sales_order"):
        return
    
    do_setting = frappe.get_doc("Daily Operation Setting")
    if not do_setting.create_by_purchase_order:
        return
    
    fieldname_list = { dos.item_group: dos.fieldname for dos in do_setting.fieldname_item_filters }

    date_item = {}
    for ig in do_setting.item_group_date:
        date_item.setdefault(ig.item_group, []).append(ig.fieldname)

    for item in self.items:
        if not date_item.get(item.item_group):
            date_item.setdefault(item.item_group, []).append("schedule_date")
        
        for new_do in date_item.get(item.item_group):
            do = frappe.new_doc("Daily Operation")
            do.date = item.get(new_do)
            do.purchase_order = self.name
            do.company = self.company
            do.supplier = self.supplier

            fieldname = fieldname_list.get(item.item_group)
            do.set(fieldname, item.item_code)
            do.save()

def remove_daily_operation(self, method):
    frappe.db.sql(
        "delete from `tabDaily Operation` where purchase_order=%s", (self.name)
    )

@frappe.whitelist()
def make_project(source_name, target_doc=None):
    purchase_order = frappe.get_doc("Purchase Order", source_name)
    if not purchase_order.get("custom_sales_order"):
        frappe.throw("Purchase Orders need a Sales Order to have a Project.")

    project = make_mapped_doc("erpnext.selling.doctype.sales_order.sales_order.make_project", purchase_order.custom_sales_order)

    return project