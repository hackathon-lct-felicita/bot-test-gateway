import asyncio
import json
import logging
import uuid

import aio_pika
from aio_pika import Message
from aio_pika.abc import (
    AbstractChannel,
    AbstractConnection,
    AbstractIncomingMessage,
    AbstractQueue,
)

from app.models.schemas import ApiPredictRequest, ApiPredictResponse

logger = logging.getLogger(__name__)


class ModelRPCClient:
    """RabbitMQ RPC client for model predictions."""

    def __init__(self, rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"):
        self.rabbitmq_url = rabbitmq_url
        self.connection: AbstractConnection | None = None
        self.channel: AbstractChannel | None = None
        self.callback_queue: AbstractQueue | None = None
        self.futures: dict[str, asyncio.Future] = {}

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()

    async def connect(self) -> None:
        """Connect to RabbitMQ."""
        try:
            self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
            self.channel = await self.connection.channel()

            self.callback_queue = await self.channel.declare_queue(
                exclusive=True, auto_delete=True
            )

            await self.callback_queue.consume(self.on_response)

            logger.info("Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from RabbitMQ."""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("Disconnected from RabbitMQ")

    async def on_response(self, message: AbstractIncomingMessage) -> None:
        """Handle RPC response."""
        async with message.process():
            correlation_id = message.correlation_id

            if correlation_id in self.futures:
                future = self.futures.pop(correlation_id)

                try:
                    json_str = message.body.decode("utf-8")
                    response_data = json.loads(json_str)
                    response = [ApiPredictResponse(**item) for item in response_data]
                    future.set_result(response)
                except Exception as e:
                    future.set_exception(e)

    async def call(
        self, request: ApiPredictRequest, timeout: float = 30.0
    ) -> list[ApiPredictResponse]:
        """Make RPC call to model service."""
        if not self.channel or not self.callback_queue:
            raise RuntimeError("Not connected to RabbitMQ. Call connect() first.")

        correlation_id = str(uuid.uuid4())

        future = asyncio.Future()
        self.futures[correlation_id] = future

        try:
            request_json = request.model_dump_json()
            message = Message(
                body=request_json.encode("utf-8"),
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
            )

            await self.channel.default_exchange.publish(
                message,
                routing_key="model_rpc_queue",
            )

            logger.info(f"Sent RPC request with correlation_id: {correlation_id}")

            response = await asyncio.wait_for(future, timeout=timeout)
            return response

        except TimeoutError as e:
            self.futures.pop(correlation_id, None)
            raise Exception(f"RPC call timed out after {timeout} seconds") from e
        except Exception:
            self.futures.pop(correlation_id, None)
            raise

    async def predict(
        self, text: str, timeout: float = 30.0
    ) -> list[ApiPredictResponse]:
        request = ApiPredictRequest(input=text)
        return await self.call(request, timeout)
