from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify
from pydantic import ValidationError as PydanticValidationError
from lib.db import init_db, seed_db, close_db
from lib.errors import NotFoundError
from lib.constants import HTTP_BAD_REQUEST, HTTP_NOT_FOUND, HTTP_INTERNAL_ERROR


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates")

    # Initialize database and seed with sample data
    with app.app_context():
        init_db()
        seed_db()

    # Register error handlers
    @app.errorhandler(NotFoundError)
    def handle_not_found(e):
        return jsonify({"error": e.message}), HTTP_NOT_FOUND

    @app.errorhandler(PydanticValidationError)
    def handle_validation(e):
        return jsonify({"error": "Validation failed", "details": e.errors()}), HTTP_BAD_REQUEST

    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({"error": "Not found"}), HTTP_NOT_FOUND

    @app.errorhandler(Exception)
    def handle_generic(e):
        return jsonify({"error": "Internal server error"}), HTTP_INTERNAL_ERROR

    # Register blueprints
    from routes.views import bp as views_bp
    from routes.auth import bp as auth_bp
    from routes.section import bp as section_bp
    from routes.product import bp as product_bp
    from routes.chat import bp as chat_bp

    app.register_blueprint(views_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(section_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(chat_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=8000)
