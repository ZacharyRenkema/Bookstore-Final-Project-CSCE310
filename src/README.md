# Bookstore-Final-Project-CSCE310

An online bookstore system with:

- A **Flask + MySQL backend** providing a REST API
- A **customer desktop GUI** (PySide6, under `src/client_view`)
- A **manager desktop GUI** (PySide6, under `src/manager`)

The system supports customer registration/login, book search, buying and renting books, order creation, bill generation with email notifications, and a manager view for managing books and payment status.

---

## 1. Project Structure

```text
Bookstore-Final-Project-CSCE310/
  scripts/
    run_client.py        # launcher for customer GUI
    run_manager.py       # launcher for manager GUI
  src/
    backend/
      app.py             # Flask app entrypoint
      auth.py            # registration/login + JWT
      books.py           # book search + CRUD
      orders.py          # order creation + manager status updates
      models.py          # SQLAlchemy models (User, Book, Order, OrderItem)
      config.py          # DB + secret configuration
      utils.py           # helper functions (JWT decoding, etc.)
      sql/               # optional SQL schema/seed helpers
    client_view/
      login_view.py      # customer login/registration GUI
      main_view.py       # main customer UI (search, cart, place order)
      user_settings_view.py
      resources/
        style.qss        # shared stylesheet for client GUI
    manager/
      manager_login.py   # manager login GUI
      manager_main_view.py  # manager UI (view/update orders, manage books)
      resources/
        style.qss        # shared stylesheet for manager GUI
  venv/                  # (optional) Python virtual environment
  README.md
  keys.txt               # contains Flask/JWT secrets (referenced by config.py)
