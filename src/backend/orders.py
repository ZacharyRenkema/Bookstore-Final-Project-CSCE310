from flask import Blueprint, request, jsonify
from models import db, Book, Order, OrderItem
from utils import get_current_user
import smtplib
from email.message import EmailMessage

orders_bp = Blueprint("orders", __name__)

SMTP_HOST = "zachary.renkema2005@gmail.com"
SMTP_PORT = 587
SMTP_USER = "zachary.renkema2005@gmail.com"
SMTP_PASS = "moltonmilk123"
SMTP_FROM = SMTP_USER


def compute_order_total(order: Order) -> float:
    return sum(float(item.unit_price) * (item.quantity or 1) for item in order.items)


def serialize_order(order: Order) -> dict:
    total = compute_order_total(order)
    return {
        "id": order.id,
        "user_id": order.user_id,
        "customer_username": order.user.username if order.user else None,
        "customer_email": order.user.email if order.user else None,
        "status": order.status,
        "created_at": order.created_at.isoformat() if order.created_at else None,
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
        "total_amount": float(total),
    }


def send_bill_email(order: Order) -> None:
    user = order.user
    if not user or not user.email:
        return

    total = compute_order_total(order)

    lines = []
    lines.append(f"Order ID: {order.id}")
    lines.append(f"Customer: {user.username} <{user.email}>")
    lines.append(f"Status: {order.status}")
    lines.append("")
    lines.append("Items:")
    for item in order.items:
        title = item.book.title if item.book else ""
        qty = item.quantity or 1
        price = float(item.unit_price)
        lines.append(f"- {title} ({item.kind}) x{qty} @ {price:.2f}")
    lines.append("")
    lines.append(f"Total amount due: {total:.2f}")

    body = "\n".join(lines)

    msg = EmailMessage()
    msg["Subject"] = f"Your Bookstore Order #{order.id}"
    msg["From"] = SMTP_FROM
    msg["To"] = user.email
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
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

    order = Order(user_id=user.id, status="Pending")

    for item in items_data:
        book_id = item.get("book_id") or item.get("id")
        item_kind = item.get("kind") or item.get("type")
        quantity = item.get("quantity", 1)

        try:
            if book_id is not None:
                book_id = int(book_id)
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid book_id type", "item": item}), 400

        if not book_id or item_kind not in ("buy", "rent"):
            return jsonify({"error": "Invalid item data", "item": item}), 400

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid quantity", "item": item}), 400

        if quantity <= 0:
            return jsonify({"error": "Quantity must be positive", "item": item}), 400

        book = Book.query.get(book_id)
        if not book:
            return jsonify({"error": f"Book not found: {book_id}"}), 400

        if item_kind == "buy":
            unit_price = float(book.buy_price)
        else:
            unit_price = float(book.rent_price)

        order_item = OrderItem(
            book_id=book.id,
            kind=item_kind,
            quantity=quantity,
            unit_price=unit_price,
        )
        order.items.append(order_item)

    order.total_amount = compute_order_total(order)

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
        orders = Order.query.order_by(Order.id.desc()).all()
    else:
        orders = (
            Order.query.filter_by(user_id=user.id)
            .order_by(Order.id.desc())
            .all()
        )

    return jsonify([serialize_order(o) for o in orders])


@orders_bp.route("/<int:order_id>/status", methods=["PATCH"])
def update_payment_status(order_id: int):
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