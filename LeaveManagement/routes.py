from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from flask import request
from datetime import datetime

from db import db
from LeaveManagement.models import LeaveRequest, LeaveStatusEnum
from EmployeeManagement.models import Employee
from helpers import get_current_employee  

leave_ns = Namespace('leave', description='Leave management')

# Response and request schemas
leave_request_model = leave_ns.model('LeaveRequest', {
    'id': fields.Integer,
    'employee_id': fields.Integer,
    'leave_type': fields.String(enum=['Annual', 'Sick', 'Personal', 'Emergency']),
    'start_date': fields.String,
    'end_date': fields.String,
    'days_requested': fields.Float,
    'reason': fields.String,
    'status': fields.String(enum=['Pending', 'Approved', 'Rejected']),
    'approved_by': fields.Integer,
    'approved_at': fields.String,
    'rejection_reason': fields.String
})

request_input_model = leave_ns.model('RequestInput', {
    'leave_type': fields.String(required=True),
    'start_date': fields.String(required=True),
    'end_date': fields.String(required=True),
    'reason': fields.String(required=True)
})

status_update_model = leave_ns.model('StatusUpdate', {
    'rejection_reason': fields.String(required=False)
})




# Routes
@leave_ns.route('/request')
class LeaveRequestSubmit(Resource):
    @leave_ns.doc(description='Submit a leave request')
    @jwt_required()
    @leave_ns.expect(request_input_model)
    def post(self):
        claims = get_current_employee()
        data = request.json

        try:
            start_date = datetime.strptime(data['start_date'], "%Y-%m-%d").date()
            end_date = datetime.strptime(data['end_date'], "%Y-%m-%d").date()
        except ValueError:
            return {'message': 'Invalid date format. Use YYYY-MM-DD.'}, 400

        if end_date < start_date:
            return {'message': 'End date must be after start date.'}, 400

        days_requested = (end_date - start_date).days + 1

        employee = Employee.query.get(claims['emp_id'])
        if not employee or (employee.emp_leave_balance or 0) < days_requested:
            return {'message': 'Insufficient leave balance'}, 400

        new_request = LeaveRequest(
            employee_id=employee.id,
            leave_type=data['leave_type'],
            start_date=start_date,
            end_date=end_date,
            days_requested=days_requested,
            reason=data['reason'],
            status=LeaveStatusEnum.PENDING
        )
        db.session.add(new_request)
        db.session.commit()

        return {'message': 'Leave request submitted'}, 201



@leave_ns.route('/my-requests')
class MyLeaveRequests(Resource):
    @leave_ns.doc(description='Get my leave requests')
    @jwt_required()
    def get(self):
        claims = get_current_employee()
        requests = LeaveRequest.query.filter_by(employee_id=claims['emp_id']) \
                                     .order_by(LeaveRequest.start_date.desc()).all()
        return leave_ns.marshal(requests, leave_request_model), 200


@leave_ns.route('/<int:id>/edit')
class EditLeaveRequest(Resource):
    @leave_ns.doc(description='Edit a pending leave request')
    @jwt_required()
    @leave_ns.expect(request_input_model)
    def put(self, id):
        claims = get_current_employee()
        data = request.json

        leave_request = LeaveRequest.query.get_or_404(id)

        # Only the owner can edit their leave request and only if it's pending
        if leave_request.employee_id != claims['emp_id']:
            return {'message': 'You can only edit your own leave requests'}, 403

        if leave_request.status != LeaveStatusEnum.PENDING:
            return {'message': 'Only pending leave requests can be edited'}, 400

        try:
            start_date = datetime.strptime(data['start_date'], "%Y-%m-%d").date()
            end_date = datetime.strptime(data['end_date'], "%Y-%m-%d").date()
        except ValueError:
            return {'message': 'Invalid date format. Use YYYY-MM-DD.'}, 400

        if end_date < start_date:
            return {'message': 'End date must be after start date.'}, 400

        days_requested = (end_date - start_date).days + 1

        employee = Employee.query.get(claims['emp_id'])
        if not employee or (employee.emp_leave_balance or 0) + leave_request.days_requested < days_requested:
            # Add back old days_requested before checking balance
            return {'message': 'Insufficient leave balance for updated dates'}, 400

        # Update the leave request fields
        leave_request.leave_type = data['leave_type']
        leave_request.start_date = start_date
        leave_request.end_date = end_date
        leave_request.days_requested = days_requested
        leave_request.reason = data['reason']

        db.session.commit()
        return {'message': 'Leave request updated successfully'}, 200


@leave_ns.route('/<int:id>/delete')
class DeleteLeaveRequest(Resource):
    @leave_ns.doc(description='Delete a pending leave request')
    @jwt_required()
    def delete(self, id):
        claims = get_current_employee()
        leave_request = LeaveRequest.query.get_or_404(id)

        # Only owner can delete their own leave request
        if leave_request.employee_id != claims['emp_id']:
            return {'message': 'You can only delete your own leave requests'}, 403

        # Only pending requests can be deleted
        if leave_request.status != LeaveStatusEnum.PENDING:
            return {'message': 'Only pending leave requests can be deleted'}, 400

        db.session.delete(leave_request)
        db.session.commit()

        return {'message': 'Leave request deleted successfully'}, 200



@leave_ns.route('/pending')
class PendingRequests(Resource):
    @leave_ns.doc(description='Get pending leave requests')
    @jwt_required()
    def get(self):
        claims = get_current_employee()
        if claims['emp_rank'] not in ['manager', 'admin']:
            return {'message': 'Access denied'}, 403

        query = LeaveRequest.query.join(Employee)

        if claims['emp_rank'] == 'manager':
            query = query.filter(
                Employee.emp_department == claims['emp_department'],
                LeaveRequest.status == LeaveStatusEnum.PENDING
            )
        else:  # admin
            query = query.filter(LeaveRequest.status == LeaveStatusEnum.PENDING)

        results = query.order_by(LeaveRequest.start_date.desc()).all()
        return leave_ns.marshal(results, leave_request_model), 200



@leave_ns.route('/<int:id>/approve')
class ApproveRequest(Resource):
    @leave_ns.doc(description='Approve a leave request')
    @jwt_required()
    def put(self, id):
        claims = get_current_employee()
        request_obj = LeaveRequest.query.get_or_404(id)

        if request_obj.status != LeaveStatusEnum.PENDING:
            return {'message': 'Leave request already processed'}, 400

        requestor = Employee.query.get(request_obj.employee_id)

        if claims['emp_rank'] == 'manager':
            if requestor.emp_department != claims['emp_department']:
                return {'message': 'Managers can only approve requests from their department'}, 403
        elif claims['emp_rank'] == 'admin':
            if requestor.emp_rank != 'admin':
                return {'message': 'Admins can only approve other admins'}, 403
        else:
            return {'message': 'Access denied'}, 403

        request_obj.status = LeaveStatusEnum.APPROVED
        request_obj.approved_by = claims['emp_id']
        request_obj.approved_at = datetime.now()

        requestor.emp_leave_balance -= request_obj.days_requested
        db.session.commit()
        return {'message': 'Leave approved'}, 200



@leave_ns.route('/<int:id>/reject')
class RejectRequest(Resource):
    @leave_ns.doc(description='Reject a leave request')
    @jwt_required()
    @leave_ns.expect(status_update_model)
    def put(self, id):
        claims = get_current_employee()
        data = request.json
        request_obj = LeaveRequest.query.get_or_404(id)

        if request_obj.status != LeaveStatusEnum.PENDING:
            return {'message': 'Leave request already processed'}, 400

        requestor = Employee.query.get(request_obj.employee_id)

        if claims['emp_rank'] == 'manager':
            if requestor.emp_department != claims['emp_department']:
                return {'message': 'Managers can only reject requests from their department'}, 403
        elif claims['emp_rank'] == 'admin':
            if requestor.emp_rank != 'admin':
                return {'message': 'Admins can only reject other admins'}, 403
        else:
            return {'message': 'Access denied'}, 403

        request_obj.status = LeaveStatusEnum.REJECTED
        request_obj.rejection_reason = data.get('rejection_reason')
        request_obj.approved_by = claims['emp_id']
        request_obj.approved_at = datetime.now()

        db.session.commit()
        return {'message': 'Leave rejected'}, 200


@leave_ns.route('/start')
class StartLeave(Resource):
    @leave_ns.doc(description='Start a leave request')
    @jwt_required()
    def post(self):
        claims = get_current_employee()
        today = datetime.today().date()

        employee = Employee.query.get(claims['emp_id'])

        if not employee:
            return {"message": "Employee not found."}, 404

        if employee.emp_work_status == 'On leave':
            return {"message": "You are already on leave."}, 400

        approved_leave = LeaveRequest.query.filter_by(
            employee_id=employee.id,
            status=LeaveStatusEnum.APPROVED,
            start_date=today
        ).first()

        if not approved_leave:
            return {"message": "No approved leave starting today."}, 400

        employee.emp_work_status = 'On leave'
        db.session.commit()

        return {"message": "Leave started. Your status has been updated to 'on leave'."}, 200



@leave_ns.route('/balance')
class LeaveBalance(Resource):
    @leave_ns.doc(description='Get leave balance')
    @jwt_required()
    def get(self):
        claims = get_current_employee()
        employee = Employee.query.get(claims['emp_id'])
        return {'leave_balance': employee.emp_leave_balance or 0}, 200
