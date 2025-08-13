from utils.database import db
from datetime import datetime

class User:
    """User model"""

    @staticmethod
    def create(username, email, password, role="user"):
        query = """
        INSERT INTO users (username, email, password, role, created_at)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (username, email, password, role, datetime.now())
        result = db.execute_update(query, params)
        return result

    @staticmethod
    def find_by_email(email):
        query = "SELECT * FROM users WHERE email = %s"
        result = db.execute_query(query, (email,))
        return result[0] if result else None

    @staticmethod
    def find_by_id(user_id):
        query = "SELECT * FROM users WHERE id = %s"
        result = db.execute_query(query, (user_id,))
        return result[0] if result else None


class Book:
    """Book model"""

    @staticmethod
    def get_all(search_title=None, search_author=None):
        query = "SELECT * FROM books WHERE 1=1"
        params = []

        if search_title:
            query += " AND title LIKE %s"
            params.append(f"%{search_title}%")

        if search_author:
            query += " AND author LIKE %s"
            params.append(f"%{search_author}%")

        query += " ORDER BY created_at DESC"
        result = db.execute_query(query, params if params else None)
        return result or []

    @staticmethod
    def find_by_id(book_id):
        query = "SELECT * FROM books WHERE id = %s"
        result = db.execute_query(query, (book_id,))
        return result[0] if result else None

    @staticmethod
    def create(title, author, description, stock, cover_image_url=None):
        query = """
        INSERT INTO books (title, author, description, stock, cover_image_url, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        now = datetime.now()
        params = (title, author, description, stock, cover_image_url, now, now)
        result = db.execute_update(query, params)
        return result

    @staticmethod
    def update(book_id, title, author, description, stock, cover_image_url=None):
        query = """
        UPDATE books 
        SET title = %s, author = %s, description = %s, stock = %s, 
            cover_image_url = %s, updated_at = %s 
        WHERE id = %s
        """
        params = (
            title,
            author,
            description,
            stock,
            cover_image_url,
            datetime.now(),
            book_id,
        )
        result = db.execute_update(query, params)
        return result

    @staticmethod
    def delete(book_id):
        query = "DELETE FROM books WHERE id = %s"
        result = db.execute_update(query, (book_id,))
        return result

    @staticmethod
    def update_stock(book_id, stock_change):
        query = "UPDATE books SET stock = stock + %s, updated_at = %s WHERE id = %s"
        params = (stock_change, datetime.now(), book_id)
        result = db.execute_update(query, params)
        return result

