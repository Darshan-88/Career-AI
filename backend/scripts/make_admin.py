
import sqlite3
from pathlib import Path

DATABASE_PATH = Path("job_intelligence.db")
ADMIN_EMAIL = "darshan.ai.test2026@gmail.com"


def make_admin():
    connection = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE users
            SET role = 'admin'
            WHERE email = ?
            """,
            (ADMIN_EMAIL,),
        )

        connection.commit()

        if cursor.rowcount == 0:
            print("Admin user not found.")
            print("Check whether this email is registered.")
        else:
            print(f"{ADMIN_EMAIL} is now an admin.")

    finally:
        connection.close()


if __name__ == "__main__":
    make_admin()
