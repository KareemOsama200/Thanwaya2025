from flask import Flask
from app import app

# This is needed for WSGI servers
application = app

# This is needed for Vercel serverless functions
def handler(request, context):
    """Vercel serverless entry point"""
    return app