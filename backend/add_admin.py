import mysql.connector
from security import hash_password
import os
username = input("Username: ")
password = input("Password: ")
role = input("Role (admin/editor): ")
email=input("Email: ")
phone=int(input("Phone: "))
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=int(os.getenv("DB_PORT", 3306))
)
cursor = db.cursor()
cursor.execute(
    "INSERT INTO admin (username, password, role, email, phone) VALUES (%s, %s, %s, %s, %s)",
    (username, hash_password(password), role, email, phone)
)

db.commit()
db.close()
print("✅ Admin added")
