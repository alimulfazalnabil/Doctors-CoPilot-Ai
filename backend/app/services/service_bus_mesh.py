import os
import json
import logging
from typing import Dict, Any
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage
from azure.identity.aio import DefaultAzureCredential

logger = logging.getLogger("uvicorn.error")

class ServiceBusMeshPublisher:
    """Handles asynchronous message publishing to Azure Service Bus queues for background processing."""
    
    def __init__(self):
        self.connection_string = os.environ.get("AZURE_SERVICEBUS_CONNECTION_STRING")
        self.queue_name = os.environ.get("AZURE_SERVICEBUS_QUEUE_NAME", "transcription-queue")
        
    async def publish_message(self, message_payload: Dict[str, Any]) -> None:
        """Publishes a structured JSON consultation payload to the Azure Service Bus queue."""
        body = json.dumps(message_payload)
        
        if self.connection_string:
            # Connect via explicit connection string if provided
            async with ServiceBusClient.from_connection_string(
                conn_str=self.connection_string, logging_enable=False
            ) as client:
                async with client.get_queue_sender(queue_name=self.queue_name) as sender:
                    message = ServiceBusMessage(body)
                    await sender.send_messages(message)
                    logger.info(f"Published message {message_payload.get('consultation_id')} to Service Bus queue.")
        else:
            # Fallback to Managed Identity (DefaultAzureCredential) using fully qualified namespace
            fully_qualified_namespace = os.environ.get("AZURE_SERVICEBUS_NAMESPACE")
            if not fully_qualified_namespace:
                logger.warning("Service Bus connection details missing; message simulation mode active.")
                return

            credential = DefaultAzureCredential()
            async with ServiceBusClient(
                fully_qualified_namespace=fully_qualified_namespace,
                credential=credential,
                logging_enable=False
            ) as client:
                async with client.get_queue_sender(queue_name=self.queue_name) as sender:
                    message = ServiceBusMessage(body)
                    await sender.send_messages(message)
                    logger.info(f"Published message via Managed Identity to Service Bus queue.")
