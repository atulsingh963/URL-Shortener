# Shortly — URL Shortener

Shortly is a lightweight, production-quality URL shortening web service built with Python, Flask, and SQLite. It provides an intuitive interface to convert long URLs into compact, shareable links, track click analytics, and offer a simple REST API interface.

---

## Features

- **Instant URL Shortening**: Convert long URLs into 6-character alphanumeric links.
- **Strict Validation**: Validates URLs ensuring valid scheme (`http://` or `https://`) and domain structure before storing.
- **Collision-Free Code Generation**: Generates unique short codes guaranteed never to overwrite existing links.
- **Click Tracking & Analytics**: Automatically increments click counts on every redirection and provides detailed link statistics (`/stats/<short_code>`).
- **One-Click Copy**: Built-in Clipboard API support with temporary UI feedback.
- **REST API**: Simple JSON endpoints for programmatic URL shortening and stats retrieval.
- **Custom Error Handling**: Clean HTML 404/500 error pages and structured JSON error responses for API calls.
- **Modern Minimal UI**: Dark-themed, responsive design built with CSS variables and clean typography.

---

## Tech Stack

- **Backend**: Python 3, Flask
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3 (Vanilla CSS), JavaScript (Vanilla JS)

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd URL-Shortener
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - **Linux/macOS**:
     ```bash
     source venv/bin/activate
     ```
   - **Windows**:
     ```cmd
     venv\Scripts\activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Run

To launch the application locally:

```bash
python app.py
```

Then open your browser and visit:

```
http://127.0.0.1:5000
```

The database (`data/shortly.db`) and table structure will be created automatically on application start.

---

## API Documentation

### 1. Shorten a URL
- **Endpoint**: `POST /api/shorten`
- **Headers**: `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "url": "https://example.com/very/long/url"
  }
  ```
- **Response (HTTP 201 Created)**:
  ```json
  {
    "success": true,
    "original_url": "https://example.com/very/long/url",
    "short_url": "http://127.0.0.1:5000/Ab3xK9",
    "short_code": "Ab3xK9"
  }
  ```
- **Error Response (HTTP 400 Bad Request)**:
  ```json
  {
    "success": false,
    "error": "Invalid URL. Please provide a valid http:// or https:// link."
  }
  ```

---

### 2. Get Link Statistics
- **Endpoint**: `GET /api/stats/<short_code>`
- **Response (HTTP 200 OK)**:
  ```json
  {
    "success": true,
    "short_code": "Ab3xK9",
    "original_url": "https://example.com/very/long/url",
    "click_count": 12,
    "created_at": "2026-08-20 21:16:07"
  }
  ```
- **Error Response (HTTP 404 Not Found)**:
  ```json
  {
    "success": false,
    "error": "Short code not found"
  }
  ```

---

## Project Structure

```
Url-Shortener/
│
├── app.py              # Flask app routes, API endpoints, URL validation & error handlers
├── database.py         # SQLite connection, database initialization & CRUD helper functions
├── requirements.txt    # Application dependencies
├── README.md           # Documentation
├── .gitignore          # Git ignore file (excludes venv, SQLite database, pycache)
│
├── templates/
│   ├── index.html      # Landing page template
│   ├── stats.html      # Statistics & analytics page template
│   ├── 404.html        # Custom 404 Not Found page
│   └── 500.html        # Custom 500 Server Error page
│
├── static/
│   ├── css/
│   │   └── style.css   # Main stylesheet with CSS variables & responsive design
│   └── js/
│       └── script.js    # Frontend JavaScript for AJAX requests & Clipboard API
│
└── data/
    └── .gitkeep        # Directory for SQLite database storage
```
