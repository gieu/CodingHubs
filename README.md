# Coding Hubs 2025

## Instalation

1. Clone the repo

   ```bash
   
   ```

2. Install the packages

   ```bash
   pip install -r requirements.txt
   ```

3. Get the gsheet credentials: `gsheet-credentials.json`

Recomended but not mandatory: create a virtual env.

```bash
python -m venv venv
venv\Scripts\activate
```

This is particullary helpfull as we will deploy this on a server (sometimes we may use a package is installed globally, but it's not in the `requirements.txt`file).

## Running the thing

Locally

```bash
streamlit run app.py
```

