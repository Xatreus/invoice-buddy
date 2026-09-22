from invoice_buddy.tools.anomaly_tools import (
    detect_anomalies_tool,
)
from invoice_buddy.tools.analytics_tools import (
    average_invoice_value_tool,
    invoice_count_tool,
    invoices_between_dates_tool,
    largest_invoice_tool,
    overdue_invoices_tool,
    spend_by_currency_tool,
    spend_by_vendor_tool,
    total_spend_tool,
    vendor_invoice_history_tool,
)

from invoice_buddy.tools.invoice_tools import (
    get_invoice_by_number_tool,
    get_invoice_tool,
    search_invoices_by_date_tool,
    search_invoices_by_vendor_text_tool,
    search_invoices_tool,
)

from invoice_buddy.tools.tool_registry import (
    ToolDefinition,
    ToolRegistry,
)

registry = ToolRegistry()


registry.register(
    ToolDefinition(
        name="get_invoice",
        description="Get an invoice by its database ID.",
        function=get_invoice_tool,
        parameters={
            "type": "object",
            "properties": {
                "invoice_id": {
                    "type": "integer",
                    "description": "The database ID of the invoice.",
                },
            },
            "required": ["invoice_id"],
        },
    )
)


registry.register(
    ToolDefinition(
        name="get_invoice_by_number",
        description="Get an invoice using its invoice number.",
        function=get_invoice_by_number_tool,
        parameters={
            "type": "object",
            "properties": {
                "invoice_number": {
                    "type": "string",
                    "description": "The invoice number.",
                },
            },
            "required": ["invoice_number"],
        },
    )
)


registry.register(
    ToolDefinition(
        name="search_invoices",
        description="Search invoices using vendor, currency, and total-value filters.",
        function=search_invoices_tool,
        parameters={
            "type": "object",
            "properties": {
                "vendor": {
                    "type": "string",
                    "description": "Exact vendor name.",
                },
                "currency": {
                    "type": "string",
                    "description": "Currency code such as INR or USD.",
                },
                "min_total": {
                    "type": "number",
                    "description": "Minimum invoice total.",
                },
                "max_total": {
                    "type": "number",
                    "description": "Maximum invoice total.",
                },
            },
            "required": [],
        },
    )
)


registry.register(
    ToolDefinition(
        name="search_invoices_by_date",
        description="Find invoices within an invoice-date range.",
        function=search_invoices_by_date_tool,
        parameters={
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "Start date in YYYY-MM-DD format.",
                },
                "end_date": {
                    "type": "string",
                    "description": "End date in YYYY-MM-DD format.",
                },
            },
            "required": ["start_date", "end_date"],
        },
    )
)


registry.register(
    ToolDefinition(
        name="search_invoices_by_vendor_text",
        description="Search invoices using partial vendor-name text.",
        function=search_invoices_by_vendor_text_tool,
        parameters={
            "type": "object",
            "properties": {
                "vendor_text": {
                    "type": "string",
                    "description": "Text to search for in vendor names.",
                },
            },
            "required": ["vendor_text"],
        },
    )
)


registry.register(
    ToolDefinition(
        name="invoice_count",
        description="Return the total number of invoices.",
        function=invoice_count_tool,
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
        },
    )
)


registry.register(
    ToolDefinition(
        name="total_spend",
        description="Calculate total spending across all invoices.",
        function=total_spend_tool,
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
        },
    )
)


registry.register(
    ToolDefinition(
        name="average_invoice_value",
        description="Calculate the average invoice value.",
        function=average_invoice_value_tool,
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
        },
    )
)


registry.register(
    ToolDefinition(
        name="largest_invoice",
        description="Find the invoice with the largest total value.",
        function=largest_invoice_tool,
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
        },
    )
)


registry.register(
    ToolDefinition(
        name="spend_by_vendor",
        description=(
            "Return total spending grouped by every vendor. "
            "This tool takes no arguments. "
            "Use this when the user wants a breakdown of spending "
            "across all vendors."
        ),
        function=spend_by_vendor_tool,
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
        },
    )
)


registry.register(
    ToolDefinition(
        name="spend_by_currency",
        description="Calculate total spending grouped by currency.",
        function=spend_by_currency_tool,
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
        },
    )
)


registry.register(
    ToolDefinition(
        name="invoices_between_dates",
        description="Return invoices within a specified date range.",
        function=invoices_between_dates_tool,
        parameters={
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "Start date in YYYY-MM-DD format.",
                },
                "end_date": {
                    "type": "string",
                    "description": "End date in YYYY-MM-DD format.",
                },
            },
            "required": ["start_date", "end_date"],
        },
    )
)


registry.register(
    ToolDefinition(
        name="overdue_invoices",
        description="Return invoices that were overdue as of a specified date.",
        function=overdue_invoices_tool,
        parameters={
            "type": "object",
            "properties": {
                "as_of": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format.",
                },
            },
            "required": ["as_of"],
        },
    )
)


registry.register(
    ToolDefinition(
        name="vendor_invoice_history",
        description=(
            "Return the complete invoice history for ONE specific vendor. "
            "Use this when the user asks about a particular vendor, "
            "including how much was spent with that vendor or how many "
            "invoices that vendor has."
        ),
        function=vendor_invoice_history_tool,
        parameters={
            "type": "object",
            "properties": {
                "vendor": {
                    "type": "string",
                    "description": "Vendor name.",
                },
            },
            "required": ["vendor"],
        },
    )
)

registry.register(
    ToolDefinition(
        name="detect_anomalies",
        description=(
            "Scan all invoices for potential anomalies. "
            "Use this when the user asks about suspicious, "
            "unusual, or potentially problematic invoices. "
            "Returns detected large invoices and vendor "
            "spending outliers."
        ),
        function=detect_anomalies_tool,
        parameters={
            "type": "object",
            "properties": {
                "large_invoice_threshold": {
                    "type": "string",
                    "description": (
                        "Optional invoice total threshold. Defaults to 100000.00."
                    ),
                },
            },
            "required": [],
        },
    )
)
