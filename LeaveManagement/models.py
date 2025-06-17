from datetime import datetime, date
from enum import Enum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Enum as SQLAlchemyEnum, Integer, Date, DateTime, Text, ForeignKey
from db import db

class LeaveTypeEnum(str, Enum):
    ANNUAL = 'Annual'
    SICK = 'Sick'
    PERSONAL = 'Personal'
    EMERGENCY = 'Emergency'

class LeaveStatusEnum(str, Enum):
    PENDING = 'Pending'
    APPROVED = 'Approved'
    REJECTED = 'Rejected'

class LeaveRequest(db.Model):
    __tablename__ = "leave_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employee.id"), nullable=False)
    leave_type: Mapped[LeaveTypeEnum] = mapped_column(SQLAlchemyEnum(LeaveTypeEnum), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    days_requested: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[LeaveStatusEnum] = mapped_column(SQLAlchemyEnum(LeaveStatusEnum), default=LeaveStatusEnum.PENDING)
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("employee.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="leave_requests", lazy=True)

    approver = relationship("Employee", foreign_keys=[approved_by], back_populates="approved_requests",lazy=True)

    def __repr__(self):
        return f"<LeaveRequest {self.id} - {self.leave_type} ({self.status})>"
