import json
import hashlib
import os
from datetime import datetime, timedelta

class LibrarySystem:
    def __init__(self, users_file="kullanicilar.json", books_file="kitaplar.json", transactions_file="islemler.json"):
        self.users_file = users_file
        self.books_file = books_file
        self.transactions_file = transactions_file
        self.users = {}  # Kullanıcılar: username -> {password, role}
        self.books = {}  # Kitaplar: isbn -> {title, author, stock, ...}
        self.transactions = []  # İşlemler: list of {username, isbn, borrow_date, due_date}
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
                "9780134685991": {
                    "title": "Effective Java",
                    "author": "Joshua Bloch",
                    "stock": 3
                },
                "9780596009205": {
                    "title": "JavaScript: The Good Parts",
                    "author": "Douglas Crockford",
                    "stock": 2
                },
                "9780131103627": {
                    "title": "Design Patterns",
                    "author": "Gang of Four",
                    "stock": 1
                }
            }
            self.save_data()

        # İşlemler dosyasını yükle
        if os.path.exists(self.transactions_file):
            with open(self.transactions_file, 'r', encoding='utf-8') as f:
                self.transactions = json.load(f)
        else:
            self.transactions = []
            self.save_data()

    def save_data(self):
        """Verileri JSON dosyalarına yazar."""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=4)
        with open(self.books_file, 'w', encoding='utf-8') as f:
            json.dump(self.books, f, ensure_ascii=False, indent=4)
        with open(self.transactions_file, 'w', encoding='utf-8') as f:
            json.dump(self.transactions, f, ensure_ascii=False, indent=4)

    def _hash_password(self, password):
        """SHA-256 ile şifre hash'ler."""
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate_user(self, username, password):
        """Kullanıcı kimlik doğrulaması yapar."""
        hashed_password = self._hash_password(password)
        user = self.users.get(username)
        if user and user.get("password") == hashed_password:
            return user.get("role")
        return None

    def get_all_books(self):
        """Tüm kitapları döndürür."""
        return list(self.books.values())

    def search_books(self, query):
        """Kitapları başlık veya yazarına göre arar."""
        query = query.lower()
        results = []
        for isbn, book in self.books.items():
            if (query in book["title"].lower() or 
                query in book["author"].lower()):
                book_copy = book.copy()
                book_copy["isbn"] = isbn
                results.append(book_copy)
        return results

    def get_book_by_isbn(self, isbn):
        """ISBN ile kitabı döndürür."""
        return self.books.get(isbn)

    def add_book(self, isbn, title, author, stock):
        """Yeni kitap ekler."""
        self.books[isbn] = {
            "title": title,
            "author": author,
            "stock": stock
        }
        self.save_data()

    def update_book(self, isbn, title=None, author=None, stock=None):
        """Kitap bilgilerini günceller."""
        if isbn in self.books:
            if title is not None:
                self.books[isbn]["title"] = title
            if author is not None:
                self.books[isbn]["author"] = author
            if stock is not None:
                self.books[isbn]["stock"] = stock
            self.save_data()

    def delete_book(self, isbn):
        """Kitabı siler."""
        if isbn in self.books:
            del self.books[isbn]
            self.save_data()

    def borrow_book(self, username, isbn):
        """Kitap ödünç alır."""
        # Kitap yoksa veya stok yoksa
        if isbn not in self.books:
            return False, "Kitap bulunamadı."
        book = self.books[isbn]
        if book["stock"] <= 0:
            return False, "Kitap stokta yok."
        
        # Kullanıcının geçici cezalı olup olmadığını kontrol et
        overdue_books = self.get_user_overdue_books(username)
        if overdue_books:
            return False, "Geçici cezalısınız. Geçmiş cezalı kitapları iade edin."

        # Yeni işlem oluştur
        borrow_date = datetime.now().isoformat()
        due_date = (datetime.now() + timedelta(days=15)).isoformat()  # 15 gün ödünç
        
        transaction = {
            "username": username,
            "isbn": isbn,
            "borrow_date": borrow_date,
            "due_date": due_date,
            "returned": False
        }
        
        self.transactions.append(transaction)
        book["stock"] -= 1
        self.save_data()
        return True, "Kitap başarıyla ödünç alındı."

    def return_book(self, username, isbn):
        """Kitap iade eder."""
        # Kitap yoksa
        if isbn not in self.books:
            return False, "Kitap bulunamadı."
        
        # İşlemi bul
        transaction = None
        for t in self.transactions:
            if (t["username"] == username and 
                t["isbn"] == isbn and 
                not t["returned"]):
                transaction = t
                break
        
        if not transaction:
            return False, "Bu kitap ödünç alınmamış veya zaten iade edilmiş."
        
        # Kitabı iade et
        book = self.books[isbn]
        book["stock"] += 1
        
        # İşlemi iade edildi olarak işaretle
        transaction["returned"] = True
        transaction["return_date"] = datetime.now().isoformat()
        
        self.save_data()
        return True, "Kitap başarıyla iade edildi."

    def get_user_overdue_books(self, username):
        """Kullanıcının geçici cezalı kitaplarını döndürür."""
        overdue = []
        current_time = datetime.now()
        for transaction in self.transactions:
            if (transaction["username"] == username and 
                not transaction["returned"]):
                due_date = datetime.fromisoformat(transaction["due_date"])
                if current_time > due_date:
                    overdue.append(transaction)
        return overdue

    def get_user_active_loans(self, username):
        """Kullanıcının aktif ödünç alım işlemlerini döndürür."""
        active = []
        for transaction in self.transactions:
            if (transaction["username"] == username and 
                not transaction["returned"]):
                active.append(transaction)
        return active

    def get_user_transaction_history(self, username):
        """Kullanıcının işlem geçmişini döndürür."""
        history = []
        for transaction in self.transactions:
            if transaction["username"] == username:
                history.append(transaction)
        return history

    def get_user_role(self, username):
        """Kullanıcının rolünü döndürür."""
        return self.users.get(username, {}).get("role")

    def create_user(self, creator_role, new_username, new_password, new_role):
        """Yeni kullanıcı oluşturur ve RBAC kontrolü yapar."""
        # RBAC kontrolü
        if creator_role == "Yönetici":
            # Yönetici tüm rolleri oluşturabilir
            if new_role not in ["Yönetici", "Personel", "Öğrenci"]:
                return False, "Geçersiz rol."
        elif creator_role == "Personel":
            # Personel sadece Öğrenci rolünü oluşturabilir
            if new_role != "Öğrenci":
                return False, "Yetkisiz işlem."
        else:
            return False, "Yetkisiz işlem."
        
        # Kullanıcı adının benzersiz olup olmadığını kontrol et
        if new_username in self.users:
            return False, "Kullanıcı zaten var."
        
        # Yeni kullanıcıyı oluştur
        hashed_password = self._hash_password(new_password)
        self.users[new_username] = {
            "password": hashed_password,
            "role": new_role
        }
        self.save_data()
        return True, "Kullanıcı başarıyla oluşturuldu."