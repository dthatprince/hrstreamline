from celery_worker import celery
from db import db
from EmployeeManagement.models import Employee
from datetime import date
from celery.schedules import crontab

from LeaveManagement.models import LeaveRequest, LeaveStatusEnum
from EmployeeManagement.models import Employee

# Import the factory and create app
from app import create_app

app = create_app()  # Create the app instance

@celery.task(name="tasks.accrual.monthly_accrual")
def monthly_accrual():
    with app.app_context():
        today = date.today()
        employees = Employee.query.filter(Employee.emp_status == 'Active').all()

        for emp in employees:
            if emp.emp_start_date:
                months_worked = (today.year - emp.emp_start_date.year) * 12 + (today.month - emp.emp_start_date.month)
                expected_balance = months_worked * 2

                if emp.emp_leave_balance is None or emp.emp_leave_balance < expected_balance:
                    emp.emp_leave_balance = expected_balance

        db.session.commit()
        print("Leave accrual completed.")


@celery.task(name="tasks.leave.end_leave_status_check")
def end_leave_status_check():
    today = date.today()

    # Get all employees currently on leave
    on_leave_employees = Employee.query.filter_by(emp_work_status='on leave').all()

    for emp in on_leave_employees:
        # Get the most recent approved leave
        recent_leave = LeaveRequest.query.filter_by(
            employee_id=emp.id,
            status=LeaveStatusEnum.APPROVED
        ).order_by(LeaveRequest.end_date.desc()).first()

        if recent_leave and recent_leave.end_date < today:
            emp.emp_work_status = 'in office'

    db.session.commit()
    print("Checked and updated leave end statuses.")