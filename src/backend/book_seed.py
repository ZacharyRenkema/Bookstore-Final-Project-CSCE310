import random

from app import create_app
from models import db, Book


# A mix of fiction, non-fiction, and tech titles with plausible authors.
BOOK_DATA = [
    ("Edge of the Tides", "Marisa Holloway"),
    ("Fragments of Yesterday", "Daniel K. Mercer"),
    ("The Last Station North", "Irene Caldwell"),
    ("Glass Cities", "Noah Feldman"),
    ("Patterns in the Dust", "Alicia Navarro"),
    ("A Theory of Small Wins", "Christopher Lang"),
    ("Quiet Maps", "Elena Duarte"),
    ("Winter at Harbor Street", "Jonas Whitaker"),
    ("Learning Data Structures in Python", "Priya Raman"),
    ("Networking Essentials", "Caleb J. Park"),
    ("Clean Web APIs", "Sandra Liu"),
    ("Algorithms in Plain English", "Mark R. Jensen"),
    ("Ordinary Days, Strange Weather", "Leah Monroe"),
    ("Coffee on the Third Floor", "Nathan Cole"),
    ("The Narrow Bridge", "Helena Abramov"),
    ("Midnight Shift at Gate 12", "Robert Castillo"),
    ("When the Lights Stayed Red", "Isabel Mendez"),
    ("Stories We Never Sent", "Julian Rivers"),
    ("Analog Machines", "Thomas ORourke"),
    ("A Short Guide to Databases", "Reena Shah"),
    ("Practical MySQL for Projects", "Gavin Holbrook"),
    ("Designing Desktop Interfaces", "Clara Novak"),
    ("Event-Driven Systems", "Hassan El-Amin"),
    ("Conversations in Empty Rooms", "Mira Gallagher"),
    ("A Field Guide to Side Projects", "Owen McKay"),
    ("Overcast Mornings", "Lena Duarte"),
    ("Five Stops from Home", "Joel Herrera"),
    ("Signal and Noise", "Anya Sokolov"),
    ("Rentals, Returns, and Receipts", "Martin Blake"),
    ("The Bookshop on Alder Lane", "Emily Tran"),
]


def generate_prices():
    """
    Generate a buy and rent price that look reasonable:
    - buy: between 9.99 and 39.99
    - rent: roughly 3050% of buy price
    """
    buy_price = round(random.uniform(9.99, 39.99), 2)
    factor = random.uniform(0.3, 0.5)
    rent_price = round(buy_price * factor, 2)
    return buy_price, rent_price


def main():
    app = create_app()
    with app.app_context():
        print("Seeding books...")

        for title, author in BOOK_DATA:
            # Check for existing book with same title + author to avoid duplicates
            existing = Book.query.filter_by(title=title, author=author).first()
            if existing:
                print(f"Skipping existing book: {title} by {author}")
                continue

            buy_price, rent_price = generate_prices()

            book = Book(
                title=title,
                author=author,
                buy_price=buy_price,
                rent_price=rent_price,
            )
            db.session.add(book)
            print(f"Added: {title} by {author} (buy {buy_price}, rent {rent_price})")

        db.session.commit()
        print("Done.")


if __name__ == "__main__":
    main()
