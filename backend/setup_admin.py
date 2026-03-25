import mysql.connector
from security import hash_password
import os
ADMINS = [
    {"username": "admin", "password": "admin123", "role": "admin"},
    {"username": "manager", "password": "manager123", "role": "editor"},
]

db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=int(os.getenv("DB_PORT", 3306))
)

cursor = db.cursor()

for admin in ADMINS:
    hashed = hash_password(admin["password"])

    cursor.execute(
        "SELECT id FROM admin WHERE username=%s",
        (admin["username"],)
    )

    if cursor.fetchone():
        cursor.execute(
            "UPDATE admin SET password=%s, role=%s WHERE username=%s",
            (hashed, admin["role"], admin["username"])
        )
        print(f"✅ Updated {admin['username']}")
    else:
        cursor.execute(
            "INSERT INTO admin (username, password, role) VALUES (%s, %s, %s)",
            (admin["username"], hashed, admin["role"])
        )
        print(f"✅ Created {admin['username']}")

db.commit()
db.close()
