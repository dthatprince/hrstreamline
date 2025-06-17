from flask_jwt_extended import get_jwt
from db import db
from EmployeeManagement.models import Employee
from AttendanceManagement.models import Attendance



# Helper function to get current employee claims from JWT
def get_current_employee():
    claims = get_jwt()
    return {
        'emp_id': claims.get('emp_id'),
        'emp_rank': claims.get('emp_rank'),
        'emp_department': claims.get('emp_department')
    }


# Helper function to get employee by ID
def get_employee_by_id(emp_id):
    return Employee.query.filter_by(id=emp_id).first()


# Helper function to filter attendance records
def get_filtered_attendance(queryset, year, month, day):
    if year:
        queryset = queryset.filter(db.extract('year', Attendance.date) == int(year))
    if month:
        queryset = queryset.filter(db.extract('month', Attendance.date) == int(month))
    if day:
        queryset = queryset.filter(db.extract('day', Attendance.date) == int(day))
    results = queryset.order_by(Attendance.date.desc()).all()
    return results

'''
def get_filtered_attendance(queryset, year, month, day):
    if year:
        queryset = queryset.filter(db.extract('year', Attendance.date) == int(year))
    if month:
        queryset = queryset.filter(db.extract('month', Attendance.date) == int(month))
    if day:
        queryset = queryset.filter(db.extract('day', Attendance.date) == int(day))
    return queryset.order_by(Attendance.date.desc()).all()
'''
