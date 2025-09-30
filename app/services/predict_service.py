import logging
import time

from app.config import settings
from app.models.schemas import ApiPredictRequest, ApiPredictResponse
from app.services.metrics_service import metrics_service
from app.services.rpc_client import ModelRPCClient

logger = logging.getLogger(__name__)


class PredictService:
    def __init__(self, rabbitmq_url: str | None = None):
        self.rabbitmq_url = rabbitmq_url or settings.rabbitmq_url

    async def predict(self, request: ApiPredictRequest) -> list[ApiPredictResponse]:
        start_time = time.time()
        try:
            async with ModelRPCClient(self.rabbitmq_url) as client:
                result = await client.predict(request.input)
                duration = time.time() - start_time
                metrics_service.record_rpc_request("success", duration)
                return result
        except Exception as e:
            duration = time.time() - start_time
            metrics_service.record_rpc_request("error", duration)
            logger.error(f"Prediction failed: {e}")
            raise
