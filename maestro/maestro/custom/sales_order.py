# Copyright (c) 2024, DAS and Contributors
# License: GNU General Public License v3. See license.txt

from frappe.utils import date_diff, flt

def real_qty_and_entities_items(self, method=None):
    for i in self.items:
        if not i.custom_quantity:
            i.custom_quantity = i.qty
        
        real_qty = i.custom_quantity
        if i.item_group in ["Hotels"]:
            i.custom_entities = date_diff(i.custom_check_out, i.custom_check_in) or 1
            real_qty *= i.custom_entities

        i.qty = flt(real_qty, i.precision("qty"))