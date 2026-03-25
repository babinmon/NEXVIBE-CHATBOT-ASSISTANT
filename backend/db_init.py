from database import get_db

def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        role VARCHAR(20) DEFAULT 'editor',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        email VARCHAR(100),
        phone VARCHAR(20)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faq (
        id INT AUTO_INCREMENT PRIMARY KEY,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        question_clean VARCHAR(255),
        UNIQUE KEY uq_question_clean (question_clean)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS unanswered_questions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        question TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS password_reset_otp (
        id INT AUTO_INCREMENT PRIMARY KEY,
        admin_id INT NOT NULL,
        otp VARCHAR(10) NOT NULL,
        expires_at DATETIME NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (admin_id) REFERENCES admin(id) ON DELETE CASCADE
    )
    """)

    db.commit()
    db.close()
    print("✅ Database initialized successfully")
