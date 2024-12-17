// Copyright (c) 2024, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Purchase Order", {
    refresh(frm) {
        if(frm.doc.docstatus == 1 && frm.doc.custom_sales_order && !frm.doc.project){
            frm.add_custom_button(
                __("Project"),
                    function () {
                        frappe.model.open_mapped_doc({
                            method: "maestro.maestro.custom.purchase_order.make_project",
                            frm: cur_frm,
                            freeze_message: __("Creating Purchase Order ..."),
                        });
                    },
                __("Create")
            )
        }
    }
})