from datetime import datetime, date, time

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    Date,
    Time,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    preferred_start_time = Column(Time, nullable=True)
    preferred_end_time = Column(Time, nullable=True)

    session_length = Column(Integer, nullable=True)

    reminder_style = Column(String, nullable=True)

    assignments = relationship(
        "Assignment",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    deadline = Column(Date, nullable=False)

    estimated_hours = Column(Float, nullable=True)

    status = Column(
        String,
        default="active",
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="assignments"
    )

    tasks = relationship(
        "Task",
        back_populates="assignment",
        cascade="all, delete-orphan"
    )


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    assignment_id = Column(
        Integer,
        ForeignKey("assignments.id"),
        nullable=False
    )

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    duration = Column(Integer, nullable=True)
    difficulty = Column(String, nullable=True)

    status = Column(
        String,
        default="pending",
        nullable=False
    )

    scheduled_date = Column(Date, nullable=True)
    scheduled_time = Column(Time, nullable=True)

    depends_on = Column(Integer, nullable=True)

    assignment = relationship(
        "Assignment",
        back_populates="tasks"
    )

    feedback = relationship(
        "Feedback",
        back_populates="task",
        cascade="all, delete-orphan"
    )


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)

    task_id = Column(
        Integer,
        ForeignKey("tasks.id"),
        nullable=False
    )

    actual_duration = Column(Integer, nullable=True)

    difficulty = Column(String, nullable=True)

    completed = Column(Boolean, default=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    task = relationship(
        "Task",
        back_populates="feedback"
    )