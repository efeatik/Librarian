# backend.py

import json
import hashlib
import os
from datetime import datetime, timedelta

class LibrarySystem:
    def __init__(self, users_file="kullanicilar.json", books_file="kitaplar.json"):
        self.users_file = users_file
        self.books_file = books_file
        self.users = {}  # Kullanıcılar: username -> {password, role}
        self.books = {}  # Kitaplar: isbn -> {title, author, stock, ...}
        self.load_data()

    def load_data(self):
        """JSON dosyalarından verileri yükler."""
        # Kullanıcılar dosyasını yükle
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r', encoding='utf-8') as f:
                self.users = json.load(f)
        else:
            # Varsayılan kullanıcılar (örnek)
            self.users = {
                "admin": {
                    "password": self._hash_password("admin123"),
                    "role": "Yönetici"
                },
                "personel": {
                    "password": self._hash_password("personel123"),
                    "role": "Personel"
                },
                "ogrenci": {
                    "password": self._hash_password("ogrenci123"),
                    "role": "Öğrenci"
                }
            }
            self.save_data()

        # Kitaplar dosyasını yükle
        if os.path.exists(self.books_file):
            with open(self.books_file, 'r', encoding='utf-8') as f:
                self.books = json.load(f)
        else:
            # Varsayılan kitaplar
            self.books = {
                "978-01": {
                    "title": "İnsanlığımı Yitirirken",
                    "author": "Osamu Dazai",
                    "stock": 3,
                    "category": "Roman"
                },
                "978-02": {
                    "title": "Yeraltından Notlar",
                    "author": "Dostoyevski",
                    "stock": 5,
                    "category": "Roman"
                },
                "978-03": {
                    "title": "Budala",
                    "author": "Dostoyevski",
                    "stock": 2,
                    "category": "Roman"
                },
                "978-04": {
                    "title": "Beyaz Geceler",
                    "author": "Dostoyevski",
                    "stock": 0,
                    "category": "Roman"
                },
                "978-05": {
                    "title": "Öteki",
                    "author": "Dostoyevski",
                    "stock": 1,
                    "category": "Roman"
                }
            }
            self.save_data()

    def save_data(self):
        """Verileri JSON dosyalarına yazar."""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=4)
        with open(self.books_file, 'w', encoding='utf-8') as f:
            json.dump(self.books, f, ensure_ascii=False, indent=4)

    def _hash_password(self, password):
        """SHA-256 ile şifre hash'ler."""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def authenticate_user(self, username, password):
        """
        Kullanıcı kimlik doğrulaması yapar.
        Returns: role string if successful, None otherwise.
        """
        if username in self.users:
            stored_hash = self.users[username]["password"]
            input_hash = self._hash_password(password)
            if stored_hash == input_hash:
                return self.users[username]["role"]
        return None

    def get_all_books_as_list(self):
        """
        Kitapları list formatında döndürür.
        Format: [[isbn, title, author, stock, status], ...]
        """
        book_list = []
        for isbn, book in self.books.items():
            stock = book["stock"]
            status = "Müsait" if stock > 0 else "Ödünç Verildi"
            book_list.append([
                isbn,
                book["title"],
                book["author"],
                str(stock),
                status
            ])
        return book_list

    def search_books(self, query):
        """
        Kitapları başlık, yazar veya ISBN'a göre arar.
        KMP algoritması yerine Python'un optimize edilmiş 'in' operatörü kullanılır.
        """
        results = []
        query = query.lower()
        for isbn, book in self.books.items():
            if (query in isbn.lower() or
                query in book["title"].lower() or
                query in book["author"].lower()):
                stock = book["stock"]
                status = "Müsait" if stock > 0 else "Ödünç Verildi"
                results.append([
                    isbn,
                    book["title"],
                    book["author"],
                    str(stock),
                    status
                ])
        return results

    def get_book_by_isbn(self, isbn):
        """ISBN'e göre tek bir kitap döndürür."""
        return self.books.get(isbn)

    def add_book(self, isbn, title, author, stock=0, category=""):
        """Yeni kitap ekler."""
        if isbn in self.books:
            return False  # ISBN zaten var
        self.books[isbn] = {
            "title": title,
            "author": author,
            "stock": stock,
            "category": category
        }
        self.save_data()
        return True

    def update_book(self, isbn, title=None, author=None, stock=None, category=None):
        """Kitap bilgilerini günceller."""
        if isbn not in self.books:
            return False
        book = self.books[isbn]
        if title is not None:
            book["title"] = title
        if author is not None:
            book["author"] = author
        if stock is not None:
            book["stock"] = stock
        if category is not None:
            book["category"] = category
        self.save_data()
        return True

    def delete_book(self, isbn):
        """Kitabı siler."""
        if isbn in self.books:
            del self.books[isbn]
            self.save_data()
            return True
        return False

    def borrow_book(self, user_id, isbn):
        """
        Kitap ödünç verilir.
        Returns: True if successful, False otherwise.
        """
        if isbn not in self.books:
            return False
        book = self.books[isbn]
        if book["stock"] <= 0:
            return False  # Stok yok
        book["stock"] -= 1
        self.save_data()
        return True

    def return_book(self, user_id, isbn):
        """
        Kitap iade edilir.
        Returns: True if successful, False otherwise.
        """
        if isbn not in self.books:
            return False
        book = self.books[isbn]
        book["stock"] += 1
        self.save_data()
        return True

    def get_user_role(self, username):
        """Kullanıcının rolünü döndürür."""
        return self.users.get(username, {}).get("role")