from db import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String


# Data Model for Employee Bio-data
class Employee(db.Model):
    __tablename__ = "employee"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    auth_id: Mapped[int] = mapped_column(db.ForeignKey("auth.id"), nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    phone_no: Mapped[str] = mapped_column(String(20), nullable=True)
    gender: Mapped[str] = mapped_column(String(10), nullable=True)
    address: Mapped[str] = mapped_column(String(200), nullable=True)
    country: Mapped[str] = mapped_column(String(50), nullable=True)

    auth = relationship(
        "Auth",
        back_populates="employee"
    )
