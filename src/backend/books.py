from flask import Blueprint, request, jsonify
from models import Book
from utils import get_current_user  # or wherever you put it

books_bp = Blueprint("books", __name__)


@books_bp.route("", methods=["GET"])
def search_books():
    user = get_current_user()
    print(user)
    print(get_current_user())
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
