from tkinter import *
class Base:
    def sel(self):
        selection = "You selected the option " + str(self.var.get())
        self.label.config(text = selection)

    def __init__(self):
        self.root = Tk()
        self.var = IntVar()
        self.frame = Frame(self.root)
        self.R1 = Radiobutton(self.frame, text="Option 1", variable=self.var, value=1, command=self.sel)
        self.R1.pack( anchor = W )
        self.R2 = Radiobutton(self.frame, text="Option 2", variable=self.var, value=2, command=self.sel)
        self.R2.pack( anchor = W )
        self.R3 = Radiobutton(self.frame, text="Option 3", variable=self.var, value=3, command=self.sel)
        self.R3.pack( anchor = W)
        self.frame.pack()
        self.label = Label(self.root)
        self.label.pack()
        self.root.mainloop()

Base()
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import text, select, update, insert, delete
# from models import Base, Employees, Classes, Services, Class_join, engine
# import os
# from datetime import date

# stmt = select(Classes.class_date).order_by(Classes.class_date.desc())
# dates = []
# with engine.begin() as connection:            
#     for row in connection.execute(stmt):
#         dates_dict = {
#             'date': row[0]
#         }
#         print(row[0])
#         dates.append(dates_dict)
#     if not dates:
#             print("No dates found")   
# print("#######")

# formatted_dates = [date_tuple['date'].strftime('%Y-%m-%d') for date_tuple in dates]

# for row in formatted_dates:
#     print(row)

# print("#######")
# with engine.begin() as connection:
#     results = connection.execute(stmt) 

# print(results)        
# for row in results:
#     print(row)

# stmt = select(Classes.class_date).order_by(Classes.class_date.desc())

# with engine.begin() as connection:            
#     for x in connection.execute(stmt):
#         print(x[0])

# # for x, y in enumerate(dates):
# #     print(x, y['date'])
    
# # cDate=[]
# # if request.args.get("date") is not None:
# #     cDate.append ({"date": request.args.get("date")})
# # else:
# #     cDate.append(dates[0])