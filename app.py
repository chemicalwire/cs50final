# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.orm import sessionmaker, DeclarativeBase, MappedAsDataclass
# from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from models import Base, Employees, Classes, Services, Class_join, engine
from helpers import apology
import os
from datetime import date
os.environ["Flask_ENV"] = "development"

# Configure application
app = Flask(__name__)
app.debug = True
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["DEBUG"] = True

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# session_factory = sessionmaker(bind=engine)

# db = SQLAlchemy(app)
# db.create_all()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
# @login_required
def index():

    return render_template("./index.html")
    # if a class exists with todays date, then display that class
    # otherwise ask if they would like to create a new class attendance
    # return render_template("index.html", stocks=portfolio, prices=prices, port_total=portfolio_total, user=user)


@app.route("/class_history", methods=["GET", "POST"])
def class_history():
    
    #get a list of all previous classes
    stmt = text("SELECT  class_date FROM classes ORDER BY class_date DESC")
    with engine.connect() as connection:
        results = connection.execute(stmt).fetchall()
    
    dates = []
    for result in results:
        dates.append(result[0])

    if request.method == "GET":
        stmt = text("SELECT class_join.id, classes.id, classes.class_date, employees.id, employees.name, services.service FROM class_join " \
        "JOIN classes ON classes.id = class_join.class_id " \
        "JOIN employees ON employees.id = class_join.employee_id " \
        "JOIN services ON services.id = class_join.service_id " \
        "ORDER BY employees.role, employees.name")

        with engine.connect() as connection:
            results = []
            for row in connection.execute(stmt):
                result_dict = {
                    'class_join_id': row[0],
                    'class_id': row[1],
                    'class_date': row[2],
                    'employee_name': row[4],
                    'service_name': row[5]
                }
                results.append(result_dict)
        if results == []:
            return apology("No classes found")
        
        return render_template("/classes.html", results=results, dates=dates)
    
    else:     

        stmt = text("SELECT class_join.id, classes.id, classes.class_date, employees.id, employees.name, services.service FROM class_join " \
        "JOIN classes ON classes.id = class_join.class_id " \
        "JOIN employees ON employees.id = class_join.employee_id " \
        "JOIN services ON services.id = class_join.service_id " \
        "WHERE classes.class_date = :date " \
        "ORDER BY employees.role, employees.name")
        cDate = [{"date": request.form.get("class_date")}]
        with engine.connect() as connection:
            results = []
            for row in connection.execute(stmt, cDate):
                result_dict = {
                    'class_join_id': row[0],
                    'class_id': row[1],
                    'class_date': row[2],
                    'employee_name': row[4],
                    'service_name': row[5]
                }
                results.append(result_dict)    

        if results == []:
            return apology("No classes found for that date")
        
        return render_template("/classes.html", results=results, dates=dates)

@app.route("/class_edit", methods=["GET", "POST"])
def class_edit():

    if request.method == "POST":
        #get the data from the form
        date = request.form.get("class_date")
        teacher = request.form.get("employee")   
        service = request.form.get("services")
        class_id = request.form.get("class_id")
        print(date, class_id, teacher, service)
        stmt = text("INSERT INTO class_join (class_id, employee_id, service_id) VALUES (:class_id, :teacher_id, :service_id)")
        data = {"class_id": class_id, "teacher_id": teacher, "service_id": service}
        with engine.begin() as connection:
            connection.execute(stmt, data)

        return redirect(f"/class_edit?date={date}")
    else:
        stmt = text("SELECT * from classes")
        # with engine.connect() as connection:
        #     print("FUCK:", connection.execute(stmt).all())
        #         #return apology("No classes found")
        # #   preload all the relevant data 
        stmt = text("SELECT class_date FROM classes ORDER BY class_date DESC")
        
        with engine.begin() as connection:
            dates = []
            for row in connection.execute(stmt):
                
                dates_dict = {
                    'date': row[0]
                }
                dates.append(dates_dict)
            if not dates:
                    return apology("There are no existing classes")
        cDate=[]
        if request.args.get("date") is not None:
            cDate.append ({"date": request.args.get("date")})
        else:
            cDate.append(dates[0])
        #print("DATE: ", cDate)

        #get services
        stmt = text("SELECT * from services WHERE service_type = 0 ORDER BY service")
        with engine.connect()  as connection:
            teacher_services = []
            for row in connection.execute(stmt):
                services_dict = { 
                    'id': row[0],
                    'service': row[1]
                }
                teacher_services.append(services_dict)  
        #print("teacher services", teacher_services) 

        stmt = text("SELECT * from services WHERE service_type = 1 ORDER BY service")
        with engine.connect()  as connection:
            student_services = []
            for row in connection.execute(stmt):
                services_dict = { 
                    'id': row[0],
                    'service': row[1]                    
                }
                student_services.append(services_dict)  
        #print("student services", student_services) 
        
        #get teachers 
        stmt = text("SELECT * from employees WHERE role = 0 AND active = 1 ORDER BY name")
        with engine.connect() as connection:
            teachers = []
            for row in connection.execute(stmt).fetchall():
                teacher_dict = {
                    'id': row[0],
                    'name': row[1]
                }
                teachers.append(teacher_dict)
        #print("teachers", teachers)
                
        #get students
        stmt = text("SELECT * from employees WHERE role = 1 AND active = 1 ORDER BY name")
        with engine.connect() as connection:
            students = []
            for row in connection.execute(stmt).fetchall():
                teacher_dict = {
                    'id': row[0],
                    'name': row[1]
                }
                students.append(teacher_dict)
            #print("students ", students)
            
            #get class_id
            stmt = text("SELECT id from classes WHERE class_date = :date")
            with engine.connect() as connection:
                class_id = connection.execute(stmt, cDate).fetchone()
                classID = class_id[0]

            # get class data
            stmt = text("SELECT class_join.id, classes.id, classes.class_date, employees.id, employees.name, services.service, classes.theory_topic, classes.notes FROM class_join " \
            "JOIN classes ON classes.id = class_join.class_id " \
            "JOIN employees ON employees.id = class_join.employee_id " \
            "JOIN services ON services.id = class_join.service_id " \
            "WHERE classes.class_date = :date " \
            "ORDER BY employees.role, employees.name")
            
            with engine.connect() as connection:
                classes = []
                for row in connection.execute(stmt, cDate):
                    result_dict = {
                        'class_join_id': row[0],
                        'class_id': row[1],
                        'class_date': row[2],
                        'employee_name': row[4],
                        'service_name': row[5],
                        'theory_topic': row[6],
                        'notes': row[7] 
                    }
                    classes.append(result_dict)
                #print("CLASSES:", classes)
        
        #return redirect("/class_history")
        return render_template("/class_edit.html",  classID=classID, dates=dates, date=cDate, teachers=teachers, students=students, teacher_services=teacher_services, student_services=student_services, classes=classes)

@app.route("/class_update", methods=["POST"])
def class_update():
    #get data from the form
    class_id = request.form.get("class_id")
    class_date = request.form.get("class_date")
    theory = request.form.get("theory_topic")
    notes = request.form.get("notes")  
    print(class_id, class_date, theory, notes)
    stmt = text("UPDATE classes SET theory_topic = :theory, notes = :notes WHERE id = :class_id")
    data = {"theory": theory, "notes": notes, "class_id": class_id} 
    with engine.begin() as connection:
        connection.execute(stmt, data)

    return redirect(f"/class_edit?date=" + class_date)

@app.route("/class_add", methods=["GET"])
def class_add():
    #get todat's date
    today = date.today()
    tDate = today.strftime("%Y-%m-%d")

    #check to see if a class already exists for today
    stmt = text("SELECT * from classes WHERE class_date = :date")
    data = {"date": tDate}
    with engine.connect() as connection:
        result = connection.execute(stmt, data).all()   
    print("DATE: ", tDate)
    print("RESULT: ", result)
    if not (result == []):
        return apology("Class already exists for today")
    
    #if it doesn't exist, create a new class
    stmt = text("INSERT INTO classes (class_date, theory_topic, notes) VALUES (:class_date, :theory_topic, :notes)")
    data = {"class_date": tDate, "theory_topic": "", "notes": ""}
    with engine.begin() as connection:
        connection.execute(stmt, data)    

    # stmt = text("SELECT * from classes WHERE class_date = :date")
    # data = {"date": tDate}
    # with engine.connect() as connection:
    #     result = connection.execute(stmt, data).all()
    
    # if result is None:
    #     stmt = text("INSERT INTO classes (theory_topic, notes) VALUES ('', '')")
    #     with engine.begin() as connection:
    #         connection.execute(stmt)
            
    # print(result)
    # if result is None:
    #     stmt = text("INSERT INTO classes (theory_topic, notes) VALUES ('', '')")
    #     with engine.begin() as connection:
    #         connection.execute(stmt)

    return redirect(f"/class_edit")

@app.route("/delete_entry", methods=["POST"])
def delete_entry():

    class_join_id = request.form.get("class_join_id")
    class_date = request.form.get("class_date")
    print("Class date: ", class_date)
    print("Join ID:", class_join_id)

    stmt = text("DELETE FROM class_join WHERE id = :class_join_id")
    data = {"class_join_id": class_join_id}
    with engine.begin() as connection:
        connection.execute(stmt, data)

    return redirect(f"/class_edit?date={class_date}") 
    return redirect("/class_edit") 

@app.route("/employees", methods=["GET"])
#@login_required
def employees():

    stmt = text("SELECT * from employees ORDER BY role, name")
    with engine.connect() as connection:
        #results = connection.execute(stmt)
        results = []
        for row in connection.execute(stmt):
            result_dict = {
                'id': row[0],
                'name': row[1],
                'role': row[2],
                'active': row[3]
            }
            results.append(result_dict)
        
    #print("RESULTS: ", results.all())
    return render_template("./employees.html", results=results)
   
@app.route("/add_employee", methods=["GET", "POST"])
def add_employee():

    # if request.method == "POST":
    name = request.form.get("employee_name")
    role = request.form.get("role")
    if role  not in ["0", "1"]:
        return apology("Not teacher or student. Stop editing the html.")
    
    #validate the data
    #Make sure we were not passed empty data
    if name == "" or role is None:
        return apology("Please enter a name and role")
    if role not in ["0", "1"]:
        return apology("Please select a valid role")
    
    #check to make sure the employee doesn't already exist
    stmt = text("SELECT * from employees WHERE name = :name")
    data = {"name": name}
    with engine.connect() as connection:
        result = connection.execute(stmt, data).fetchone()

    if result is not None:
        return apology("Employee already exists")   

    print(name, role)
    stmt = text("INSERT INTO employees (name, role, active) VALUES (:name, :role, 1)")  
    data = {"name": name, "role": role}
    with engine.begin() as connection:
        connection.execute(stmt, data)  
    
    return redirect("/employees")

@app.route("/edit_employee", methods=["GET", "POST"])
def edit_employee():
    # if request.method == "POST":
    employeeID = request.form.get("employee_id")
    print(employeeID)
    if employeeID == "":
        return apology("Please select an employee to edit") 
    stmt = text("UPDATE employees SET active = 0 WHERE id = :employeeID")
    data = {"employeeID": employeeID}
    with engine.begin() as connection:
        connection.execute(stmt, data)

    
    return redirect("/employees")

@app.route("/services")
def get_services():
    stmt = text("SELECT * from services ORDER BY service_type, service")
    with engine.connect() as connection:
        results = []
        for row in connection.execute(stmt):
            result_dict = {
                'id': row[0],
                'service': row[1],
                'service_type': row[2]
            }
            results.append(result_dict)
    
    return render_template("./services.html", results=results)

@app.route("/add_service", methods=["GET", "POST"])
def add_service():


    name = request.form.get("service_name")
    role = request.form.get("type")
    # print(name, role)

    if role  not in ["0", "1"]:
        return apology("Dirty data detected. Stop editing the html.")
    #validate the data
    if name == "" or role is None:
        return apology("Please enter a service name and type") 
    if role not in ["0", "1"]:  
        return apology("Please select a valid service type")    
    
    #check to make sure the service doesn't already exist
    stmt = text("SELECT * from services WHERE service = :name AND service_type = :role  ") 
    data = {"name": name, "role": role}
    with engine.connect() as connection:
        result = connection.execute(stmt, data).fetchone()
    if result is not None:
        return apology("Service already exists")
    stmt = text("INSERT INTO services (service, service_type) VALUES (:name, :role)")
    data = {"name": name, "role": role}
    with engine.begin() as connection:
        connection.execute(stmt, data)

    return redirect("/services")



if __name__ == "__main__":
    app.run(debug=True)