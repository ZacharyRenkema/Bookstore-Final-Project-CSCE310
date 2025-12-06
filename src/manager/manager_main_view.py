import sys
import requests
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QTabWidget,
    QFormLayout,
)
from PySide6.QtCore import Qt

API_BASE_URL = "http://127.0.0.1:5000"


class ManagerMainView(QMainWindow):
    def __init__(self, username: str, token: str):
        super().__init__()
        self.username = username
        self.token = token
        self.orders_data = []
        self.books_data = []

        self.setWindowTitle(f"Bookstore Manager Dashboard - {username}")
        self.setMinimumSize(1152, 648)

        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(8, 8, 8, 8)
        root_layout.setSpacing(8)

        top_bar = QHBoxLayout()
        title_label = QLabel(f"Manager Dashboard - {username}")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        top_bar.addWidget(title_label, alignment=Qt.AlignLeft)
        top_bar.addStretch()
        root_layout.addLayout(top_bar)

        self.tabs = QTabWidget()
        root_layout.addWidget(self.tabs)

        self.orders_tab = QWidget()
        self.books_tab = QWidget()
        self.tabs.addTab(self.orders_tab, "Orders")
        self.tabs.addTab(self.books_tab, "Books")

        self._setup_orders_tab()
        self._setup_books_tab()

    def _headers(self):
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _setup_orders_tab(self):
        layout = QVBoxLayout(self.orders_tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        controls = QHBoxLayout()
        self.refresh_orders_button = QPushButton("Refresh Orders")
        self.refresh_orders_button.clicked.connect(self.refresh_orders)
        self.mark_paid_button = QPushButton("Mark as Paid")
        self.mark_paid_button.clicked.connect(lambda: self.update_order_status("Paid"))
        self.mark_pending_button = QPushButton("Mark as Pending")
        self.mark_pending_button.clicked.connect(lambda: self.update_order_status("Pending"))
        controls.addWidget(self.refresh_orders_button)
        controls.addStretch()
        controls.addWidget(self.mark_pending_button)
        controls.addWidget(self.mark_paid_button)
        layout.addLayout(controls)

        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(5)
        self.orders_table.setHorizontalHeaderLabels(
            ["Order ID", "Customer", "Status", "Total", "Created At"]
        )
        self.orders_table.horizontalHeader().setStretchLastSection(True)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.orders_table.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self.orders_table)

    def _setup_books_tab(self):
        layout = QVBoxLayout(self.books_tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        top_row = QHBoxLayout()
        self.refresh_books_button = QPushButton("Refresh Books")
        self.refresh_books_button.clicked.connect(self.refresh_books)
        top_row.addWidget(self.refresh_books_button)
        top_row.addStretch()
        layout.addLayout(top_row)

        self.books_table = QTableWidget()
        self.books_table.setColumnCount(4)
        self.books_table.setHorizontalHeaderLabels(
            ["Title", "Author", "Buy Price", "Rent Price"]
        )
        self.books_table.horizontalHeader().setStretchLastSection(True)
        self.books_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.books_table.setSelectionMode(QTableWidget.SingleSelection)
        self.books_table.cellClicked.connect(self.on_book_row_selected)
        layout.addWidget(self.books_table)

        form_layout = QFormLayout()
        self.title_input = QLineEdit()
        self.author_input = QLineEdit()
        self.buy_price_input = QLineEdit()
        self.rent_price_input = QLineEdit()
        form_layout.addRow("Title:", self.title_input)
        form_layout.addRow("Author:", self.author_input)
        form_layout.addRow("Buy Price:", self.buy_price_input)
        form_layout.addRow("Rent Price:", self.rent_price_input)

        form_widget = QWidget()
        form_widget.setLayout(form_layout)
        layout.addWidget(form_widget)

        buttons_row = QHBoxLayout()
        self.add_book_button = QPushButton("Add Book")
        self.add_book_button.clicked.connect(self.create_book)
        self.update_book_button = QPushButton("Update Selected Book")
        self.update_book_button.clicked.connect(self.update_selected_book)
        buttons_row.addWidget(self.add_book_button)
        buttons_row.addWidget(self.update_book_button)
        buttons_row.addStretch()
        layout.addLayout(buttons_row)

    def refresh_orders(self):
        try:
            resp = requests.get(
                f"{API_BASE_URL}/orders",
                headers=self._headers(),
                timeout=5,
            )
        except requests.RequestException as e:
            QMessageBox.critical(self, "Network Error", f"Could not fetch orders:\n{e}")
            return

        if resp.status_code != 200:
            try:
                data = resp.json()
                msg = data.get("error", f"Failed to fetch orders ({resp.status_code}).")
            except Exception:
                msg = f"Failed to fetch orders ({resp.status_code})."
            QMessageBox.warning(self, "Error", msg)
            return

        orders = resp.json()
        self.orders_data = orders
        self.orders_table.setRowCount(len(orders))

        for row, order in enumerate(orders):
            oid = str(order.get("id", ""))
            customer = order.get("customer_username") or ""
            status = order.get("status", "")
            total = f"{order.get('total_amount', 0):.2f}"
            created_at = order.get("created_at") or ""

            self.orders_table.setItem(row, 0, QTableWidgetItem(oid))
            self.orders_table.setItem(row, 1, QTableWidgetItem(customer))
            self.orders_table.setItem(row, 2, QTableWidgetItem(status))
            self.orders_table.setItem(row, 3, QTableWidgetItem(total))
            self.orders_table.setItem(row, 4, QTableWidgetItem(created_at))

    def update_order_status(self, new_status: str):
        selected = self.orders_table.currentRow()
        if selected < 0 or selected >= len(self.orders_data):
            QMessageBox.warning(self, "No Selection", "Please select an order first.")
            return

        order = self.orders_data[selected]
        order_id = order.get("id")

        if order_id is None:
            QMessageBox.warning(self, "Error", "Invalid order selection.")
            return

        try:
            resp = requests.patch(
                f"{API_BASE_URL}/orders/{order_id}/status",
                headers={**self._headers(), "Content-Type": "application/json"},
                json={"status": new_status},
                timeout=5,
            )
        except requests.RequestException as e:
            QMessageBox.critical(self, "Network Error", f"Could not update order:\n{e}")
            return

        if resp.status_code != 200:
            try:
                data = resp.json()
                msg = data.get("error", f"Failed to update order ({resp.status_code}).")
            except Exception:
                msg = f"Failed to update order ({resp.status_code})."
            QMessageBox.warning(self, "Error", msg)
            return

        QMessageBox.information(self, "Success", f"Order {order_id} updated to {new_status}.")
        self.refresh_orders()

    def refresh_books(self):
        try:
            resp = requests.get(
                f"{API_BASE_URL}/books",
                headers=self._headers(),
                timeout=5,
            )
        except requests.RequestException as e:
            QMessageBox.critical(self, "Network Error", f"Could not fetch books:\n{e}")
            return

        if resp.status_code != 200:
            try:
                data = resp.json()
                msg = data.get("error", f"Failed to fetch books ({resp.status_code}).")
            except Exception:
                msg = f"Failed to fetch books ({resp.status_code})."
            QMessageBox.warning(self, "Error", msg)
            return

        books = resp.json()
        self.books_data = books
        self.books_table.setRowCount(len(books))

        for row, book in enumerate(books):
            title = str(book.get("title", ""))
            author = str(book.get("author", ""))
            buy_price = f"{book.get('buy_price', 0):.2f}"
            rent_price = f"{book.get('rent_price', 0):.2f}"

            self.books_table.setItem(row, 0, QTableWidgetItem(title))
            self.books_table.setItem(row, 1, QTableWidgetItem(author))
            self.books_table.setItem(row, 2, QTableWidgetItem(buy_price))
            self.books_table.setItem(row, 3, QTableWidgetItem(rent_price))

    def on_book_row_selected(self, row: int, column: int):
        if row < 0 or row >= len(self.books_data):
            return
        book = self.books_data[row]
        self.title_input.setText(str(book.get("title", "")))
        self.author_input.setText(str(book.get("author", "")))
        self.buy_price_input.setText(str(book.get("buy_price", "")))
        self.rent_price_input.setText(str(book.get("rent_price", "")))

    def create_book(self):
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        buy_price = self.buy_price_input.text().strip()
        rent_price = self.rent_price_input.text().strip()

        if not title or not author or not buy_price or not rent_price:
            QMessageBox.warning(self, "Missing Data", "Please fill in all book fields.")
            return

        try:
            float(buy_price)
            float(rent_price)
        except ValueError:
            QMessageBox.warning(self, "Invalid Data", "Prices must be numeric.")
            return

        try:
            resp = requests.post(
                f"{API_BASE_URL}/books",
                headers={**self._headers(), "Content-Type": "application/json"},
                json={
                    "title": title,
                    "author": author,
                    "buy_price": buy_price,
                    "rent_price": rent_price,
                },
                timeout=5,
            )
        except requests.RequestException as e:
            QMessageBox.critical(self, "Network Error", f"Could not create book:\n{e}")
            return

        if resp.status_code != 201:
            try:
                data = resp.json()
                msg = data.get("error", f"Failed to create book ({resp.status_code}).")
            except Exception:
                msg = f"Failed to create book ({resp.status_code})."
            QMessageBox.warning(self, "Error", msg)
            return

        QMessageBox.information(self, "Success", "Book created.")
        self.refresh_books()

    def update_selected_book(self):
        row = self.books_table.currentRow()
        if row < 0 or row >= len(self.books_data):
            QMessageBox.warning(self, "No Selection", "Please select a book first.")
            return

        book = self.books_data[row]
        book_id = book.get("id")
        if book_id is None:
            QMessageBox.warning(self, "Error", "Invalid book selection.")
            return

        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        buy_price = self.buy_price_input.text().strip()
        rent_price = self.rent_price_input.text().strip()

        payload = {}
        if title:
            payload["title"] = title
        if author:
            payload["author"] = author
        if buy_price:
            try:
                float(buy_price)
                payload["buy_price"] = buy_price
            except ValueError:
                QMessageBox.warning(self, "Invalid Data", "Buy price must be numeric.")
                return
        if rent_price:
            try:
                float(rent_price)
                payload["rent_price"] = rent_price
            except ValueError:
                QMessageBox.warning(self, "Invalid Data", "Rent price must be numeric.")
                return

        if not payload:
            QMessageBox.warning(self, "No Changes", "Nothing to update.")
            return

        try:
            resp = requests.patch(
                f"{API_BASE_URL}/books/{book_id}",
                headers={**self._headers(), "Content-Type": "application/json"},
                json=payload,
                timeout=5,
            )
        except requests.RequestException as e:
            QMessageBox.critical(self, "Network Error", f"Could not update book:\n{e}")
            return

        if resp.status_code != 200:
            try:
                data = resp.json()
                msg = data.get("error", f"Failed to update book ({resp.status_code}).")
            except Exception:
                msg = f"Failed to update book ({resp.status_code})."
            QMessageBox.warning(self, "Error", msg)
            return

        QMessageBox.information(self, "Success", "Book updated.")
        self.refresh_books()

def load_stylesheet(app: QApplication):
    base_dir = Path(__file__).resolve().parent
    style_path = base_dir / "resources" / "style.qss"

    try:
        with style_path.open("r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"style.qss not found at {style_path}, running without custom stylesheet")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    load_stylesheet(app)
    window = ManagerMainView(username="Manager", token="")
    window.show()
    sys.exit(app.exec())
