from flask import Flask
from flask_restx import Api
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import DevelopmentConfig
from db import db
from extensions import bcrypt, is_token_revoked
import extensions as security_utils


from Authentication.routes import auth_ns
from EmployeeManagement.routes import employee_ns
from AttendanceManagement.routes import attendance_ns
from LeaveManagement.routes import leave_ns


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
    
    
    # Initialize Flask-RESTX Api with Swagger docs on /docs - http://127.0.0.1:5000/
    api = Api(
      app,
      version='1.0',
      title='HR Streamline API - API documentation',
      description=(
        'A Human Resource Management System (HRMS) designed to streamline core HR processes '
        'and improve employee management within organizations. This system focuses on managing employee data, '
        'tracking leave requests, and automating essential HR tasks to enhance operational efficiency and employee experience.\n\n'
        'To get login account access and access control documentation, visit the <a href="https://github.com/dthatprince/hrstreamline/blob/postgresql-version/docs.md" target="_blank">Testing Docs</a>.'
      ),
      security='Bearer',
      authorizations={
        'Bearer': {
          'type': 'apiKey',
          'in': 'header',
          'name': 'Authorization',
          'description': 'JWT token with `Bearer <JWT>` format'
        }
      }
    )
    
    # Register the auth namespace
    api.add_namespace(auth_ns)
    api.add_namespace(employee_ns)
    api.add_namespace(attendance_ns)
    api.add_namespace(leave_ns)

    return app


app = create_app()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)