from datetime import date, datetime
from typing import Optional
from sqlalchemy import Integer, Date, DateTime, Enum, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import db

class Attendance(db.Model):
    __tablename__ = "attendance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employee.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    clock_in_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    clock_out_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    total_hours: Mapped[float] = mapped_column(Numeric(4, 2), default=0.00)
    status: Mapped[str] = mapped_column(
        Enum("Present", "Absent", "Late", "Half Day", name="attendance_status_enum"),
        default="Absent"
    )

    
    employee = relationship("Employee", back_populates="attendance_records")

    __table_args__ = (
        UniqueConstraint("employee_id", "date", name="unique_employee_date"),
    )
