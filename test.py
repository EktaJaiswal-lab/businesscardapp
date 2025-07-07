import mysql.connector
print("➡️ Trying to connect...")

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='ekta',
        database='business_card_db'
    )
    print("✅ Connected to MySQL successfully!")
    conn.close()
except mysql.connector.Error as err:
    print("❌ Failed to connect to MySQL:", err)
