import os
import logging
from azure.monitor.opentelemetry import configure_azure_monitor

logger = logging.getLogger("uvicorn.error")

def setup_opentelemetry(app):
    """
    Initializes OpenTelemetry and links it with Azure Monitor Application Insights 
    using the official azure-monitor-opentelemetry package distro.
    """
    connection_string = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    
    if not connection_string:
        logger.warning("APPLICATIONINSIGHTS_CONNECTION_STRING is not set. Distributed tracing to Azure Monitor is disabled.")
        return

    # Configure Azure Monitor OpenTelemetry distro (handles traces, metrics, and logs automatically)
    configure_azure_monitor(
        connection_string=connection_string,
        enable_live_metrics=True,
    )
    logger.info("Azure Monitor OpenTelemetry distributed tracing successfully initialized.")
