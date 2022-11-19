from flask import Flask,redirect, render_template, request, session, url_for, flash
from werkzeug.utils import secure_filename
from importlib.resources import contents
from tkinter import S
from turtle import title
from pyexpat import model
from sqlalchemy import PrimaryKeyConstraint
import ibm_db
from markupsafe import escape
import os
import requests
import json
url = "https://www.fast2sms.com/dev/bulkV2"

headers = {
 'authorization': 'xe1nQcD4A8tFWRIXHyrhPLqKEl7Zpg9VUCYGd3j5MTiSzO6omNSP2LpXfBuqC5J6kTa04KmIgVZ7GHEA',
 'Content-Type': "application/x-www-form-urlencoded",
 'Cache-Control': "no-cache"
}



app = Flask(__name__)
app.secret_key='oiuytrekjhgfd\\\124!@#$%^'
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=0c77d6f2-5da9-48a9-81f8-86b520b87518.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31198;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=tfc22793;PWD=IGXPWDZrWRG7eqRu","","")
print(conn)
print("connection successful...")


@app.route('/')
def home(): 
    message = "TEAM ID : PNT2022TMID29830" +" "+ "BATCH ID : B1-1M3E "
    return render_template('index.html',mes=message)

@app.route('/login', methods=['GET','POST'])
def login():
    return render_template('login.html')


@app.route('/register', methods = ['GET','POST'])
def register():
    return render_template('register.html')


@app.route('/customize')
def customize():
    return render_template('customize.html')
  
    

@app.route('/dashboardsk')
def dashboardsk():
    return render_template('dashboardsk.html')

@app.route('/changepass', methods = ['GET','POST'])
def changepass():
    return render_template('changepassword.html')




@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        
        name = request.form['name']
        email = request.form['email']
        phonenumber = request.form['phonenumber']
        password = request.form['password']
       
        

        sql = "SELECT * FROM shopkeeper WHERE email=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
         return render_template('index.html', msg="You are already a member, please login using your details....")
      
        else:
            insert_sql = f"INSERT INTO shopkeeper VALUES (?,?,?,?);"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, name)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, phonenumber)
            ibm_db.bind_param(prep_stmt, 4, password)
            ibm_db.execute(prep_stmt)
            return render_template('login.html', msg="User Data saved successfuly..")

          
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        
        productid= request.form['product_id']
        productname= request.form['product_name']
        quantity = request.form['quantity']
        price= request.form['price']
       
        
        insert_sql = f"INSERT INTO inventory VALUES (?,?,?,?);"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, productid)
        ibm_db.bind_param(prep_stmt, 2, productname)
        ibm_db.bind_param(prep_stmt, 3, quantity)
        ibm_db.bind_param(prep_stmt, 4, price)
        ibm_db.execute(prep_stmt)
        return redirect(url_for('customize'))

@app.route('/delete',methods=['GET', 'POST'])
def delete():
    if request.method =='POST':
        productid= request.form['productid']
        sql = f"SELECT * FROM inventory WHERE productid = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,productid)
        cusdel = ibm_db.execute(stmt)

    if cusdel:
        sql = f"delete from inventory where productid = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,productid)
        ibm_db.execute(stmt)
        return redirect(url_for("customize"))

def executeCountQuery(tableName,columnName):
    sql = "SELECT COUNT("+columnName+") FROM "+ tableName
    stmt=ibm_db.exec_immediate(conn,sql)
    count_id=ibm_db.fetch_both(stmt)
    return count_id.get('1')

@app.route('/dashboard')
def dashboard():
      
       sql = "SELECT COUNT(productid) FROM inventory where quantity <= 3"
       stmt=ibm_db.exec_immediate(conn,sql)
       count_id=ibm_db.fetch_both(stmt)
       print(count_id)
       data = {
        'totalcount' : executeCountQuery("inventory","productid"),
        'customer' : executeCountQuery("shopkeeper","email"),
        'lowstocks' : count_id.get('1')
       }
       return render_template('dashboard.html', data = data)


@app.route('/update',methods=['GET', 'POST'])
def update():
    
    if request.method == 'POST':
            productid = request.form["productid"]
            quantity = request.form["quantity"]
            sql="SELECT quantity FROM inventory WHERE productid = "+productid
            stmt = ibm_db.exec_immediate(conn,sql)
            oldQuantity=ibm_db.fetch_both(stmt).get('QUANTITY')
            newQuantity= int(quantity) + oldQuantity
            sql  = "UPDATE inventory SET quantity=? WHERE productid = ?"
            stmt = ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,newQuantity)
            ibm_db.bind_param(stmt,2,productid)
            ibm_db.execute(stmt)
            flash("Updated Successfully")
            return redirect(url_for('customize'))



@app.route('/lowstocksdis')
def lowstocksdis():
    lowstocksdis= []
    sql = "SELECT * FROM inventory WHERE quantity<=3"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    
    while dictionary != False:
        lowstocksdis.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
        print(dictionary)

    if lowstocksdis:
        sql = "SELECT * FROM inventory"
        stmt = ibm_db.exec_immediate(conn, sql)
        user = ibm_db.fetch_both(stmt)
    return render_template('lowstocks.html', lowstocksdis = lowstocksdis) 

@app.route('/forget', methods=['GET', 'POST'])
def forget():
    if request.method == 'POST':
        cm = request.form["Email"]
        cp = request.form["oldpassword"]
        co = request.form["newpass"]
        sql = "UPDATE retailer   SET password= ? WHERE email = ?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,co)
        ibm_db.bind_param(stmt,2,cm)
        ibm_db.execute(stmt)
        return redirect(url_for('home'))




@app.route('/signin', methods=['GET', 'POST'])
def signin():
    app.secret_key='oiuytrekjhgfd\\\124!@#$%^'
    if request.method == 'POST':
        mail = request.form['em']
        password = request.form['pass']
        print(mail, password)
        
        sql = f"select * from retailer where email='{escape(mail)}' and password= '{escape(password)}'"
        stmt = ibm_db.exec_immediate(conn, sql)
        data = ibm_db.fetch_both(stmt)
            
        if data:
            session["email"] = escape(mail)
            session["password"] = escape(password)
            return redirect(url_for('dashboard'))

        else:
             return redirect(url_for("login",msg = "Account does not exits or invalid"))

@app.route('/signinsk', methods=['GET', 'POST'])
def signinsk():
    
    app.secret_key='oiuytrekjhgfd\\\124!@#$%^'
    if request.method == 'POST':
        mail = request.form['em']
        password = request.form['pass']
          
        
        sql = f"select * from shopkeeper where email='{escape(mail)}' and password= '{escape(password)}'"
        stmt = ibm_db.exec_immediate(conn, sql)
        data = ibm_db.fetch_both(stmt)
            
        if data:
            session["email"] = escape(mail)
            session["password"] = escape(password)
            return redirect(url_for('dashboardsk'))

        else:
            return redirect(url_for("login",msg = "Account does not exits or invalid"))

@app.route('/inventory')
def inventory():
    inventory = []
    
    sql = "SELECT * FROM INVENTORY "
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
        inventory.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)

    if inventory:
        sql = "SELECT * FROM INVENTORY"
        stmt = ibm_db.exec_immediate(conn, sql)
        user = ibm_db.fetch_both(stmt)
    length=len(inventory)
    alertmessage=''
    lowStockItemsString = ""
    for i in inventory:
        if i[2] == 1 :
            lowStockItemsString = lowStockItemsString + i[1]+"  "
    print(lowStockItemsString)     
    my_data = {
            # Your default Sender ID
            'sender_id': 'FTWSMS',

            # Put your message here!
            'message': 'low stocks on following items'+ lowStockItemsString,
        
            'language': 'english',
            'route': 'p',
        
            # You can send sms to multiple numbers
            # separated by comma.
                
            'numbers': '6385517795'
            }
    response = requests.request("POST",url,data = my_data,headers = headers)
    #load json data from sourc
    returned_msg = json.loads(response.text)

    # print the send message
    print(returned_msg['message'])
    return render_template('inventory.html', inventory = inventory) 

@app.route('/customer')
def customer():
    customer = []
    sql = f"SELECT NAME FROM SHOPKEEPER"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
        customer.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)

    if customer:
        sql = f"SELECT NAME FROM SHOPKEEPER"
        stmt = ibm_db.exec_immediate(conn, sql)
        user = ibm_db.fetch_both(stmt)
    return render_template('customers.html', customer = customer)      



if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)
