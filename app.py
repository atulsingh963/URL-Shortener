import secrets
import string
from urllib.parse import urlparse
from flask import Flask, render_template, request, redirect, jsonify, abort
import database as db

app = Flask(__name__)

# Automatically initialize database table on app startup
db.init_db()


def is_valid_url(url: str) -> bool:
    """
    Validates that a URL is non-empty, uses http or https scheme,
    and has a valid netloc (domain).
    """
    if not url or not isinstance(url, str):
        return False

    url = url.strip()
    if len(url) > 2048:
        return False

    try:
        parsed = urlparse(url)
        # Only allow http and https schemes
        if parsed.scheme not in ("http", "https"):
            return False
        # Domain/host must be present
        if not parsed.netloc:
            return False
        return True
    except Exception:
        return False


def generate_unique_short_code(length: int = 6) -> str:
    """Generates a random 6-character alphanumeric code guaranteed to be unique in DB."""
    alphabet = string.ascii_letters + string.digits
    for _ in range(100):
        code = "".join(secrets.choice(alphabet) for _ in range(length))
        if not db.code_exists(code):
            return code
    raise RuntimeError("Failed to generate a unique short code after maximum attempts.")


@app.route("/")
def index():
    """Renders the main landing page."""
    return render_template("index.html")


@app.route("/api/shorten", methods=["POST"])
def api_shorten():
    """
    API endpoint to shorten a URL.
    Accepts JSON body or Form data with a 'url' field.
    Returns HTTP 201 Created on success, HTTP 400 Bad Request on invalid input.
    """
    data = request.get_json(silent=True) or request.form
    raw_url = data.get("url") if data else None

    if not raw_url:
        return jsonify({"success": False, "error": "URL is required"}), 400

    raw_url = raw_url.strip()

    if not is_valid_url(raw_url):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Invalid URL. Please provide a valid http:// or https:// link.",
                }
            ),
            400,
        )

    try:
        short_code = generate_unique_short_code()
        db.create_url(raw_url, short_code)
        
        # Build base URL dynamically from request
        host_url = request.host_url.rstrip("/")
        short_url = f"{host_url}/{short_code}"

        return (
            jsonify(
                {
                    "success": True,
                    "original_url": raw_url,
                    "short_url": short_url,
                    "short_code": short_code,
                }
            ),
            201,
        )
    except Exception as e:
        app.logger.error(f"Error creating short URL: {e}")
        return (
            jsonify({"success": False, "error": "Failed to shorten URL due to a server error."}),
            500,
        )


@app.route("/api/stats/<short_code>", methods=["GET"])
def api_stats(short_code):
    """API endpoint to retrieve URL statistics."""
    stats = db.get_stats(short_code)
    if not stats:
        return jsonify({"success": False, "error": "Short code not found"}), 404

    return jsonify(
        {
            "success": True,
            "short_code": stats["short_code"],
            "original_url": stats["original_url"],
            "click_count": stats["click_count"],
            "created_at": str(stats["created_at"]),
        }
    )


@app.route("/stats/<short_code>")
def stats_page(short_code):
    """HTML page displaying statistical metadata for a shortened link."""
    stats = db.get_stats(short_code)
    if not stats:
        return render_template("404.html"), 404

    host_url = request.host_url.rstrip("/")
    short_url = f"{host_url}/{short_code}"

    return render_template(
        "stats.html",
        stats=stats,
        short_url=short_url,
    )


@app.route("/<short_code>")
def redirect_to_url(short_code):
    """
    Redirects the short code to the original URL if found,
    and increments the click count.
    """
    # Exclude static routes if any fallthrough occurs
    if short_code in ("favicon.ico", "robots.txt"):
        abort(404)

    record = db.get_url_and_increment_clicks(short_code)
    if not record:
        return render_template("404.html"), 404

    return redirect(record["original_url"])


@app.errorhandler(404)
def not_found_error(error):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Resource not found"}), 404
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Internal server error"}), 500
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
