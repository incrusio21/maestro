// Copyright (c) 2024, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Order Item", {
	custom_quantity(frm, cdt, cdn) {
        var item = locals[cdt][cdn]
        var real_qty = item.custom_quantity
        if(in_list(["Hotels"], item.item_group)){
            real_qty *= item.custom_entities 
        }

        frappe.model.set_value(cdt, cdn, "qty", flt(real_qty, precision("qty", item)))
    }
})