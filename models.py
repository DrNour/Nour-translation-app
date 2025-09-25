from sqlalchemy import Column, Integer, String, ForeignKey, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # hashed
    role = Column(String, nullable=False)      # "student" or "instructor"
    submissions = relationship("Submission", back_populates="student")

class Exercise(Base):
    __tablename__ = "exercises"
    id = Column(Integer, primary_key=True)
    source_text = Column(Text)
    target_lang = Column(String)
    submissions = relationship("Submission", back_populates="exercise")

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    translation = Column(Text)
    bleu = Column(String)
    comet = Column(String)
    errors = Column(Text)  # JSON string of error categories

    student = relationship("User", back_populates="submissions")
    exercise = relationship("Exercise", back_populates="submissions")

engine = create_engine("sqlite:///translation_app.db")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
