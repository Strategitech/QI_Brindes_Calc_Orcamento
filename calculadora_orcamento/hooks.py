from erpnext.hooks import app_logo_url

app_name = "calculadora_orcamento"
app_title = "Calculadora Orcamento"
app_publisher = "Strategitech"
app_description = "Calculadora de custos totais para orcamento"
app_email = "joaolucasmoura@strategitech.tech"
app_license = "mit"
app_logo_url = "/assets/calculadora_orcamento/QI_logo.png"  # noqa: F811
# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "calculadora_orcamento",
# 		"logo": "/assets/calculadora_orcamento/logo.png",
# 		"title": "Calculadora Orcamento",
# 		"route": "/calculadora_orcamento",
# 		"has_permission": "calculadora_orcamento.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/calculadora_orcamento/css/calculadora_orcamento.css"
# app_include_js = "/assets/calculadora_orcamento/js/calculadora_orcamento.js"

# include js, css files in header of web template
# web_include_css = "/assets/calculadora_orcamento/css/calculadora_orcamento.css"
# web_include_js = "/assets/calculadora_orcamento/js/calculadora_orcamento.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "calculadora_orcamento/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "calculadora_orcamento/public/icons.svg"

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
# 	"methods": "calculadora_orcamento.utils.jinja_methods",
# 	"filters": "calculadora_orcamento.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "calculadora_orcamento.install.before_install"
# after_install = "calculadora_orcamento.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "calculadora_orcamento.uninstall.before_uninstall"
# after_uninstall = "calculadora_orcamento.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "calculadora_orcamento.utils.before_app_install"
# after_app_install = "calculadora_orcamento.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "calculadora_orcamento.utils.before_app_uninstall"
# after_app_uninstall = "calculadora_orcamento.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "calculadora_orcamento.notifications.get_notification_config"

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

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"QI Shipment": {
		"before_save": "calculadora_orcamento.calculadora_orcamento.events.set_orcamento_on_shipment"
	}
}

# Custom Fields
# ---------------

custom_fields = {
	"Delivery Note": [
		{
			"fieldname": "orcamento",
			"fieldtype": "Link",
			"label": "Orçamento",
			"options": "Calculadora Orcamento",
			"insert_after": "customer",
			"read_only": 1,
		}
	],
	"QI Shipment": [
		{
			"fieldname": "orcamento",
			"fieldtype": "Link",
			"label": "Orçamento",
			"options": "Calculadora Orcamento",
			"insert_after": "delivery_note",
			"read_only": 1,
			"in_list_view": 1,
		}
	],
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"calculadora_orcamento.tasks.all"
# 	],
# 	"daily": [
# 		"calculadora_orcamento.tasks.daily"
# 	],
# 	"hourly": [
# 		"calculadora_orcamento.tasks.hourly"
# 	],
# 	"weekly": [
# 		"calculadora_orcamento.tasks.weekly"
# 	],
# 	"monthly": [
# 		"calculadora_orcamento.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "calculadora_orcamento.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "calculadora_orcamento.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "calculadora_orcamento.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["calculadora_orcamento.utils.before_request"]
# after_request = ["calculadora_orcamento.utils.after_request"]

# Job Events
# ----------
# before_job = ["calculadora_orcamento.utils.before_job"]
# after_job = ["calculadora_orcamento.utils.after_job"]

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
# 	"calculadora_orcamento.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

