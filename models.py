# Data Model Definitions

from utils.database import db
from datetime import datetime


class User:
    """User model"""

    @staticmethod
    def create(username, email, password_hash, role="user"):
        """Create a new user"""
        query = """
        INSERT INTO users (username, email, password_hash, role, created_at)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (username, email, password_hash, role, datetime.now())
        result = db.execute_update(query, params)
        return result

    @staticmethod
    def find_by_email(email):
        """Find a user by email"""
        query = "SELECT * FROM users WHERE email = %s"
        result = db.execute_query(query, (email,))
        return result[0] if result else None

    @staticmethod
    def find_by_id(user_id):
        """Find a user by ID"""
        query = "SELECT * FROM users WHERE id = %s"
        result = db.execute_query(query, (user_id,))
        return result[0] if result else None

    @staticmethod
    def search(query):
        sql = "SELECT * FROM users WHERE username LIKE %s OR email LIKE %s"
        pattern = f"%{query}%"
        return db.execute_query(sql, (pattern, pattern))


class Book:
    """Book model"""

    @staticmethod
    def get_all(search_title=None, search_author=None):
        """Get all books, with optional search"""
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
        """Find a book by ID"""
        query = "SELECT * FROM books WHERE id = %s"
        result = db.execute_query(query, (book_id,))
        return result[0] if result else None

    @staticmethod
    def create(title, author, description, stock, cover_image_url=None):
        """Create a new book"""
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
        """Update book information"""
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
        """Delete a book"""
        query = "DELETE FROM books WHERE id = %s"
        result = db.execute_update(query, (book_id,))
        return result

    @staticmethod
    def update_stock(book_id, stock_change):
        """Update book stock quantity"""
        query = "UPDATE books SET stock = stock + %s, updated_at = %s WHERE id = %s"
        params = (stock_change, datetime.now(), book_id)
        result = db.execute_update(query, params)
        return result


class BorrowRecord:
    """Borrowing record model"""

    @staticmethod
    def create(user_id, book_id, status="requested", borrow_date=None):
        """Create a borrow record"""
        query = """
        INSERT INTO borrow_records (user_id, book_id, status, borrow_date)
        VALUES (%s, %s, %s, %s)
        """
        params = (user_id, book_id, status, borrow_date)
        result = db.execute_update(query, params)
        return result

    @staticmethod
    def get_by_user(user_id):
        """Get borrowing history by user with book title and author"""
        query = """
        SELECT br.id, br.user_id, br.book_id, br.borrow_date, br.return_date, br.status, 
            b.title, b.author 
        FROM borrow_records br
        JOIN books b ON br.book_id = b.id
        WHERE br.user_id = %s
        ORDER BY br.borrow_date DESC
        """
        result = db.execute_query(query, (user_id,))
        return result or []

    @staticmethod
    def get_all(status=None):
        """Get all borrow records, optionally filtered by status"""
        query = """
        SELECT br.*, b.title, b.author, u.username, u.email 
        FROM borrow_records br 
        JOIN books b ON br.book_id = b.id 
        JOIN users u ON br.user_id = u.id
        """
        params = []

        if status:
            query += " WHERE br.status = %s"
            params.append(status)

        query += " ORDER BY br.borrow_date DESC"
        result = db.execute_query(query, params if params else None)
        return result or []

    @staticmethod
    def update_status(record_id, status, return_date=None):
        """Update the borrow status"""
        if return_date:
            query = (
                "UPDATE borrow_records SET status = %s, return_date = %s WHERE id = %s"
            )
            params = (status, return_date, record_id)
        else:
            query = "UPDATE borrow_records SET status = %s WHERE id = %s"
            params = (status, record_id)

        result = db.execute_update(query, params)
        return result

    @staticmethod
    def find_by_id(record_id):
        """Find a borrow record by ID"""
        query = "SELECT * FROM borrow_records WHERE id = %s"
        result = db.execute_query(query, (record_id,))
        return result[0] if result else None

