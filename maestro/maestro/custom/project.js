// Copyright (c) 2024, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Project", {
    refresh: function (frm) {
        frm.set_df_property("custom_reference", "cannot_add_rows", true);
		frm.set_df_property("custom_reference", "cannot_delete_rows", true);

        frm.set_query("hotel", "custom_reference", function (doc, cdt, cdn) {
            // var item = locals[cdt][cdn]

			return {
				filters: {
					item_group: "Hotels",
				},
			};
		});
    },
    custom_create_daily_operation(frm){
        if(!frm.doc.expected_start_date || ! frm.doc.expected_end_date){
            frappe.throw("Please enter the check-in and check-out dates.")
        }

        if((frm.doc.custom_reference || []).length > 0){
            erpnext.project.show_prompt_reset_daily_operation(frm)
        }else{
            erpnext.project.create_daily_operation(frm)
        }
    }
})

erpnext.project = {
    show_prompt_reset_daily_operation : function(frm) {
        frappe.warn('The Daily Operation will be removed.',
            'Are you certain you want to proceed?',
            () => {            
                erpnext.project.create_daily_operation(frm)
            },
            'Continue'
        )
    },
    create_daily_operation: function(frm){
        frappe.call({
            doc: frm.doc,
            method: "create_daily_operation",
            freeze: true,
            callback: function () {
                frm.doc.__unsaved = 1
                frm.get_field("custom_reference").grid.reset_grid()
            },
        })
    }
}