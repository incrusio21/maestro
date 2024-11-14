// Copyright (c) 2024, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Order", {
    refresh(frm) {
        console.log(frm.doc.docstatus)
        if(frm.doc.docstatus == 1){
            frm.add_custom_button(
                __("Additional Order"),
                    function () {
                        frappe.model.open_mapped_doc({
                            method: "maestro.maestro.custom.sales_order.make_additional_sales_order",
                            frm: cur_frm,
                            freeze_message: __("Creating Sales Order ..."),
                        });
                    },
                __("Create")
            )
        }
    }
})

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