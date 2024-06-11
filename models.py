from sqlalchemy.orm import sessionmaker, DeclarativeBase, MappedAsDataclass
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import create_engine, ForeignKey, String, text, Integer, Column
from sqlalchemy import func, insert
from datetime import date
from typing import Optional


class Base(MappedAsDataclass, DeclarativeBase):
    pass

class Employees(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str]
    role: Mapped[int] 
    active: Mapped[int]
    class_joins = relationship("Class_join", back_populates="employees")

    # def __repr__(self):
    #     return f"{{'id': {self.id}, 'name': {self.name}, 'role': {self.role}, 'active': {self.active}}}"

class Services(Base):
    __tablename__ = "services"
    id: Mapped[int] = mapped_column(primary_key=True,init=False)
    service: Mapped[str]
    service_type: Mapped[int]
    class_joins = relationship("Class_join", back_populates="services")

    # def __repr__(self):
    #     return f"{{'id': {self.id}, 'service': {self.service}, 'service_type': {self.service_type}}}"

class Classes(Base):
    __tablename__ = "classes"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    class_date: Mapped[date]
    theory_topic: Mapped[Optional[str]]
    notes: Mapped[Optional[str]]
    class_joins = relationship("Class_join", back_populates="classes")

    # def __repr__(self):
    #     return f"{{'id': {self.id}, 'class_date': {self.class_date}, 'theory_topic': {self.theory_topic}, 'notes': {self.notes}}}"


class Class_join(Base):
    __tablename__ = "class_join"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"))
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id")) 
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))
    classes: Mapped[list["Classes"]]= relationship("Classes", back_populates="class_joins")
    employees: Mapped[list["Employees"]] = relationship("Employees", back_populates="class_joins")
    services: Mapped[list["Services"]] = relationship("Services", back_populates="class_joins")

    # def __repr__(self):
    #     return f"{{'id': {self.id}, 'class_id': {self.class_id}, 'employee_id': {self.employee_id}, 'service_id': {self.service_id}}}"

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)   
    username: Mapped[str]
    password_hash: Mapped[str]

engine = create_engine("sqlite:///attendance.db")
Base.metadata.create_all(bind=engine)

def populate_database():
	
    stmt = text("""INSERT INTO services (service, service_type) VALUES 
    ('Theory', 0), 
    ('Blowdry/Up-do', 1), 
    ('Cut and Style', 1), 
    ('Barbering', 1), 
    ('Haircutting', 0), 
    ('Single Process', 1), 
    ('Color', 0), 
    ('Highlights', 1), 
    ('Balayage', 1), 
    ('Mannequin', 1), 
    ('Absent', 1), 
    ('Excused', 1), 
    ('Creative Color', 1), 
    ('Haircutting Shadow', 0), 
    ('Color Shadow', 0), 
    ('Styling', 0)""")
      
    with engine.begin() as connection:
        connection.execute(stmt)

    stmt = text("""
        INSERT INTO employees (name, role, active) VALUES
        ('Billy', 0, 1),
        ('Anna', 0, 1),
        ('Michael', 0, 1),
        ('Julie', 0, 1),
        ('Aimee', 0, 1),
        ('Cheryl', 0, 1),
        ('Kelsie', 0, 1),
        ('Craig', 0, 1)
    """)
    with engine.begin() as connection:
        connection.execute(stmt)

# def populate_database():
#     ''' add in  services'''

#     inserts = [
#         {"service": "Theory", "service_type": 0},
#         {"service": "Blowdry/Up-do", "service_type": 1},
#         {"service": "Cut and Style", "service_type": 1},
#         {"service": "Barbering", "service_type": 1},
#         {"service": "Haircutting", "service_type": 0},
#         {"service": "Single Process", "service_type": 1},
#         {"service": "Color", "service_type": 0},
#         {"service": "Highlights", "service_type": 1},
#         {"service": "Balayage", "service_type": 1},
#         {"service": "Mannequin", "service_type": 1},
#         {"service": "Absent", "service_type": 1},
#         {"service": "Excused", "service_type": 1},
#         {"service": "Creative Color", "service_type": 1},
#         {"service": "Haircutting Shadow", "service_type": 0},
#         {"service": "Color Shadow", "service_type": 0},
#         {"service": "Styling", "service_type": 0}
#     ]

#     user_insert = insert(Services)
#     with engine.begin() as connection:
#         connection.execute(user_insert, inserts)
