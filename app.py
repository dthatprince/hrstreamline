from flask import Flask
from flask_restx import Api
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import DevelopmentConfig
from db import db
from extensions import bcrypt, is_token_revoked
import extensions as security_utils


from Authentication.routes import auth_ns



def create_app():
    app = Flask(__name__)

    # Load configurations
    app.config.from_object(DevelopmentConfig())

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app) # Initialize the app with bcrypt
    jwt = JWTManager(app) #Initialize app with JWT
    migrate = Migrate(app, db) # Initialize Flask-Migrate 

    # Register token revocation callback
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return is_token_revoked(jwt_header, jwt_payload)
    
    
    # Initialize Flask-RESTX Api with Swagger docs on /docs - http://127.0.0.1:5000/docs
    api = Api(app, version='1.0', title='HR Streamline API', description='API documentation')
    
    # Register the auth namespace
    api.add_namespace(auth_ns)

    return app


app = create_app()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)