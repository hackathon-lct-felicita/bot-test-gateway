import logging
import time

from fastapi import APIRouter, HTTPException, Response

from app.models.schemas import ApiPredictRequest, ApiPredictResponse
from app.services.metrics_service import metrics_service
from app.services.predict_service import PredictService

logger = logging.getLogger(__name__)

router = APIRouter()
predict_service = PredictService()


@router.post("/predict")
async def predict(request: ApiPredictRequest) -> list[ApiPredictResponse]:
    start_time = time.time()
    try:
        result = await predict_service.predict(request)
        duration = time.time() - start_time
        metrics_service.record_predict_request("success", duration)
        return result
    except Exception as e:
        duration = time.time() - start_time
        metrics_service.record_predict_request("error", duration)
        logger.error(f"Prediction endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/metrics")
async def metrics() -> Response:
    """Prometheus metrics endpoint."""
    metrics_data, content_type = metrics_service.get_metrics()
    return Response(content=metrics_data, media_type=content_type)
