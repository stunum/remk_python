from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    full_name = Column(String(100), nullable=False)
    user_type = Column(String(20), nullable=False, default='doctor')
    department = Column(String(100))
    title = Column(String(50))
    license_number = Column(String(50))
    status = Column(String(20), nullable=False, default='active')
    last_login_at = Column(TIMESTAMP(timezone=True))
    deleted_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), default='CURRENT_TIMESTAMP')
    updated_at = Column(TIMESTAMP(timezone=True), default='CURRENT_TIMESTAMP')
    created_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    updated_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))

    __table_args__ = (
        CheckConstraint("user_type IN ('admin', 'doctor', 'technician', 'viewer')"),
        CheckConstraint("status IN ('active', 'inactive', 'locked')"),
    )