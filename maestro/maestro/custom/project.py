# Copyright (c) 2024, DAS and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe.utils import date_diff

def validate_so_and_daily_operation(self, method):
    if self.do_setting.create_by_purchase_order:
        return 
    
    do_project = self.get("custom_reference", { "daily_operation": True })
    if not do_project:
        return
    
    # validasi daily operation harus memiliki sales order yang sama dengan project 
    do_list = frappe.get_list("Daily Operation", 
        {
            "name": ["in", [r.daily_operation for r in do_project]],
            "sales_order": ["!=", self.sales_order]
        }, pluck="name")
    
    if do_list or len(do_project) != (
        date_diff(self.expected_end_date, self.expected_start_date) + 1
    ):
        frappe.throw("Please recreate the daily operation.")

def create_daily_operation(self, method=None):
    if self.do_setting.create_by_purchase_order:
        return 
    
    not_link_do = self.get("custom_reference", { "daily_operation": False })
    if not not_link_do:
        return
    
    # buat daily operation dengan default value sesuai dengan data pada  
    for row in not_link_do:
        do = frappe.new_doc("Daily Operation")
        # field dari doc project
        for field in ["sales_order", "company"]:
            do.set(field, self.get(field))

        # field dari table references
        for field in ["date", "hotel", "lunch", "flight", "currency", "conversion_rate", "grand_total"]:
            do.set(field, row.get(field))

        do.update_base_total()
        do.save()

        row.daily_operation = do.name
        row.base_grand_total = do.base_grand_total
        
    # check data reference pada database untuk d bandingkan
    previous = self.get_doc_before_save()
    if not previous or not previous.get("custom_reference"):
        return
    
    # get data daily operation yang sudah tidak ada pada table untuk d hapus
    removed_do = list(set([x.daily_operation for x in previous.custom_reference]) - set([x.daily_operation for x in self.custom_reference]))    
    if not removed_do:
        return

    for row in removed_do:
        frappe.delete_doc("Daily Operation", row, force=1)

def remove_daily_operation(self, method=None):
    if self.do_setting.create_by_purchase_order:
        return 
    
    link_do = self.get("custom_reference", { "daily_operation": True })
    
    for row in link_do:
        frappe.delete_doc("Daily Operation", row.daily_operation)
