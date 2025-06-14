from db import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String


# Data Model for Employee Auth
class Auth(db.Model):
    __tablename__ = "auth"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # one-to-one relationship with Employee
    employee = relationship(
        "Employee",
        back_populates="auth",
        cascade="all, delete-orphan",
        uselist=False  # one-to-one relationship
    )

    def to_dict(self):
        return {"id": self.id, "email": self.email}
    
    def __repr__(self):
        return f"<Login email={self.email}>"
