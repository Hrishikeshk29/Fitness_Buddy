"""
=============================================================================
FITNESS BUDDY - MAIN FLASK APPLICATION
=============================================================================
Entry point for the Agentic AI Fitness Buddy powered by IBM Granite / watsonx.ai
=============================================================================
"""

import os
from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS

from config import Config
from models.models import db, User
from routes.auth_routes import auth_bp
from routes.main_routes import main_bp
from routes.chat_routes import chat_bp


def create_app(config_class=Config) -> Flask:
    """Application factory."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Extensions
    db.init_app(app)
    CORS(app)

    # Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access Fitness Buddy."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id: str):
        return User.query.get(int(user_id))

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(chat_bp)

    # Create all tables
    with app.app_context():
        db.create_all()

    return app


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
app = create_app()

if __name__ == "__main__":
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() == "true"
    app.run(host=host, port=port, debug=debug)
