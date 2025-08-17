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
    print(f"\n=== 图书更新API调试 ===")
    print(f"图书ID: {book_id}")
    
    try:
        # Check if book exists
        book = Book.find_by_id(book_id)
        print(f"查找到的图书: {book}")
        
        if not book:
            print("❌ 图书不存在")
            return jsonify({
                'success': False,
                'message': 'Book not found'
            }), 404
        
        data = request.get_json()
        print(f"接收到的数据: {data}")
        
        # Validate required fields
        required_fields = ['title', 'author', 'description', 'stock']
        for field in required_fields:
            if field not in data:
                print(f"❌ 缺少必填字段: {field}")
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        print("✅ 字段验证通过")
        
        # Prepare update parameters
        update_params = {
            'book_id': book_id,
            'title': data['title'],
            'author': data['author'],
            'description': data['description'],
            'stock': int(data['stock']),
            'cover_image_url': data.get('cover_image_url'),
            'price': float(data.get('price', 0.0))
        }
        print(f"更新参数: {update_params}")
        
        # Update book
        print("开始调用 Book.update...")
        result = Book.update(**update_params)
        print(f"Book.update 返回结果: {result} (类型: {type(result)})")
        
        if result:
            print("✅ 更新成功")
            return jsonify({
                'success': True,
                'message': 'Book updated successfully'
            })
        else:
            print("❌ 更新失败，result为False")
            return jsonify({
                'success': False,
                'message': 'Failed to update book'
            }), 500
            
    except Exception as e:
        print(f"❌ 更新过程中发生异常: {str(e)}")
        import traceback
        print("完整错误堆栈:")
        traceback.print_exc()
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
