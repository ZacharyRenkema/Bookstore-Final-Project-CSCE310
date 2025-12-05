from flask import Blueprint, request, jsonify
from models import db, Book, Order, OrderItem
from utils import get_current_user
from datetime import datetime, timezone
import os
import smtplib
from email.message import EmailMessage

orders_bp = Blueprint("orders", __name__)


def serialize_order(order):
    return {
        "id": order.id,
        "user_id": order.user_id,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "status": order.status,
        "total_amount": float(order.total_amount) if getattr(order, "total_amount", None) is not None else None,
        "items": [
            {
                "id": item.id,
                "book_id": item.book_id,
                "title": item.book.title if item.book else None,
                "author": item.book.author if item.book else None,
                "kind": item.kind,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
            }
            for item in order.items
        ],
    }


def send_bill_email(order):
    user = order.user
    if not user or not user.email:
        return
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    from_addr = os.getenv("SMTP_FROM", smtp_user or "no-reply@example.com")
    if not smtp_host or not smtp_user or not smtp_pass:
        return
    lines = []
    lines.append(f"Order ID: {order.id}")
    lines.append(f"Customer: {user.username} <{user.email}>")
    lines.append(f"Status: {order.status}")
    lines.append("")
    lines.append("Items:")
    for item in order.items:
        title = item.book.title if item.book else ""
        kind = item.kind
        qty = item.quantity
        price = float(item.unit_price)
        lines.append(f"- {title} ({kind}) x {qty} @ {price:.2f}")
    lines.append("")
    lines.append(f"Total: {float(order.total_amount):.2f}")
    body = "\n".join(lines)
    msg = EmailMessage()
    msg["Subject"] = f"Your Bookstore Order #{order.id}"
    msg["From"] = from_addr
    msg["To"] = user.email
    msg.set_content(body)
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
    except Exception:
        return


@orders_bp.route("", methods=["POST"])
def create_order():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    items_data = data.get("items") or []

    if not items_data:
        return jsonify({"error": "No items provided"}), 400

    books_map = {}
    order_items = []
    total = 0.0

    for item in items_data:
        book_id = item.get("book_id")
        kind = item.get("kind")
        quantity = item.get("quantity", 1)

        if not book_id or kind not in ("buy", "rent"):
            return jsonify({"error": "Invalid item data"}), 400

        if quantity <= 0:
            return jsonify({"error": "Quantity must be positive"}), 400

        if book_id not in books_map:
            book = Book.query.get(book_id)
            if not book:
                return jsonify({"error": f"Book not found: {book_id}"}), 400
            books_map[book_id] = book
        else:
            book = books_map[book_id]

        if kind == "buy":
            unit_price = float(book.buy_price)
        else:
            unit_price = float(book.rent_price)

        line_total = unit_price * quantity
        total += line_total

        oi = OrderItem(
            book_id=book.id,
            quantity=quantity,
            kind=kind,
            unit_price=unit_price,
        )

        order_items.append(oi)

    order = Order(
        user_id=user.id,
        created_at=datetime.now(timezone.utc),
        status="Pending",
        total_amount=total,
    )

    for oi in order_items:
        order.items.append(oi)

    db.session.add(order)
    db.session.commit()

    send_bill_email(order)

    return jsonify(serialize_order(order)), 201


@orders_bp.route("", methods=["GET"])
def list_orders():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if user.role == "manager":
        orders = Order.query.order_by(Order.created_at.desc()).all()
    else:
        orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()

    return jsonify([serialize_order(o) for o in orders])


@orders_bp.route("/<int:order_id>/status", methods=["PATCH"])
def update_status(order_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if user.role != "manager":
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json() or {}
    new_status = data.get("status")

    if new_status not in ("Pending", "Paid"):
        return jsonify({"error": "Invalid status"}), 400

    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    order.status = new_status
    db.session.commit()

    return jsonify(serialize_order(order))
