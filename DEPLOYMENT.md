# Verify and share the SolaRizz API

## Start FastAPI on Windows

Open PowerShell in the cloned repository. Update the checkout and use the existing virtual environment. If you created the environment under Local AppData, use the alternate Python path shown below.

```powershell
git pull --ff-only origin main
$python = '.\.venv\Scripts\python.exe'
# Alternate path for the venv outside OneDrive
# $python = Join-Path $env:LOCALAPPDATA 'SOLRIZ\venv\Scripts\python.exe'
& $python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

After startup completes, visit `http://127.0.0.1:8000/docs`. Keep this window open.

## Open an HTTPS tunnel with ngrok

1. Sign in or create an ngrok account. Follow the Windows installation instructions in the [ngrok dashboard](https://dashboard.ngrok.com/get-started/setup/windows). With Windows Package Manager, use `winget install --id Ngrok.Ngrok --exact`.
2. Open a second PowerShell window. Copy the authtoken command from the ngrok dashboard and run it on your computer. The command has the form `ngrok config add-authtoken <YOUR_AUTHTOKEN>`. Keep the token out of chat and Git.
3. Run `ngrok http 8000`. Copy the **HTTPS** forwarding URL. Keep both PowerShell windows open.
4. Open the public URL with `/docs` appended in a signed-out browser. If ngrok displays its browser interstitial, continue to the site. The Postman collection sends the ngrok interstitial bypass header.

An ngrok tunnel forwards traffic to your running laptop. The URL stops serving the API if FastAPI, ngrok, or the internet connection stops, or if the laptop sleeps or shuts down. Persistent hosting is required if the college needs access with the laptop off.

## Run the Postman collection

1. In Postman, click **Import** and select [postman/solarizz.postman_collection.json](postman/solarizz.postman_collection.json).
2. To test locally, leave the collection variable `base_url` at `http://127.0.0.1:8000`. To test publicly, set it to the HTTPS ngrok forwarding address without a trailing slash.
3. Select **Run collection**, then **Run SolaRizz API Verification**. All seven requests and 14 assertions should pass. The notebook sample should return `178.7476348876953` within a tolerance of `0.000001`. The prediction unit is unverified.
4. Save a screenshot of the public run for submission. Confirm the public `/docs` page on a different connection if available, and submit the working HTTPS base URL.
