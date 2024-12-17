// Copyright (c) 2024, DAS and contributors
// For license information, please see license.txt

frappe.provide("maestro")

frappe.ui.form.on("Daily Operation Setting", {
	refresh(frm) {
        maestro.do_setting.set_fieldname_select(frm)
        maestro.do_setting.set_purchase_order_fieldname(frm)
	},
    create_by_purchase_order(frm){
        maestro.do_setting.set_purchase_order_fieldname(frm)
    }
});

maestro.do_setting = {
    set_fieldname_select: (frm) => {
        let doctype = "Daily Operation"
        frappe.model.with_doctype(doctype, () => {
            // get doctype fields
            let fields = $.map(
                frappe.get_doc("DocType", doctype).fields,
                (d) => {
                    if (
                        d.fieldtype == "Link" && d.options == "Item"
                    ) {
                        return {
                            label: `${__(d.label, null, d.parent)}`,
                            value: d.fieldname,
                        };
                    } else {
                        return null;
                    }
                }
            );

            frm.fields_dict.fieldname_item_filters.grid.update_docfield_property(
                "fieldname",
                "options",
                [""].concat(fields)
            );
        })
    },
    set_purchase_order_fieldname: (frm) => {
        if (frm.doc.create_by_purchase_order) {
            let doctype = "Purchase Order Item"
            frappe.model.with_doctype(doctype, () => {
                // get doctype fields
                let fields = $.map(
                    frappe.get_doc("DocType", doctype).fields,
                    (d) => {
                        if (
                            d.fieldtype == "Date"
                        ) {
                            return {
                                label: `${__(d.label, null, d.parent)}`,
                                value: d.fieldname,
                            };
                        } else {
                            return null;
                        }
                    }
                );
    
                frm.fields_dict.item_group_date.grid.update_docfield_property(
                    "fieldname",
                    "options",
                    [""].concat(fields)
                );
            })
        }
    }
}