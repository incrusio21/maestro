// Copyright (c) 2024, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Order Item", {
    custom_check_in(frm, cdt, cdn) {
        frm.trigger("set_enteties", cdt, cdn);
    },
    custom_check_out(frm, cdt, cdn) {
        frm.trigger("set_enteties", cdt, cdn);
    },
	custom_quantity(frm, cdt, cdn) {
        var item = locals[cdt][cdn]
        var real_qty = item.custom_quantity
        if(in_list(["Hotels"], item.item_group)){
            real_qty *= item.custom_entities 
        }

        frappe.model.set_value(cdt, cdn, "qty", flt(real_qty, precision("qty", item)))
    },
    set_enteties(frm, cdt, cdn){
        var item = locals[cdt][cdn]
        
        if(!item.custom_check_in || !item.custom_check_out) return

        check_in = moment(item.custom_check_in).format(frappe.defaultDateFormat)
        check_out = moment(item.custom_check_out).format(frappe.defaultDateFormat)

        frappe.model.set_value(cdt, cdn, "custom_entities", flt(
            frappe.datetime.get_diff(item.custom_check_out, check_in), precision("custom_entities", item)))

        frm.trigger("custom_quantity", cdt, cdn);
    }

})