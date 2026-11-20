from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from xgboost import XGBRegressor

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
    model = XGBRegressor()
    model.load_model(ARTIFACT_DIR / "solar_generation_model.ubj")
    features = joblib.load(ARTIFACT_DIR / "solar_feature_names.pkl")
    if list(model.feature_names_in_) != features or set(features) != set(PredictionInput.model_fields):
        raise RuntimeError("Saved model, feature list, and API schema must agree.")
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
    row = pd.DataFrame([payload.model_dump()], columns=features)
    prediction = request.app.state.model.predict(row)[0]
    return PredictionOutput(predicted_generation=float(prediction))
