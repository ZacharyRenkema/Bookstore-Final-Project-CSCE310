# app.py
from flask import Flask
from flask_bcrypt import Bcrypt
from models import db
import config

bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)

    # Database config
    app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["SECRET_KEY"] = config.KEY      
    app.config["JWT_SECRET"] = config.JWT      

    # Init extensions
    db.init_app(app)
    bcrypt.init_app(app)

    # Register blueprints
    from auth import auth_bp
    from books import books_bp
    from orders import orders_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(books_bp, url_prefix="/books")
    app.register_blueprint(orders_bp, url_prefix="/orders")

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()   
    app.run(debug=True)
