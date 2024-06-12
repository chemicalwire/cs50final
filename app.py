from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select, update, insert, delete
import sqlalchemy.exc
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from models import Base, Employees, Classes, Services, Class_join, Users, engine
from helpers import apology, login_required
import os
from datetime import date

os.environ["Flask_ENV"] = "development"

# Configure application
app = Flask(__name__)
app.debug = True
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["DEBUG"] = True


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
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
@login_required
def index():
    return render_template("./index.html")

@app.route("/class_edit", methods=["GET", "POST"])
@login_required
def class_edit():
    ''' Class edit page. Allows user to add students to a class, update theory and notes, and delete students from a class.'''

    if request.method == "POST":
        ''' insert new class participant and then return to the get of this page'''
        #get the data from the form
        date = request.form.get("class_date")
        class_id = request.form.get("class_id")
        teacher = request.form.get("employee")   
        service = request.form.get("services")

        # print(service, teacher)
        if not teacher:
             return apology("Please stop editing the html, asshole")  
              
        # print(date, employees, service, class_id)
        stmt = insert(Class_join).values(class_id = class_id, employee_id = teacher, service_id = service)  
        try:
            with engine.begin() as connection:
                connection.execute(stmt)
        except sqlalchemy.exc.IntegrityError:
            return apology("There was an error adding this to the database. Please try again.")

        return redirect(f"/class_edit?date={date}")
    else:

        ############################################
        # the following code bugs me, but it works
        ############################################
        stmt = select(Classes.class_date).order_by(Classes.class_date.desc())
        dates = []
        with engine.begin() as connection:            
            for row in connection.execute(stmt):
                dates.append({'date': row[0]}) 
        if not dates:
            return apology("There are no existing classes")                     
        cDate=[]
        if request.args.get("date") is not None:
            cDate.append ({"date": request.args.get("date")})
        else:
            cDate.append(dates[0])

        
        # this is the way to go maybe?, but i need to figure out how to incorporate it
        # formatted_dates = [date_tuple['date'].strftime('%Y-%m-%d') for date_tuple in dates]
        # print(formatted_dates)

        ######################################################
        # Get all the relevant data to populate the form
        #####################################################
         
        #get services
        stmt = select(Services).where(Services.service_type == 0).order_by(Services.service)
        with engine.connect()  as connection:
            teacher_services = connection.execute(stmt).fetchall()
        stmt = select(Services).where(Services.service_type == 1).order_by(Services.service)
        with engine.connect()  as connection:       
            student_services = connection.execute(stmt).fetchall()
        #get teachers and students
        stmt = select(Employees).where(Employees.role == 0, Employees.active == 1).order_by(Employees.name)
        with engine.connect() as connection:
            teachers = connection.execute(stmt).fetchall()
        stmt = select(Employees).where(Employees.role == 1, Employees.active == 1).order_by(Employees.name)
        with engine.connect() as connection:
            students = connection.execute(stmt).fetchall()
        #get class_id
        stmt = text("SELECT id from classes WHERE class_date = :date")
        with engine.connect() as connection:
            classID = connection.execute(stmt, cDate).fetchone()
        if classID is None: # if there is no class for this date, return an apology
            return apology("No class found for this date")
        
        # get class data for specified class - I tried to write this using ORM and it was just ridiculous
        stmt = text("SELECT class_join.id AS class_join_id, classes.id, " \
        "classes.class_date, employees.id, employees.name AS employee_name, " \
        "services.service AS service_name, classes.theory_topic AS theory_topic, "\
        "classes.notes AS notes FROM class_join " \
        "JOIN classes ON classes.id = class_join.class_id " \
        "JOIN employees ON employees.id = class_join.employee_id " \
        "JOIN services ON services.id = class_join.service_id " \
        "WHERE classes.class_date = :date " \
        "ORDER BY employees.role, employees.name")      
        with engine.connect() as connection:
            classes = connection.execute(stmt, cDate).fetchall()

        return render_template("/class_edit.html",  classID=classID, dates=dates, date=cDate, teachers=teachers, students=students, teacher_services=teacher_services, student_services=student_services, classes=classes)

@app.route("/update_class_data", methods=["POST"])
@login_required
def class_update():
    '''updates the theory and notes for a class'''
    #get data from the form
    class_id = request.form.get("class_id")
    class_date = request.form.get("class_date")
    theory = request.form.get("theory_topic")
    notes = request.form.get("notes")  
    stmt = update(Classes).where(Classes.id == class_id).values(theory_topic = theory, notes = notes)
    with engine.begin() as connection:
        connection.execute(stmt)

    return redirect(f"/class_edit?date=" + class_date)

@app.route("/class_add", methods=["GET"])
@login_required
def class_add():
    '''Adds a new class for the current date, if one already exist, yell at the user'''
    #get today's date
    today = date.today()
    tDate = today

    #check to see if a class already exists for today
    stmt = select(Classes).where(Classes.class_date == tDate)
    with engine.connect() as connection:
        result = connection.execute(stmt).all()   
    if not (result == []):
        return apology("Class already exists for today")
    
    #if it doesn't exist, create a new class
    stmt = insert(Classes).values(class_date = tDate, theory_topic = "", notes = "")
    with engine.begin() as connection:
        connection.execute(stmt)    

    return redirect(f"/class_edit?date={tDate}")

@app.route("/delete_entry", methods=["POST"])
@login_required
def delete_entry():
    '''deletes a student from class'''

    class_join_id = request.form.get("class_join_id")
    class_date = request.form.get("class_date")
    stmt = delete(Class_join).where(Class_join.id == class_join_id)
    with engine.begin() as connection:
        connection.execute(stmt)

    return redirect(f"/class_edit?date={class_date}") 

@app.route("/employees", methods=["GET", "POST"])
@login_required
def employees():
    '''display a list of employees'''
    
    if request.method == "GET":
        stmt= select(Employees).order_by(Employees.role, Employees.name)    
        with engine.connect() as connection:
            results= connection.execute(stmt).fetchall()

        active_status = '0'
    else:
        ''' toggles inactive on or off'''
        active_status = request.form.get("active_status")
        if active_status == "1":
            stmt = select(Employees).where(Employees.active == active_status).order_by(Employees.active.desc(), Employees.role, Employees.name)
        else:
            stmt = select(Employees).order_by(Employees.role, Employees.name)

        with engine.connect() as connection:
            results = connection.execute(stmt).fetchall()   

    return render_template("./employees.html", results=results, active=active_status)

@app.route("/change_active_status", methods=["GET", "POST", "FETCH"])
@login_required
def change_active_status():

    ''' can i just make this a fetch request?'''
    active_status = request.form.get("active_status")
    employeeID = request.form.get("employeeID")
    active_status = request.form.get("active_status")
    print(employeeID, active_status)

    stmt = update(Employees).where(Employees.id == employeeID).values(active = active_status)
    with engine.begin() as connection:
        connection.execute(stmt)

    return redirect(f"/employees?active_status={active_status}")
   
@app.route("/add_employee", methods=["GET", "POST"])
@login_required
def add_employee():
    '''add employee to the database'''

    if request.method == "POST":
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
        
        #check to make sure employee with the same name doesn't already exist
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
    
@app.route("/services")
@login_required
def get_services():
    '''display a list of services'''
    stmt = select(Services).order_by(Services.service_type, Services.service)   
    with engine.connect() as connection:
        results = connection.execute(stmt).fetchall()
    
    return render_template("./services.html", results=results)

@app.route("/add_service", methods=["GET", "POST"])
@login_required
def add_service():
    '''add a service to the database'''
    name = request.form.get("service_name")
    role = request.form.get("type")

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


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # check to make sure fields are all filled out and passwords match
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            return apology("What is you name? What is your favorite color?")
        elif (request.form.get("confirmation") != request.form.get("password")):
            return apology("Passwords do not match")

        # Query database for username
        stmt = select(Users).where(Users.username == request.form.get("username"))
        with engine.connect() as connection:
            if connection.execute(stmt).fetchall():
                return apology("Username in use")
        
        hashpassword = generate_password_hash(request.form.get("password"))

        stmt = insert(Users).values(username = request.form.get("username"), password_hash = hashpassword)
        with engine.begin() as connection:
            result = connection.execute(stmt)
            session["user_id"] = result.inserted_primary_key[0]   

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("register.html")
    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    session.clear()
    if request.method == "POST":
        #  check for username and password
        if (not request.form.get("username")) or (not request.form.get("password")):
            return apology("What is your name? What is your favorite color?", 403)

        stmt = select(Users).where(Users.username == request.form.get("username"))
        with engine.connect() as connection:
            rows = connection.execute(stmt).fetchall()
 
            if not rows or not check_password_hash(rows[0][2], request.form.get("password")):
                return apology("You shall not pass!", 403)

        session["user_id"] = rows[0][0]
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log out"""

    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)