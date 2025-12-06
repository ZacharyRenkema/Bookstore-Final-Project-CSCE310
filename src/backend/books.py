from flask import Blueprint, request, jsonify
from models import db, Book
from utils import get_current_user

books_bp = Blueprint("books", __name__)


@books_bp.route("", methods=["GET"])
def search_books():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    q = request.args.get("q", "").strip()
    query = Book.query

    if q:
        like = f"%{q}%"
        query = query.filter(
            (Book.title.ilike(like)) | (Book.author.ilike(like))
        )

    books = query.all()

    return jsonify([
        {
            "id": b.id,
            "title": b.title,
            "author": b.author,
            "buy_price": float(b.buy_price),
            "rent_price": float(b.rent_price),
        }
        for b in books
    ])


@books_bp.route("", methods=["POST"])
def create_book():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    if user.role != "manager":
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json() or {}
    title = data.get("title", "").strip()
    author = data.get("author", "").strip()
    buy_price = data.get("buy_price")
    rent_price = data.get("rent_price")

    if not title or not author or buy_price is None or rent_price is None:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        buy_price_val = float(buy_price)
        rent_price_val = float(rent_price)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid price values"}), 400

    book = Book(
        title=title,
        author=author,
        buy_price=buy_price_val,
        rent_price=rent_price_val,
    )
    db.session.add(book)
    db.session.commit()

    return jsonify(
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "buy_price": float(book.buy_price),
            "rent_price": float(book.rent_price),
        }
    ), 201


@books_bp.route("/<int:book_id>", methods=["PUT", "PATCH"])
def update_book(book_id: int):
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    if user.role != "manager":
        return jsonify({"error": "Forbidden"}), 403

    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    data = request.get_json() or {}

    title = data.get("title")
    author = data.get("author")
    buy_price = data.get("buy_price")
    rent_price = data.get("rent_price")

    if title is not None:
        title = str(title).strip()
        if title:
            book.title = title
    if author is not None:
        author = str(author).strip()
        if author:
            book.author = author
    if buy_price is not None:
        try:
            book.buy_price = float(buy_price)
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid buy_price"}), 400
    if rent_price is not None:
        try:
            book.rent_price = float(rent_price)
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid rent_price"}), 400

    db.session.commit()

    return jsonify(
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "buy_price": float(book.buy_price),
            "rent_price": float(book.rent_price),
        }
    )
