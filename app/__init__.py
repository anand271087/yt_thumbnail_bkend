from flask import Flask
from app.services import setup_routes
from flask_cors import CORS 

def create_app():
    app = Flask(__name__)
    # Enable CORS for Netlify frontend
    #CORS(app, origins=["https://symphonious-empanada-1fa992.netlify.app"])

    # Or allow all origins temporarily (for testing)
    CORS(app)
    setup_routes(app)
    return app
