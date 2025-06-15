from db import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Date
import datetime

# Data Model for Employee Bio-data
class Employee(db.Model):
    __tablename__ = "employee"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    auth_id: Mapped[int] = mapped_column(db.ForeignKey("auth.id"), nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    phone_no: Mapped[str] = mapped_column(String(20), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=False)
    country: Mapped[str] = mapped_column(String(50), nullable=False)

    emp_department: Mapped[str] = mapped_column(String(50), nullable=True)
    emp_team: Mapped[str] = mapped_column(String(100), nullable=True)
    emp_position: Mapped[str] = mapped_column(String(100), nullable=True)
    emp_rank: Mapped[str] = mapped_column(String(20), nullable=True)

    emp_leave_balance: Mapped[int] = mapped_column(Integer, nullable=True)
    emp_start_date: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    emp_end_date: Mapped[datetime.date] = mapped_column(Date, nullable=True)

    emp_status: Mapped[str] = mapped_column(String(20), nullable=True)
    emp_work_status: Mapped[str] = mapped_column(String(20), nullable=True)


    auth = relationship(
        "Auth",
        back_populates="employee"
    )
