import os
import platform
import mysql.connector as sql
import pandas as pd

# Establish DB connection
mydb = sql.connect(host="localhost",user="root",password="@prince",
                   database="food")
mycursor = mydb.cursor()


def Customer():
    try:
        c_id = int(input("Enter the customer ID number: "))
        name = input("Enter the Customer Name: ")
        cphone = input("Enter customer phone number: ")
        payment = int(input("Enter payment method ((1)Credit Card/(2)Debit Card): "))
        pstatus = input("Enter the payment status (Paid/Unpaid): ")
        email = input("Enter the email ID: ")
        orderid = input("Enter Order ID: ")
        date = input("Enter the Date (YYYY-MM-DD): ")

        sql = """
            INSERT INTO customer (c_id, C_name, cphone, payment, pstatus, email, orderid, date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (c_id, name, cphone, payment, pstatus, email, orderid, date)
        mycursor.execute(sql, values)
        mydb.commit()
        print("Customer added successfully.")
    except Exception as e:
        print(f"Error: {e}")


def Employee():
    try:
        Emp_id = int(input("Enter the Employee ID: "))
        ename = input("Enter the Employee Name: ")
        emp_g = input("Enter Gender (M/F): ")
        eage = int(input("Enter Employee Age: "))
        emp_phone = input("Enter Employee Phone Number: ")
        pwd = input("Set Password: ")

        sql = """
            INSERT INTO Employee (Emp_id, ename, emp_g, eage, emp_phone, pwd)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (Emp_id, ename, emp_g, eage, emp_phone, pwd)
        mycursor.execute(sql, values)
        mydb.commit()
        print("Employee added successfully.")
    except Exception as e:
        print(f"Error: {e}")


def Food():
    try:
        Food_id = int(input("Enter the Food ID: "))
        Foodname = input("Enter the Food Name: ")
        Food_size = input("Enter Food Size (Small/Medium/Large): ")
        price = int(input("Enter Price of Food: "))

        sql = "INSERT INTO Food (Food_id, Foodname, Food_size, prize) VALUES (%s, %s, %s, %s)"
        values = (Food_id, Foodname, Food_size, price)
        mycursor.execute(sql, values)
        mydb.commit()
        print("Food item added successfully.")
    except Exception as e:
        print(f"Error: {e}")


def OrderFood():
    try:
        OrderF_id = int(input("Enter the Food Order ID: "))
        C_id = int(input("Enter the Customer ID: "))
        Emp_id = int(input("Enter the Employee ID: "))
        Food_id = int(input("Enter the Food ID: "))
        Food_qty = int(input("Enter Quantity: "))
        Total_price = float(input("Enter Total Price: "))

        sql = """
            INSERT INTO OrderFood (OrderF_id, C_id, Emp_id, Food_id, Food_qty, Total_price)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (OrderF_id, C_id, Emp_id, Food_id, Food_qty, Total_price)
        mycursor.execute(sql, values)
        mydb.commit()
        print("Order placed successfully.")
    except Exception as e:
        print(f"Error: {e}")


def View():
    print("\nSelect the search criteria:")
    print("1. View Employee by ID")
    print("2. View Customer by Name")
    print("3. View All Foods")
    print("4. View Orders by Food ID")
    
    try:
        ch = int(input("Enter your choice (1 to 4): "))
        if ch == 1:
            s = int(input("Enter Employee ID: "))
            sql = "SELECT * FROM Employee WHERE Emp_id = %s"
            mycursor.execute(sql, (s,))
        elif ch == 2:
            s = input("Enter Customer Name: ")
            sql = "SELECT * FROM Customer WHERE C_name = %s"
            mycursor.execute(sql, (s,))
        elif ch == 3:
            sql = "SELECT * FROM Food"
            mycursor.execute(sql)
        elif ch == 4:
            s = int(input("Enter Food ID: "))
            sql = "SELECT * FROM OrderFood WHERE Food_id = %s"
            mycursor.execute(sql, (s,))
        else:
            print("Invalid choice.")
            return

        res = mycursor.fetchall()
        for x in res:
            print(x)
    except Exception as e:
        print(f"Error: {e}")


def feeDeposit():
    try:
        roll = int(input("Enter Roll Number: "))
        feedeposit = float(input("Enter Fee to be deposited: "))
        month = input("Enter Month (e.g., August): ")

        sql = "INSERT INTO fee (roll, feedeposit, month) VALUES (%s, %s, %s)"
        mycursor.execute(sql, (roll, feedeposit, month))
        mydb.commit()
        print("Fee deposited successfully.")
    except Exception as e:
        print(f"Error: {e}")


def MenuSet():
    print("\n===== FOOD ORDER SYSTEM MENU =====")
    print("1: Add Employee")
    print("2: Add Customer")
    print("3: Add Food Item")
    print("4: Place Order")
    print("5: Deposit Fee (if applicable)")
    print("6: View Records")

    try:
        userInput = int(input("Select an option (1-6): "))
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    if userInput == 1:
        Employee()
    elif userInput == 2:
        Customer()
    elif userInput == 3:
        Food()
    elif userInput == 4:
        OrderFood()
    elif userInput == 5:
        feeDeposit()
    elif userInput == 6:
        View()
    else:
        print("Enter a valid choice (1-6).")


def runAgain():
    runAgn = input("\nDo you want to run again? (Y/N): ")
    while runAgn.lower() == 'y':
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')
        MenuSet()
        runAgn = input("\nDo you want to run again? (Y/N): ")
    print("Goodbye! Have a nice day.")


# Run once at start
MenuSet()
runAgain()

