from sqlalchemy import Column, String, TIMESTAMP, Enum, func, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class GpsTrack(Base):
    __tablename__ = "gps_track"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    latitude = Column(String, nullable=False)
    longitude = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    user = relationship("User", back_populates="tracks")

class Role(str, Enum):
    User = "User"
    Admin = "Admin"


class User(Base):
    __tablename__ = "user"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Role, nullable=False, default=Role.User)
    register_date = Column(
        TIMESTAMP, nullable=False, server_default=func.current_timestamp()
    )
    tracks = relationship("GpsTrack", back_populates="user", cascade="all, delete-orphan")
