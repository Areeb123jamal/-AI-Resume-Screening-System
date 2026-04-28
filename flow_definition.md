# Screenshots

This folder contains screenshots of the AI Resume Screening System API in action.

| File | Description |
|------|-------------|
| `api_running.png` | Flask development server running in terminal |
| `open_browser.png` | Browser showing the `/` health-check endpoint |
| `output.png` | Postman showing `POST /match` response with match score |

## How to capture your own screenshots

1. Run the server: `python app.py`
2. Open Postman and send `POST http://127.0.0.1:5000/match` with the sample body
3. Screenshot the 200 OK response showing `match_score`
