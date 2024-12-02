# Copyright (c) 2024, DAS and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe.utils import add_days, date_diff, flt

from erpnext.projects.doctype.project.project import Project
from frappe.model.document import Document

class Project(Project):

    def before_save(self):
        self.calculate_summary()
    
    def calculate_summary(self):
        if not self.sales_order:
            return
        
        sum_dict, profit = {}, 0
        # ambil data so dan create summary list jika blum ada
        so_total = frappe.get_cached_value("Sales Order", self.sales_order, ["currency", "rounded_total", "base_rounded_total"], as_dict=1)
        if not self.get("custom_summary_list"):
            self.create_summary_list()

        # total so masuk dalam field selling sesuai currency
        sum_dict.setdefault(so_total.currency, {"nett": 0, "selling": so_total.rounded_total})

        profit_precision = self.precision("custom_profit")

        # get total daily operation dan masukkan ke field nett
        for do in self.custom_reference:
            curr = sum_dict.setdefault(do.currency, {"nett": 0, "selling": 0})
            curr["nett"] += do.grand_total
            profit += do.base_grand_total
        
        for sum_curr in self.custom_summary_list:
            curr_sum = sum_dict.get(sum_curr.total_invoice, {})
            sum_curr.update({
                "nett": curr_sum.get("nett", 0),
                "selling": curr_sum.get("selling", 0)
            })

        # base grand total daily operation - base rounded total sales order
        self.custom_profit = flt(profit - so_total.base_rounded_total, profit_precision)

    def create_summary_list(self, selling_curr=None, selling_total=0):
        self.custom_summary_list = []

        # untuk sekarang masih fix tiga currency
        for curr in ["USD", "EUR", "IDR"]:
            self.append("custom_summary_list", {
                "total_invoice": curr,
                "selling": selling_total if selling_curr == curr else 0
            })

    def upadate_daily_operation_ref(self, daily_operation=None):
        do_to_update, selected_do = self.custom_reference, False
        
        # update field pada table reference. jika terdapat isi daily operation maka hanya ubah data tersebut
        if isinstance(daily_operation, Document):
            do_to_update = self.get("custom_reference", {"daily_operation": daily_operation.get("name")})
            selected_do = True
    
        updated_field = ["date", "hotel", "lunch", "flight", "currency", "grand_total", "conversion_rate", "base_grand_total"]
        for dop in do_to_update:
            do = frappe.get_value("Daily Operation", dop.daily_operation, updated_field, as_dict=1) if not selected_do else daily_operation
            for field in updated_field:
                dop.set(field, do.get(field))
        
            

        self.calculate_summary()

    @frappe.whitelist()    
    def create_daily_operation(self):
        # memastikan tanggal akhir lebih besar dari awal
        dd =  date_diff(self.expected_end_date, self.expected_start_date)
        if dd < 0:
            frappe.throw("Invalid date selection: check-out date cannot exceed check-in date.")

        # ambil data sales order untuk default value table reference
        so_total = frappe.get_cached_value("Sales Order", self.sales_order, ["currency", "conversion_rate"], as_dict=1)

        # buat ulang isi dari table reference
        self.custom_reference = []
        for idx in range(0, dd + 1):
            self.append("custom_reference", {
                "date": add_days(self.expected_start_date, idx),
                "currency": so_total.currency,
                "conversion_rate": so_total.conversion_rate,
            })

        