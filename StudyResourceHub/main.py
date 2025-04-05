from app import app

# This variable is used by Vercel/WSGI to locate the application
application = app

if __name__ == "__main__":
    # For local development only - production will use WSGI server
    debug_mode = app.config.get('DEBUG', False)
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)
