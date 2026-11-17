# Backend setup

1. Create a developer account at [Adzuna](https://developer.adzuna.com/signup)
   and obtain an app ID and app key.
2. Copy `.env.example` to `.env` in this folder and fill in the credentials:

   ```text
   ADZUNA_APP_ID=your_app_id
   ADZUNA_APP_KEY=your_app_key
   ```

   Keep `.env` private; it is excluded from version control.
3. Install dependencies and start the API from this folder:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv\Scripts\python.exe app.py
   ```

Live job searches use Adzuna's India job listings. Profile photos and job-search
locations are stored locally in the application's SQLite database.

After adding credentials, restart `app.py`. Sign in to the dashboard, choose a
profile photo, save your city or postal code, then search for a role and use
**View job & apply** to continue to the listing on Adzuna.
