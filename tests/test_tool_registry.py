import pytest

from invoice_buddy.tools.registry import registry
from invoice_buddy.tools.tool_registry import (
    ToolDefinition,
    ToolRegistry,
)


def test_registry_contains_all_tools():
    tools = registry.list_tools()

    assert len(tools) == 17


def test_registry_get_tool():
    tool = registry.get("total_spend")

    assert tool.name == "total_spend"
    assert tool.description
    assert callable(tool.function)


def test_registry_get_unknown_tool():
    with pytest.raises(KeyError):
        registry.get("does_not_exist")


def test_registry_prevents_duplicate_tools():
    test_registry = ToolRegistry()

    tool = ToolDefinition(
        name="test_tool",
        description="A test tool.",
        function=lambda: None,
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
        },
    )

    test_registry.register(tool)

    with pytest.raises(ValueError):
        test_registry.register(tool)


def test_registry_lists_tools():
    tools = registry.list_tools()

    names = {tool.name for tool in tools}

    assert "get_invoice" in names
    assert "search_invoices" in names
    assert "total_spend" in names
    assert "overdue_invoices" in names


def test_registry_returns_llm_schemas():
    schemas = registry.schemas()

    assert len(schemas) == 17

    total_spend_schema = next(
        schema for schema in schemas if schema["name"] == "total_spend"
    )

    assert total_spend_schema["description"]
    assert total_spend_schema["parameters"]["type"] == "object"


def test_search_invoice_schema_has_filters():
    tool = registry.get("search_invoices")

    properties = tool.parameters["properties"]

    assert "vendor" in properties
    assert "currency" in properties
    assert "min_total" in properties
    assert "max_total" in properties


def test_required_parameters_are_defined():
    tool = registry.get("get_invoice_by_number")

    assert tool.parameters["required"] == ["invoice_number"]
