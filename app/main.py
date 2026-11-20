from contextlib import asynccontextmanager
from pathlib import Path

import numpy as np
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from xgboost import Booster, DMatrix

ARTIFACT_DIR = Path(__file__).resolve().parents[1] / "phase1_artifacts"
FLOAT32_MAX = 3.4028234663852886e38


class PredictionInput(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", allow_inf_nan=False)

    ALLSKY_SFC_SW_DWN: float = Field(ge=0, le=FLOAT32_MAX, description="Reported solar irradiance")
    T2M: float = Field(ge=-FLOAT32_MAX, le=FLOAT32_MAX, description="Air temperature at 2 m")
    T2MDEW: float = Field(ge=-FLOAT32_MAX, le=FLOAT32_MAX, description="Dew point at 2 m")
    RH2M: float = Field(ge=0, le=100, description="Relative humidity at 2 m (%)")
    WS10M: float = Field(ge=0, le=FLOAT32_MAX, description="Wind speed at 10 m")
    Hour: int = Field(ge=0, le=23)
    Month: int = Field(ge=1, le=12)
    DayOfYear: int = Field(ge=1, le=366)


class PredictionOutput(BaseModel):
    predicted_generation: float = Field(description="Estimated generation in unverified dataset units")


@asynccontextmanager
async def lifespan(app: FastAPI):
    model = Booster(params={"nthread": 1}, model_file=ARTIFACT_DIR / "solar_generation_model.ubj")
    features = model.feature_names
    if not features or len(features) != len(PredictionInput.model_fields) or set(features) != set(PredictionInput.model_fields):
        raise RuntimeError("Saved model feature names must match the API schema.")
    app.state.model = model
    app.state.features = features
    yield


app = FastAPI(
    title="SolaRizz API",
    description="Solar Power Generation Prediction and Performance Deviation Analysis",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def invalid_request(_request: Request, exc: RequestValidationError):
    # Invalid input can include non-finite numbers that cannot be echoed in JSON.
    details = [
        {"loc": error["loc"], "msg": error["msg"], "type": error["type"]}
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": details})


@app.get("/")
def root():
    return {"name": app.title, "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionOutput)
def predict(payload: PredictionInput, request: Request):
    features = request.app.state.features
    values = payload.model_dump()
    row = np.array([[values[feature] for feature in features]], dtype=np.float32)
    data = DMatrix(row, feature_names=features, nthread=1)
    prediction = request.app.state.model.predict(data)[0]
    return PredictionOutput(predicted_generation=float(prediction))
