
import sqlite3
from pathlib import Path

DATABASE_PATH = Path("job_intelligence.db")


def add_role_column():
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH.resolve()}"
        )

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]

        if not columns:
            raise RuntimeError(
                "The users table does not exist in this database."
            )

        if "role" in columns:
            print("Role column already exists.")
        else:
            cursor.execute(
                """
                ALTER TABLE users
                ADD COLUMN role VARCHAR(20)
                NOT NULL DEFAULT 'user'
                """
            )
            connection.commit()
            print("Role column added successfully.")

    finally:
        connection.close()


if __name__ == "__main__":
    add_role_column()
