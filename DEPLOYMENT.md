# Deploy SolaRizz on Vercel

SolaRizz is a FastAPI prediction API. Vercel's FastAPI preset serves the ASGI application in `app/main.py` as a Python 3.12 function. Uvicorn is for local development. The function loads the trained XGBoost Booster from `phase1_artifacts/solar_generation_model.ubj` and checks its embedded feature names against the API schema at startup.

## Production settings

| Setting | Value |
|---|---|
| Git repository | `tejasai-m-code/SOLAR-POWER-GENERATION-PREDICTION-` |
| Production branch | `main` |
| Framework preset | FastAPI |
| Root directory | Repository root |
| Python version | 3.12 via `.python-version` |
| Install and build commands | Vercel FastAPI defaults |
| Production dependencies | `requirements.txt` |
| Application environment variables | None required |

Import the existing GitHub repository in the authorized Vercel scope, or use its existing Vercel project. If Vercel cannot list the repository, grant its GitHub App access to this repository. Let Vercel build the project and use its reported production domain. Future pushes to `main` redeploy when the Git integration is enabled.

Function configuration includes the portable model and its embedded feature order. The deployment excludes notebook, training CSV, and legacy model files. Local, notebook, and test dependencies are in `requirements-dev.txt`.

## Local verification

From the repository root in PowerShell, using Python 3.12:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` after startup. The four entry points are `GET /`, `GET /health`, `GET /docs`, and `POST /predict`.

## Public verification and Postman

1. Open the production URL and its `/health` and `/docs` routes from a signed-out browser. Check that Swagger can reach the public API.
2. In Swagger, use the following notebook sample for `POST /predict`. The eight keys are listed in training order.

   ```json
   {
     "ALLSKY_SFC_SW_DWN": 0.0,
     "T2M": 27.7,
     "T2MDEW": 19.38,
     "RH2M": 60.49,
     "WS10M": 1.93,
     "Hour": 20,
     "Month": 4,
     "DayOfYear": 94
   }
   ```

   Expect HTTP 200 with a numeric `predicted_generation` near `178.7476348876953`. Omit a required field or provide an invalid type to check HTTP 422.
3. Import [the Postman collection](postman/solarizz.postman_collection.json). Set `base_url` to the public HTTPS origin without a trailing slash, and run the collection. Confirm seven requests and 14 assertions pass. The public Swagger URL is the college evaluation link once verified.

## Troubleshooting

Use Vercel build logs to diagnose dependency installation or function size errors. If startup fails, check runtime logs for missing portable model or incompatible Linux native libraries. If the deployment returns an authentication page, check deployment protection for this project's production domain before submitting it.

The model estimates generation using same-hour weather observations. The generation timestamp convention and physical target unit remain unverified.
