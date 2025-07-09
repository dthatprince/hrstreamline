from datetime import date
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt

from db import db
from extensions import bcrypt, blacklist
from Authentication.models import Auth
from EmployeeManagement.models import Employee
from helpers import get_current_employee, get_employee_by_id  

employee_ns = Namespace('employees', description='Employee related operations')

message_model = employee_ns.model('Message', {
    'message': fields.String(description='Response message')
})

# Response model
employee_model = employee_ns.model('Employee', {
    'id': fields.Integer,
    'email': fields.String,
    'first_name': fields.String,
    'last_name': fields.String,
    'phone_no': fields.String,
    'gender': fields.String,
    'address': fields.String,
    'country': fields.String,
    'emp_department': fields.String,
    'emp_team': fields.String,
    'emp_position': fields.String,
    'emp_rank': fields.String,
    'emp_leave_balance': fields.Float,
    'emp_start_date': fields.String,
    'emp_end_date': fields.String,
    'emp_status': fields.String,
    'emp_work_status': fields.String
})

# update personal profile model
update_model = employee_ns.model('UpdateProfile', {
    'first_name': fields.String,
    'last_name': fields.String,
    'phone_no': fields.String,
    'gender': fields.String,
    'address': fields.String,
    'country': fields.String
})

# HR update employee model
hr_update_model = employee_ns.model('HRUpdate', {
    'emp_department': fields.String,
    'emp_team': fields.String,
    'emp_position': fields.String,
    'emp_rank': fields.String,
    #'emp_end_date': fields.String,
    #'emp_status': fields.String
})



# View Personal Profile
@employee_ns.route('/myaccount')
class MyProfile(Resource):
    @employee_ns.doc(
        description="Get the current employee's profile."
    )
    @jwt_required()
    @employee_ns.marshal_with(employee_model)
    def get(self):
        claims = get_current_employee()
        emp = get_employee_by_id(claims['emp_id'])
        if not emp:
            return {'message': 'Employee profile not found.'}, 404
        return emp

# Update Personal Profile
@employee_ns.route('/myaccount/update')
class UpdateMyProfile(Resource):
    @employee_ns.doc(
        description="Update the current employee's profile."
    )
    @jwt_required()
    @employee_ns.expect(update_model)
    def put(self):
        claims = get_current_employee()
        emp = get_employee_by_id(claims['emp_id'])
        if not emp:
            return {'message': 'Employee profile not found.'}, 404
        
        data = employee_ns.payload
        for field in update_model.keys():
            if field in data:
                setattr(emp, field, data[field])
        db.session.commit()
        return {'message': 'Profile updated successfully'}



# View All Employees
@employee_ns.route('/')
class AllEmployees(Resource):
    @employee_ns.doc(
        description="Get a list of all employees."
    )
    @jwt_required()
    @employee_ns.marshal_list_with(employee_model)
    def get(self):
        emp = get_current_employee()
        if not emp:
            return {'message': 'Employee not found.'}, 404

        if emp['emp_rank'] == 'admin' and emp['emp_department'] == 'Human Resource':
            return Employee.query.all()
        elif emp['emp_rank'] == 'manager':
            return Employee.query.filter_by(emp_department=emp['emp_department']).all()
        else:
            return {'message': 'Access denied'}, 403



# Get Employee Information by ID
@employee_ns.route('/<int:id>')
class GetEmployee(Resource):
    @employee_ns.doc(
        description="Get information about a specific employee."
    )
    @jwt_required()
    #@employee_ns.marshal_with(employee_model)
    def get(self, id):
        emp = get_current_employee()
        target_emp = get_employee_by_id(id)

        if not target_emp:
            return {'message': 'Employee not found'}, 404

        if emp['emp_rank'] == 'admin' and emp['emp_department'] == 'Human Resource':
            return employee_ns.marshal(target_emp, employee_model)
        elif emp['emp_rank'] == 'manager' and emp['emp_department'] == target_emp.emp_department:
            return employee_ns.marshal(target_emp, employee_model)
        else:
            return {'message': 'Access denied'}, 403


# Update Employee Information
@employee_ns.route('/<int:id>/update')
class HRUpdate(Resource):
    @employee_ns.doc(
        description="Update employee information by id."
    )
    @jwt_required()
    @employee_ns.expect(hr_update_model)
    def put(self, id):
        emp = get_current_employee()
        target_emp = get_employee_by_id(id)

        if not target_emp:
            return {'message': 'Employee not found'}, 404

        if not (emp['emp_rank'] == 'admin' and emp['emp_department'] == 'Human Resource'):
            return {'message': 'Access denied'}, 403

        data = employee_ns.payload
        for field in hr_update_model.keys():
            if field in data:
                setattr(target_emp, field, data[field])
        db.session.commit()
        return {'message': 'Employee record updated successfully'}



# Terminate Employee
@employee_ns.route('/<int:id>/terminate')
class TerminateEmployee(Resource):
    @employee_ns.doc(
        description="Terminate an employee by id."
    )
    @jwt_required()
    def put(self, id):
        emp = get_current_employee()
        target_emp = get_employee_by_id(id)

        if not target_emp:
            return {'message': 'Employee not found'}, 404

        if not (emp['emp_rank'] == 'admin' and emp['emp_department'] == 'Human Resource'):
            return {'message': 'Access denied'}, 403

        target_emp.emp_status = 'Terminated'
        target_emp.emp_end_date = date.today().isoformat()
        db.session.commit()
        return {'message': f'Employee {target_emp.first_name} {target_emp.last_name} terminated successfully'}
