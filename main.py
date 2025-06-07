import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    port=3306, # your port number 
    user="root",
    password="" , # your password
    # database = "chatbot"  after creating your database name
)
mycursor = mydb.cursor()
mycursor.execute("CREATE DATABASE chatbot ")
mycursor.execute("""CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100),
    password_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

sqlFormula = "INSERT INTO users(id, username,email,password_hash,created_at) VALUES(%s,%s,%s,%s,%s)"
users = [("1","swathi","swathi@gmail.com","swathi@123"),
         ("2","anu","anu@gmail.com","anu@001"),
         ("3","joe","joe@gmail.com","joe90"),
         ("4","arav","arav@gmail.com","arav@123"),
         ("5","jay","jay@gmail.com","pass@123"),
         ("6","yuvi","yuvi@gmail.com","yuvi009"),
         ("7","karthika","karthika@gmail.com","karthika08"),]
mycursor.executemany(sqlFormula,users)
mydb.commit()

