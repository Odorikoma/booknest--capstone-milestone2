# Book Management Routing

from flask import Blueprint, request, jsonify
from models import Book
from flask_jwt_extended import jwt_required, get_jwt_identity

books_bp = Blueprint('books', __name__)

@books_bp.route('/api/books', methods=['GET'])
def get_books():
    """Get book list, support search"""
    try:
        # Get query parameters
        title = request.args.get('title')
        author = request.args.get('author')
        
        # Search Books
        books = Book.get_all(search_title=title, search_author=author)
        
        return jsonify({
            'success': True,
            'data': books,
            'message': 'Successfully retrieved book list'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve book list: {str(e)}'
        }), 500

@books_bp.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Get details of a single book"""
    try:
        book = Book.find_by_id(book_id)
        
        if not book:
            return jsonify({
                'success': False,
                'message': 'Book not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': book,
            'message': 'Successfully retrieved book details'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve book details: {str(e)}'
        }), 500

@books_bp.route('/api/books', methods=['POST'])
@jwt_required()
def create_book():
    """Create a new book"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'author', 'description', 'stock']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Create a book
        result = Book.create(
            title=data['title'],
            author=data['author'],
            description=data['description'],
            stock=int(data['stock']),
            cover_image_url=data.get('cover_image_url'),
            price=float(data.get('price', 0.0))
        )
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Book created successfully'
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to create book'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Book creation failed: {str(e)}'
        }), 500

@books_bp.route('/api/books/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id):
    """Update book information"""
    try:
        # Check if book exists
        book = Book.find_by_id(book_id)
        if not book:
            return jsonify({
                'success': False,
                'message': 'Book not found'
            }), 404
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'author', 'description', 'stock']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Update book
        result = Book.update(
            book_id=book_id,
            title=data['title'],
            author=data['author'],
            description=data['description'],
            stock=int(data['stock']),
            cover_image_url=data.get('cover_image_url'),
            price=float(data.get('price', 0.0))
        )
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Book updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update book'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Book update failed: {str(e)}'
        }), 500

@books_bp.route('/api/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    """Delete a book"""
    try:
        # Check if book exists
        book = Book.find_by_id(book_id)
        if not book:
            return jsonify({
                'success': False,
                'message': 'Book not found'
            }), 404
        
        # Delete book
        result = Book.delete(book_id)
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Book deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to delete book'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Book deletion failed: {str(e)}'
        }), 500
