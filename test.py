
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select, update, insert, delete
from models import Base, Employees, Classes, Services, Class_join, engine
import os
from datetime import date

stmt = select(Classes.class_date).order_by(Classes.class_date.desc())
dates = []
with engine.begin() as connection:            
    for row in connection.execute(stmt):
        dates_dict = {
            'date': row[0]
        }
        print(row[0])
        dates.append(dates_dict)
    if not dates:
            print("No dates found")   
print("#######")
with engine.begin() as connection:
    results = connection.execute(stmt) 

print(results)        
for row in results:
    print(row)
       
# cDate=[]
# if request.args.get("date") is not None:
#     cDate.append ({"date": request.args.get("date")})
# else:
#     cDate.append(dates[0])