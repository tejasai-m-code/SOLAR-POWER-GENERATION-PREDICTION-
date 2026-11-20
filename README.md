# SolaRizz — Solar Power Generation Prediction and Performance Deviation Analysis

SolaRizz estimates generation from five same-hour weather observations and three calendar features. The notebook compares regressors using chronological splits and selects a model by validation MAE. The generation column is labeled `Solar (MW)` in the source CSV, and its physical unit remains unverified.

## Run the API

Use Python 3.12. From the repository root, install the pinned dependencies and start the app.

```sh
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app
```

Open Swagger at `http://127.0.0.1:8000/docs`. The service loads the saved XGBoost model at startup. Use `GET /` for API information, `GET /health` for health, and `POST /predict` for predictions. Run the API tests with `python -m pytest -q`.

## Publish the notebook on Kaggle

The original research notebook is [code.ipynb](code.ipynb). Use [kaggle/solarizz.ipynb](kaggle/solarizz.ipynb) for submission. It reads Kaggle inputs, trains the models, displays validation and holdout metrics, and verifies its saved model.

1. Sign in at [Kaggle](https://www.kaggle.com/). Under **Datasets**, create a dataset and upload the two original CSVs from this repository:
   - `POWER_Point_Hourly_20240101_20250624_017d39N_078d49E_LST.csv`
   - `solar_ready.csv`
   Start with a private dataset. Confirm your permission to redistribute the generation data before making the dataset public or exposing its data through public notebook outputs.
2. Create a **New Notebook** under **Code**. Import `kaggle/solarizz.ipynb` using the notebook editor's import option and set the title to **SolaRizz | Solar Power Generation Prediction Using Machine Learning**.
3. In the notebook's **Add Input** panel, find and attach your dataset. The notebook finds both CSVs under `/kaggle/input` by their original filenames. Keep one attached copy of each file.
4. Run all cells in a Python CPU session. Check the split counts, model comparison table, holdout metrics, and exact prediction match after reload. If a required import fails, install that package in the notebook session and restart it. The tested reference dependencies are pinned in `requirements-dev.txt`.
5. Click **Save Version**, choose **Save & Run All**, and wait for the run to complete. Check the saved version's output before changing visibility.
6. Use **Share** or the notebook visibility setting to make the notebook public. If Kaggle requires public input access for reproducibility, review the dataset's sharing permissions before changing its visibility.
7. Copy the saved notebook's URL and open it in a signed-out or private browser window to confirm that a reviewer can access it. Use that URL for your submission.
