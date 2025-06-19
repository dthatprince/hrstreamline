from datetime import date, timedelta
from flask_restx import Namespace, Resource, fields  # API documentation
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from db import db
from extensions import bcrypt, blacklist
from Authentication.models import Auth
from EmployeeManagement.models import Employee
from flask import jsonify


auth_ns = Namespace('authentication', description='Authentication related operations')



register_model = auth_ns.model('Register', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
    'first_name': fields.String(required=True, description='First name'),
    'last_name': fields.String(required=True, description='Last name'),
    'phone_no': fields.String(description='Phone number'),
    'gender': fields.String(description='Gender'),
    'address': fields.String(description='Address'),
    'country': fields.String(description='Country'),
})

login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
})

token_model = auth_ns.model('Token', {
    'access_token': fields.String(description='JWT Access Token')
})

message_model = auth_ns.model('Message', {
    'message': fields.String(description='Response message')
})



   
@auth_ns.route('/home')
class Home(Resource):
    @auth_ns.doc(
        description="Home endpoint for authenticated users."
    )
    @jwt_required()
    def get(self):
        return {"message": "API is working!"}

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.doc(
        description="Registers a new user."
    )
    @auth_ns.expect(register_model)
    @auth_ns.response(201, 'User registered successfully', model=message_model)
    @auth_ns.response(400, 'User already exists', model=message_model)
    def post(self):
        data = auth_ns.payload
        if Auth.query.filter_by(email=data['email']).first():
            return {"message": "User already exists"}, 400

        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        auth = Auth(email=data['email'], password_hash=hashed_password)
        db.session.add(auth)
        db.session.flush()

        employee = Employee(
            auth_id=auth.id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_no=data.get('phone_no'),
            gender=data.get('gender'),
            address=data.get('address'),
            country=data.get('country'),
            emp_department=None,  # or 'Unassigned'
            emp_team=None,
            emp_position=None,
            emp_rank=None,
            emp_leave_balance=0.0,  
            emp_start_date=date.today(),
            emp_end_date=None,
            emp_status="Active",
            emp_work_status="In office"
        )
        db.session.add(employee)
        db.session.commit()

        return {"message": "User registered successfully"}, 201


@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.doc(
        description="Logs in a user and returns a JWT token."
    )
    @auth_ns.expect(login_model)
    @auth_ns.response(200, 'Success', model=token_model)
    @auth_ns.response(401, 'Invalid email or password', model=message_model)
    @auth_ns.response(403, 'Access forbidden: Terminated employee', model=message_model)
    def post(self):
        data = auth_ns.payload
        auth = Auth.query.filter_by(email=data['email']).first()
        
        if not auth or not bcrypt.check_password_hash(auth.password_hash, data['password']):
            return {"message": "Invalid email or password"}, 401

        employee = Employee.query.filter_by(auth_id=auth.id).first()
        
        # Check for terminated status
        if employee and employee.emp_status == "Terminated":
            return {"message": "Access forbidden: Your account has been terminated"}, 403

        access_token = create_access_token(
            identity=auth.email,
            additional_claims={
                'auth_id': auth.id,
                'emp_id': employee.id,
                'emp_rank': employee.emp_rank if employee else None,
                'emp_department': employee.emp_department if employee else None,
                'full_name': f"{employee.first_name} {employee.last_name}",
                "emp_status": employee.emp_status if employee else None
            },
            # expires_delta=timedelta(hours=2)
        )
        return {"access_token": access_token}, 200



@auth_ns.route('/logout')
class Logout(Resource):
    @auth_ns.doc(
        description="Logs out the user by invalidating the JWT token."
    )
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        blacklist.add(jti)
        return {"msg": "Successfully logged out"}, 200