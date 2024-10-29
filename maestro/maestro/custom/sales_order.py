# Copyright (c) 2024, DAS and Contributors
# License: GNU General Public License v3. See license.txt

from frappe.utils import flt

def real_qty_items(self, method=None):
    for i in self.items:
        if not i.custom_quantity:
            i.custom_quantity = i.qty
            continue
        
        real_qty = i.custom_quantity
        if i.item_group in ["Hotels"]:
            real_qty *= i.custom_entities

        i.qty = flt(real_qty, i.precision("qty"))