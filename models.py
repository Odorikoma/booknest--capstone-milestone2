from utils.database import db
from datetime import datetime

# -------------------------
# Users
# -------------------------
class User:
    """User model"""

    @staticmethod
    def create(username, email, password_hash, role="user"):
        """
        与当前 DB 一致：users(username,email,password_hash,role,create_at)
        如果你暂时还想用明文密码，把字段名改回 password 并调整表结构/seed。
        """
        sql = """
        INSERT INTO users (username, email, password_hash, role, create_at)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (username, email, password_hash, role, datetime.now())
        return db.execute_update(sql, params)

    @staticmethod
    def find_by_email(email):
        # 显式选择列并给 password_hash 起别名，避免 KeyError
        sql = """
        SELECT id,
               username,
               email,
               password_hash AS password,
               role,
               create_at
          FROM users
         WHERE email = %s
        """
        rows = db.execute_query(sql, (email,))
        return rows[0] if rows else None

    @staticmethod
    def find_by_id(user_id):
        sql = "SELECT * FROM users WHERE id = %s"
        rows = db.execute_query(sql, (user_id,))
        return rows[0] if rows else None

    @staticmethod
    def search(query):
        sql = "SELECT * FROM users WHERE username LIKE %s OR email LIKE %s"
        pattern = f"%{query}%"
        return db.execute_query(sql, (pattern, pattern))


# -------------------------
# Books
# -------------------------
class Book:
    """Book model"""

    @staticmethod
    def get_all(search_title=None, search_author=None):
        sql = "SELECT * FROM books WHERE 1=1"
        params = []
        if search_title:
            sql += " AND title LIKE %s"
            params.append(f"%{search_title}%")
        if search_author:
            sql += " AND author LIKE %s"
            params.append(f"%{search_author}%")
        sql += " ORDER BY created_at DESC"
        return db.execute_query(sql, params if params else None) or []

    @staticmethod
    def find_by_id(book_id):
        sql = "SELECT * FROM books WHERE id = %s"
        rows = db.execute_query(sql, (book_id,))
        return rows[0] if rows else None

    @staticmethod
    def create(title, author, description, stock, cover_image_url=None, price=0.0):
        sql = """
        INSERT INTO books (title, author, description, stock, cover_image_url, price, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        now = datetime.now()
        params = (title, author, description, stock, cover_image_url, price, now)
        return db.execute_update(sql, params)

    @staticmethod
    def update(book_id, title, author, description, stock, cover_image_url=None, price=0.0):
        sql = """
        UPDATE books
           SET title=%s, author=%s, description=%s, stock=%s,
               cover_image_url=%s, price=%s, created_at=%s
         WHERE id=%s
        """
        params = (title, author, description, stock, cover_image_url, price, datetime.now(), book_id)
        return db.execute_update(sql, params)

    @staticmethod
    def delete(book_id):
        sql = "DELETE FROM books WHERE id = %s"
        return db.execute_update(sql, (book_id,))

    @staticmethod
    def update_stock(book_id, delta):
        sql = "UPDATE books SET stock = stock + %s, created_at = %s WHERE id = %s"
        return db.execute_update(sql, (delta, datetime.now(), book_id))


# -------------------------
# Borrows
# -------------------------
class BorrowRecord:
    """
    与当前 seed/schema 对齐：表名是 `borrows`
    列：id, user_id, book_id, borrow_date, return_date, borrow_status, notes
    """

    @staticmethod
    def create(user_id, book_id, borrow_status="requested", borrow_date=None, notes=None):
        sql = """
        INSERT INTO borrows (user_id, book_id, borrow_date, borrow_status, notes)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (user_id, book_id, borrow_date or datetime.now(), borrow_status, notes)
        return db.execute_update(sql, params)

    @staticmethod
    def get_by_user(user_id):
        sql = """
        SELECT br.id, br.user_id, br.book_id, br.borrow_date, br.return_date, br.borrow_status, br.notes,
               b.title, b.author
          FROM borrows br
          JOIN books b ON br.book_id = b.id
         WHERE br.user_id = %s
         ORDER BY br.borrow_date DESC
        """
        return db.execute_query(sql, (user_id,)) or []

    @staticmethod
    def get_all(borrow_status=None):
        sql = """
        SELECT br.*, b.title, b.author, u.username, u.email
          FROM borrows br
          JOIN books b ON br.book_id = b.id
          JOIN users u ON br.user_id = u.id
        """
        params = []
        if borrow_status:
            sql += " WHERE br.borrow_status = %s"
            params.append(borrow_status)
        sql += " ORDER BY br.borrow_date DESC"
        return db.execute_query(sql, params if params else None) or []

    @staticmethod
    def update_status(record_id, borrow_status, return_date=None, notes=None):
        if return_date is not None and notes is not None:
            sql = "UPDATE borrows SET borrow_status=%s, return_date=%s, notes=%s WHERE id=%s"
            params = (borrow_status, return_date, notes, record_id)
        elif return_date is not None:
            sql = "UPDATE borrows SET borrow_status=%s, return_date=%s WHERE id=%s"
            params = (borrow_status, return_date, record_id)
        elif notes is not None:
            sql = "UPDATE borrows SET borrow_status=%s, notes=%s WHERE id=%s"
            params = (borrow_status, notes, record_id)
        else:
            sql = "UPDATE borrows SET borrow_status=%s WHERE id=%s"
            params = (borrow_status, record_id)
        return db.execute_update(sql, params)

    @staticmethod
    def find_by_id(record_id):
        sql = "SELECT * FROM borrows WHERE id = %s"
        rows = db.execute_query(sql, (record_id,))
        return rows[0] if rows else None


