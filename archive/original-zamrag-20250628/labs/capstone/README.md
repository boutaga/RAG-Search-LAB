# Capstone Search App

This example combines the existing `chatbotUI` backend with a simple Streamlit interface.

## Prerequisites

- Python packages: `flask`, `flask-cors`, `openai`, `psycopg2-binary`, `streamlit`, `requests`
- Environment variables:
  - `DATABASE_URL` – connection string for PostgreSQL
  - `OPENAI_API_KEY` – your OpenAI API key

## Running the Backend

Start the Flask service (provides the `/search` endpoint used by the UI):

```bash
python chatbotUI/app.py
```

## Running the Streamlit Frontend

In a separate terminal run:

```bash
streamlit run labs/capstone/app.py
```

The app shows a search box and lets you choose the mode. Results are paginated and you can filter by title.

Make sure the backend is accessible at `http://localhost:5000/search` or adjust the URL in the sidebar of the Streamlit app.
