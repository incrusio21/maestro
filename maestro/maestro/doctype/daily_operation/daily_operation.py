# Copyright (c) 2024, DAS and contributors
# For license information, please see license.txt

import frappe

from frappe import _
from frappe.utils import flt
from frappe.model.document import Document


class DailyOperation(Document):
	
	def validate(self):
		self.validate_conversion_rate()
		self.update_base_total()
		self.update_project()
	
	def validate_conversion_rate(self):
		if not self.conversion_rate:
			frappe.throw(
				_("{0} is mandatory. Maybe Currency Exchange record is not created for {1}.").format(
					self.meta.get_label("conversion_rate"), self.currency
				)
			)
	def update_base_total(self):
		self.base_grand_total = (
			flt(self.grand_total * self.conversion_rate, self.precision("base_grand_total"))
		)

	def update_project(self):
		if self.get("__islocal"):
			return
		
		project = frappe.get_value("Daily Operation Project", { "daily_operation": self.name }, "parent")
		doc = frappe.get_doc("Project", project, for_update=1)
		doc.upadate_daily_operation_ref(self)
		doc.save(ignore_permissions=None)

