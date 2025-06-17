from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required
from datetime import datetime, date
from sqlalchemy import and_
from flask import request

from db import db
from AttendanceManagement.models import Attendance
from EmployeeManagement.models import Employee
from Authentication.models import Auth
from helpers import get_current_employee, get_filtered_attendance

attendance_ns = Namespace('attendance', description='Attendance management')

# Schemas
attendance_model = attendance_ns.model('Attendance', {
    'id': fields.Integer,
    'employee_id': fields.Integer,
    'date': fields.String,
    'clock_in_time': fields.String,
    'clock_out_time': fields.String,
    'total_hours': fields.Float,
    'status': fields.String
})

message_model = attendance_ns.model('Message', {
    'message': fields.String
})



@attendance_ns.route('/status')
class ClockStatus(Resource):
    @jwt_required()
    def get(self):
        claims = get_current_employee()
        today = date.today()
        record = Attendance.query.filter_by(employee_id=claims['emp_id'], date=today).first()
        if not record:
            return {'status': 'not_clocked_in'}, 200
        elif record.clock_out_time:
            return {'status': 'clocked_out'}, 200
        else:
            return {'status': 'clocked_in'}, 200


@attendance_ns.route('/clock-in')
class ClockIn(Resource):
    @jwt_required()
    def post(self):
        claims = get_current_employee()
        today = date.today()

        existing = Attendance.query.filter_by(employee_id=claims['emp_id'], date=today).first()
        if existing:
            return {'message': 'Already clocked in today.'}, 400

        attendance = Attendance(
            employee_id=claims['emp_id'],
            date=today,
            clock_in_time=datetime.now(),
            status='Present'
        )
        db.session.add(attendance)
        db.session.commit()
        return {'message': 'Clock-in successful'}, 200

@attendance_ns.route('/clock-out')
class ClockOut(Resource):
    @jwt_required()
    def post(self):
        claims = get_current_employee()
        today = date.today()

        attendance = Attendance.query.filter_by(employee_id=claims['emp_id'], date=today).first()
        if not attendance or attendance.clock_out_time:
            return {'message': 'Cannot clock out. Either not clocked in or already clocked out.'}, 400

        attendance.clock_out_time = datetime.now()
        delta = attendance.clock_out_time - attendance.clock_in_time
        attendance.total_hours = round(delta.total_seconds() / 3600, 2)
        db.session.commit()

        return {'message': 'Clock-out successful'}, 200




@attendance_ns.route('/my-attendance')
class MyAttendance(Resource):
    @jwt_required()
    def get(self):
        claims = get_current_employee()
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        day = request.args.get('day', type=int)

        queryset = Attendance.query.filter_by(employee_id=claims['emp_id'])
        records = get_filtered_attendance(queryset, year, month, day)

        if not records:
            return {'message': 'No attendance records found.'}, 200
        return marshal(records, attendance_model), 200




@attendance_ns.route('/department-attendance')
class DepartmentAttendance(Resource):
    @jwt_required()
    def get(self):
        claims = get_current_employee()
        if claims['emp_rank'] != 'manager':
            return {'message': 'Access denied'}, 403

        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        day = request.args.get('day', type=int)

        department_employees = Employee.query.filter_by(
            emp_department=claims['emp_department']
        ).with_entities(Employee.id)

        emp_ids = [emp.id for emp in department_employees]
        queryset = Attendance.query.filter(Attendance.employee_id.in_(emp_ids))
        records = get_filtered_attendance(queryset, year, month, day)

        if not records:
            return {'message': 'No attendance records found for department.'}, 200
        return marshal(records, attendance_model), 200





@attendance_ns.route('/all-attendance')
class AllAttendance(Resource):
    @jwt_required()
    def get(self):
        claims = get_current_employee()
        if claims['emp_rank'] != 'admin' or claims['emp_department'] != 'Human Resource':
            return {'message': 'Access denied'}, 403

        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        day = request.args.get('day', type=int)

        queryset = Attendance.query
        records = get_filtered_attendance(queryset, year, month, day)

        if not records:
            return {'message': 'No attendance records found.'}, 200
        return marshal(records, attendance_model), 200




@attendance_ns.route('/employee/<int:id>/attendance')
class AttendanceByID(Resource):
    @jwt_required()
    def get(self, id):
        claims = get_current_employee()
        if claims['emp_rank'] != 'admin' or claims['emp_department'] != 'Human Resource':
            return {'message': 'Access denied'}, 403

        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        day = request.args.get('day', type=int)

        queryset = Attendance.query.filter_by(employee_id=id)
        records = get_filtered_attendance(queryset, year, month, day)

        if not records:
            return {'message': 'No attendance records found for employee.'}, 200
        return marshal(records, attendance_model), 200



