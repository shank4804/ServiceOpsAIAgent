from typing import Dict, Any
from azure_monitor import AzureMonitorAgent
from llama_index.core.tools import ToolMetadata  # Correct for v0.12.17

class AzureMonitoringTool:
    """Tool for fetching Azure monitoring metrics and details."""
    
    def __init__(self):
        """Initialize the monitoring tool."""
        self.azure_monitor = AzureMonitorAgent()
        self._metadata = ToolMetadata(
            name="azure_monitoring",
            description=(
                "Use this tool to fetch current Azure infrastructure metrics and monitoring details. "
                "This will return information about various services including API Management, "
                "Functions, SQL Database, VM Scale Sets, and more."
            )
        )

    @property
    def metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        return self._metadata

    def run(self, **kwargs: Any) -> Dict:
        """
        Execute the monitoring tool to fetch current metrics.
        
        Returns:
            Dict: Current Azure infrastructure metrics and monitoring details
        """
        try:
            metrics = self.azure_monitor.get_metrics()
            return {
                "status": "success",
                "metrics": metrics
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            } 