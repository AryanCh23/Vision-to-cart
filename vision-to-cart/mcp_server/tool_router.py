import importlib
import asyncio
from typing import Dict, Any, Callable

# Absolute imports
from mcp_server.error_recovery import with_recovery

class ToolRouter:
    """
    Registry and dispatcher for executing tools by name.
    Automatically wraps all calls in the recovery / retry mechanism.
    """
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._register_tools()

    def _register_tools(self):
        # Maps tool name to its target module and handler function name
        tool_mappings = {
            "image_intelligence_tool": ("tools.image_intelligence_tool", "run_image_intelligence"),
            "nl_understanding_tool": ("tools.nl_understanding_tool", "run_nl_understanding"),
            "catalog_intelligence_tool": ("tools.catalog_intelligence_tool", "run_catalog_intelligence"),
            "search_retrieval_tool": ("tools.search_retrieval_tool", "run_search_retrieval"),
            "ranking_scoring_tool": ("tools.ranking_scoring_tool", "run_ranking_scoring"),
            "recommendation_tool": ("tools.recommendation_tool", "run_recommendation"),
            "pdp_cart_checkout_tool": ("tools.pdp_cart_checkout_tool", "run_cart_action")
        }

        for name, (module_path, func_name) in tool_mappings.items():
            try:
                mod = importlib.import_module(module_path)
                func = getattr(mod, func_name)
                self._tools[name] = func
            except Exception as e:
                print(f"ToolRouter: Warning, failed to register tool '{name}' from {module_path}. Error: {e}")

    async def call_tool(self, tool_name: str, payload: Dict[str, Any]) -> Any:
        if tool_name not in self._tools:
            raise ValueError(f"Tool '{tool_name}' is not registered.")
        
        tool_func = self._tools[tool_name]
        
        # Apply the error recovery wrapper to the tool execution
        # with_recovery performs retries, fallback routing, and failsafe returns.
        recovered_func = with_recovery(tool_name, tool_func)
        
        # Run asynchronously
        if asyncio.iscoroutinefunction(recovered_func):
            return await recovered_func(payload)
        else:
            return recovered_func(payload)
