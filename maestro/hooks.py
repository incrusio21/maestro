app_name = "maestro"
app_title = "Maestro"
app_publisher = "DAS"
app_description = "Maestro"
app_email = "das@gmail.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/maestro/css/maestro.css"
# app_include_js = "/assets/maestro/js/maestro.js"

# include js, css files in header of web template
# web_include_css = "/assets/maestro/css/maestro.css"
# web_include_js = "/assets/maestro/js/maestro.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "maestro/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Project" : "maestro/custom/project.js",
    "Purchase Order" : "maestro/custom/purchase_order.js",
    "Sales Order" : "maestro/custom/sales_order.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "maestro/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "maestro.utils.jinja_methods",
# 	"filters": "maestro.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "maestro.install.before_install"
# after_install = "maestro.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "maestro.uninstall.before_uninstall"
# after_uninstall = "maestro.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "maestro.utils.before_app_install"
# after_app_install = "maestro.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "maestro.utils.before_app_uninstall"
# after_app_uninstall = "maestro.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "maestro.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Project": "maestro.overrides.project.Project"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	# "*": {
	# 	"on_update": "method",
	# 	"on_cancel": "method",
	# 	"on_trash": "method"
	# }
    "Purchase Order": {
        "on_submit": ["maestro.maestro.custom.purchase_order.create_daily_operation", "maestro.maestro.custom.purchase_order.update_project_daily_operation"],
        "on_cancel": ["maestro.maestro.custom.purchase_order.update_project_daily_operation", "maestro.maestro.custom.purchase_order.remove_daily_operation"]
    },
    "Project": {
        "validate": ["maestro.maestro.custom.project.validate_so_and_daily_operation", "maestro.maestro.custom.project.create_daily_operation"],
        "after_delete": "maestro.maestro.custom.project.remove_daily_operation",
    },
    "Sales Order": {
        "autoname": "maestro.maestro.custom.sales_order.additional_sales_order_autoname",
        "before_validate": "maestro.maestro.custom.sales_order.real_qty_and_entities_items"
    },
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"maestro.tasks.all"
# 	],
# 	"daily": [
# 		"maestro.tasks.daily"
# 	],
# 	"hourly": [
# 		"maestro.tasks.hourly"
# 	],
# 	"weekly": [
# 		"maestro.tasks.weekly"
# 	],
# 	"monthly": [
# 		"maestro.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "maestro.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"erpnext.selling.doctype.sales_order.sales_order.make_project": "maestro.maestro.custom.sales_order.make_project",
    "erpnext.selling.doctype.sales_order.sales_order.make_purchase_order": "maestro.maestro.custom.sales_order.make_purchase_order"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "maestro.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["maestro.utils.before_request"]
# after_request = ["maestro.utils.after_request"]

# Job Events
# ----------
# before_job = ["maestro.utils.before_job"]
# after_job = ["maestro.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"maestro.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

