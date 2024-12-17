# Copyright (c) 2024, DAS and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe.utils import add_days, date_diff, flt

from erpnext.projects.doctype.project.project import Project
from frappe.model.document import Document

class Project(Project):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.do_setting = frappe.get_doc("Daily Operation Setting")
    
    def after_insert(self):
        super().after_insert()
        if not self.sales_order:
            return 
        
        po_list = frappe.get_list("Purchase Order", {"custom_sales_order": self.sales_order}, pluck="name")
        for po in po_list:
            doc = frappe.get_doc("Purchase Order", po)
            doc.project = self.name
            doc.db_update()

        self.update_daily_operation_by_purchase_order()
        self.calculate_summary()
        self.db_update_all()
        self.reload()

    def calculate_summary(self):
        if not self.sales_order:
            return

        sum_dict = {}

        # ambil data so dan create summary list jika blum ada
        so_total = frappe.get_cached_value("Sales Order", self.sales_order, ["currency", "rounded_total", "base_rounded_total"], as_dict=1)
        if not self.get("custom_summary_list"):
            self.create_summary_list()

        # total so masuk dalam field selling sesuai currency
        sum_dict.setdefault(so_total.currency, {"nett": 0, "selling": so_total.rounded_total})
        
        profit_precision = self.precision("custom_profit")
        
        profit = self.summary_by_daily_operation(sum_dict) \
            if not self.do_setting.create_by_purchase_order else self.summary_by_daily_purchase_order(sum_dict)

        for sum_curr in self.custom_summary_list:
            curr_sum = sum_dict.get(sum_curr.total_invoice, {})
            sum_curr.update({
                "nett": curr_sum.get("nett", 0),
                "selling": curr_sum.get("selling", 0)
            })

        # base grand total daily operation - base rounded total sales order
        self.custom_profit = flt(profit - so_total.base_rounded_total, profit_precision)

    def summary_by_daily_purchase_order(self, sum_dict):
        profit = 0

        pur_ord = frappe.qb.DocType("Purchase Order")

        pur_ord_list = (
            frappe.qb.from_(pur_ord)
            .select(pur_ord.name, pur_ord.currency, pur_ord.rounded_total, pur_ord.base_rounded_total)
            .where(
                (pur_ord.docstatus == 1)
                & (pur_ord.project == self.name)
            )
        ).run(as_dict=True)

        for p_o in pur_ord_list:
            curr = sum_dict.setdefault(p_o.currency, {"nett": 0, "selling": 0})
            curr["nett"] += p_o.rounded_total
            profit += p_o.base_rounded_total

        return profit
    
    def summary_by_daily_operation(self, sum_dict):
        profit = 0

        # get total daily operation dan masukkan ke field nett
        for do in self.custom_reference:
            curr = sum_dict.setdefault(do.currency, {"nett": 0, "selling": 0})
            curr["nett"] += do.grand_total
            profit += do.base_grand_total

        return profit

    def create_summary_list(self, selling_curr=None, selling_total=0):
        self.custom_summary_list = []

        # untuk sekarang masih fix tiga currency
        for curr in ["USD", "EUR", "IDR"]:
            self.append("custom_summary_list", {
                "total_invoice": curr,
                "selling": selling_total if selling_curr == curr else 0
            })

    def update_daily_operation_by_purchase_order(self):
        if not self.do_setting.create_by_purchase_order:
            return
        
        pur_ord = frappe.qb.DocType("Purchase Order")
        daily_opt = frappe.qb.DocType("Daily Operation")

        do_list = (
            frappe.qb.from_(daily_opt)
            .inner_join(pur_ord)
            .on(pur_ord.name == daily_opt.purchase_order)
            .select(daily_opt.name.as_("daily_operation"), daily_opt.date, daily_opt.hotel, daily_opt.lunch, daily_opt.flight)
            .where(
                (pur_ord.docstatus == 1)
                & (pur_ord.project == self.name)
            )
            .orderby(daily_opt.date)
        ).run(as_dict=True)

        self.custom_reference = []
        for d_o in do_list:
            self.append("custom_reference", d_o)

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

        