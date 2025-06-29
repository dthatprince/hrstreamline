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
            """
A Human Resource Management System (HRMS) designed to streamline core HR processes 
and improve employee management within organizations. This system focuses on managing employee data, 
tracking leave requests, and automating essential HR tasks to enhance operational efficiency and employee experience.

# 🗂️ Leave Management API – User Roles & Test Accounts

## 👥 User Roles & Permissions

| **Role**   | **Department**      | **Permissions** |
|------------|---------------------|------------------|
| 🧑‍💼 **Staff**    | Any                 | - Submit leave requests<br>- View own leave history<br>- Edit/delete own pending requests<br>- Check leave balance<br>- Mark self as on leave |
| 👨‍💼 **Manager**  | e.g., Engineering   | - All **Staff** permissions<br>- View & approve/reject pending requests **in their department**<br>- Cannot approve Admins or users outside their department |
| 🧑‍💼 **Admin (HR)** | Human Resource     | - All **Staff** permissions<br>- View all pending requests across departments<br>- Approve/reject any **Staff** and **Manager** leave requests<br>- Cannot approve/reject other Admins<br>- Final authority in approval workflow |

---

## 🔑 Test User Accounts

### 🧑‍💼 Staff – Engineering
```json
{
  "email": "cristiano.ronaldo@cr7.com",
  "password": "Password123!"
}
```

### 🧑‍💼 Staff – Research
```json
{
  "email": "burna.boy@example.com",
  "password": "afrobeatKing2024"
}
```

### 🧑‍💼 Staff – Sales
```json
{
  "email": "antoine.griezmann@example.com",
  "password": "anotherPass789"
}
```

---

### 👨‍💼 Manager – Engineering
```json
{
  "email": "messi.leo@goat.com",
  "password": "MessiRocks10!"
}
```

---

### 🧑‍💼 Admin (HR)
```json
{
  "email": "serena.williams@tennis.com",
  "password": "SerenaPower23!"
}
```

## 🔐 Authorize with Token

After logging in and receiving your access token, click the **Authorize** padlock icon on the top right and paste your token in the following format:

```
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MTE1ODMxMSwianRpIjoiNzBlMTYzNGEtZTIyMS00YWRmLTlkMWItZDc0ODRhNmFkMTM4Iiw
```

---

## ✅ Role Permissions Matrix

| **Action**                       | **Staff** | **Manager** | **Admin** |
|----------------------------------|-----------|-------------|-----------|
| Submit leave request             | ✅        | ✅          | ✅        |
| View own leave history           | ✅        | ✅          | ✅        |
| Edit/delete own pending request | ✅        | ✅          | ✅        |
| View leave balance               | ✅        | ✅          | ✅        |
| View department leave requests   | ❌        | ✅          | ✅        |
| Approve/reject department leaves | ❌        | ✅          | ✅        |
| View all leave requests          | ❌        | ❌          | ✅        |
| Approve/reject Admin requests    | ❌        | ❌          | ❌        |
"""
        
        
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