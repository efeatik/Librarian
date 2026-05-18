import json
import os
import hashlib
from datetime import datetime, timedelta

class LibrarySystem:
    def __init__(self):
        self.books = {}
        self.users = {}
        self.transactions = []
        self.load_data()
    
    def load_data(self):
        # Kitaplar dosyasını yükle
        if os.path.exists("kitaplar.json"):
            with open("kitaplar.json", "r") as f:
                self.books = json.load(f)
        else:
            # Eğer dosya yoksa, boş bir kitap listesi oluştur
            self.books = {}
            self.save_books()
        
        # Kullanıcılar dosyasını yükle
        if os.path.exists("kullanicilar.json"):
            with open("kullanicilar.json", "r") as f:
                self.users = json.load(f)
        else:
            # Eğer dosya yoksa, root kullanıcıyı oluştur
            self.users = {
                "admin": {
                    "password": self._hash_password("admin123"),
                    "role": "Yönetici"
                }
            }
            self.save_users()
        
        # İşlemler dosyasını yükle
        if os.path.exists("islem.json"):
            with open("islem.json", "r") as f:
                self.transactions = json.load(f)
        else:
            self.transactions = []
            self.save_transactions()

    def _hash_password(self, password):
        # Güvenli SHA-256 şifrelemesi
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def save_books(self):
        with open("kitaplar.json", "w") as f:
            json.dump(self.books, f)

    def save_users(self):
        with open("kullanicilar.json", "w") as f:
            json.dump(self.users, f)

    def save_transactions(self):
        with open("islem.json", "w") as f:
            json.dump(self.transactions, f)

    # Diğer metodlar burada kalır...
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
        self.save_books()

    def update_book(self, isbn, title=None, author=None, stock=None):
        """Kitap bilgilerini günceller."""
        if isbn in self.books:
            if title is not None:
                self.books[isbn]["title"] = title
            if author is not None:
                self.books[isbn]["author"] = author
            if stock is not None:
                self.books[isbn]["stock"] = stock
            self.save_books()

    def delete_book(self, isbn):
        """Kitabı siler."""
        if isbn in self.books:
            del self.books[isbn]
            self.save_books()

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
        self.save_books()
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
        
        self.save_books()
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

    def authenticate_user(self, username, password):
        """Kullanıcı kimlik doğrulaması yapar."""
        if username in self.users:
            stored_hash = self.users[username]["password"]
            if stored_hash == self._hash_password(password):
                return self.users[username]["role"]
        return None

    def create_user(self, admin_username, username, password, role):
        """Yeni kullanıcı oluşturur."""
       
       # Artık personel sadece kullanıcı oluşturabilir, yönetici her türlü kullanıcı oluşturabilir
        creator_role = self.users.get(admin_username, {}).get("role")
        if creator_role == "Yönetici":
            pass  # Yönetici her türlü kullanıcı oluşturabilir
        elif creator_role == "Personel" and role == "Öğrenci":
            pass  # Personel sadece kullanıcı oluşturabilir
        else:
            return False, "Yeterli yetki yok veya geçersiz rol."
        
        if username in self.users:
            return False, "Kullanıcı zaten mevcut."
        
        self.users[username] = {
            "password": self._hash_password(password),
            "role": role
        }
        self.save_users()
        return True, "Kullanıcı başarıyla oluşturuldu."

    def get_all_books(self):
        """Tüm kitapları döndürür."""
        books_list = []
        for isbn, info in self.books.items():
            books_list.append((isbn, info["title"], info["author"], info["stock"]))
        return books_list

    def search_books(self, query):
        """Kitapları arar."""
        results = []
        for isbn, info in self.books.items():
            if (query.lower() in info["title"].lower() or 
                query.lower() in info["author"].lower() or 
                query == isbn):
                results.append((isbn, info["title"], info["author"], info["stock"]))
        return results

    def get_user_transactions(self, username):
        """Kullanıcının tüm işlemlerini döndürür."""
        user_transactions = []
        for transaction in self.transactions:
            if transaction["username"] == username:
                user_transactions.append(transaction)
        return user_transactions

    def get_overdue_books(self):
        """Geçmiş cezalı kitapları döndürür."""
        overdue = []
        current_time = datetime.now()
        for transaction in self.transactions:
            if (not transaction["returned"]):
                due_date = datetime.fromisoformat(transaction["due_date"])
                if current_time > due_date:
                    overdue.append(transaction)
        return overdue
    
    def get_all_overdue_books(self):
        overdue_list = []
        from datetime import datetime
        current_time = datetime.now()
        for t in self.transactions:
            if not t.get("returned", False): # Kitap henüz iade edilmemişse
                due_date = datetime.fromisoformat(t["due_date"])
                if current_time > due_date:
                    overdue_list.append(t)
        return overdue_list