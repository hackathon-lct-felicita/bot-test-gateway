from pydantic import BaseModel, Field


class ApiPredictRequest(BaseModel):
    input: str = Field(description="Input text to analyze")


class ApiPredictResponse(BaseModel):
    start_index: int = Field(description="Start character index")
    end_index: int = Field(description="End character index")
    entity: str = Field(description="BIO entity label")
