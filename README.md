# ExpenseHandler AI Agent

A simple Python + Streamlit expense management agent for a student project.

## Features
- Add income and expenses
- Suggest transaction categories using transparent keyword rules
- Set a monthly budget
- View monthly income, expenses, remaining budget, and transaction count
- Budget warnings and simple saving recommendations
- Category chart and monthly spending trend
- View transaction history and export it to CSV
- Save transactions locally in `expenses_data.json`

> **Important:** This is a learning prototype. The “AI” behavior is rule-based, not a trained machine-learning model or professional financial advice. For a class demo, use sample data. Do not store sensitive financial information on a public deployment. Local JSON persistence may not be reliable on hosted platforms such as Streamlit Community Cloud.

## Run on Windows
1. Install Python 3.11 or newer from https://www.python.org/downloads/ (enable **Add Python to PATH** during installation).
2. Extract this ZIP.
3. Open the extracted folder in File Explorer.
4. Click the address bar, type `cmd`, and press Enter.
5. Run:

```bash
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

If `py` is not recognized, try:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The app should open in your browser.

## Deploy online (demo)
1. Create a GitHub repository and upload `app.py`, `requirements.txt`, and `README.md`.
2. Open https://share.streamlit.io/
3. Sign in with GitHub, choose the repository and branch, and select `app.py` as the main file.
4. Deploy.

Avoid uploading real personal finance records. Hosted app file storage may reset or be shared depending on deployment setup.
