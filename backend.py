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
        if os.path.exists("kitaplar.json"):
            with open("kitaplar.json", "r") as f:
                self.books = json.load(f)
        else:
            self.books = {}
            self.save_books()
        
        if os.path.exists("kullanicilar.json"):
            with open("kullanicilar.json", "r") as f:
                self.users = json.load(f)
        else:
            self.users = {
                "admin": {
                    "password": self._hash_password("admin123"),
                    "role": "Yönetici"
                }
            }
            self.save_users()
        
        if os.path.exists("islem.json"):
            with open("islem.json", "r") as f:
                self.transactions = json.load(f)
        else:
            self.transactions = []
            self.save_transactions()

    def _hash_password(self, password):
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

    def get_book_by_isbn(self, isbn):
        return self.books.get(isbn)

    def add_book(self, isbn, title, author, stock):
        self.books[isbn] = {
            "title": title,
            "author": author,
            "stock": stock
        }
        self.save_books()

    def update_book(self, isbn, title=None, author=None, stock=None):
        if isbn in self.books:
            if title is not None: self.books[isbn]["title"] = title
            if author is not None: self.books[isbn]["author"] = author
            if stock is not None: self.books[isbn]["stock"] = stock
            self.save_books()

    def delete_book(self, isbn):
        if isbn in self.books:
            del self.books[isbn]
            self.save_books()

    # --- GÜNCELLENEN FONKSİYON: DİREKT ALMAK YERİNE TALEP OLUŞTURUR ---
    def borrow_book(self, username, isbn):
        if isbn not in self.books:
            return False, "Kitap bulunamadı."
        book = self.books[isbn]
        if book["stock"] <= 0:
            return False, "Kitap stokta yok."
        
        overdue_books = self.get_user_overdue_books(username)
        if overdue_books:
            return False, "Geçici cezalısınız. Lütfen önce geciken kitapları iade edin."

        # Stok düşmüyoruz, sadece talep oluşturuyoruz. Benzersiz ID atıyoruz.
        transaction = {
            "id": str(datetime.now().timestamp()), 
            "username": username,
            "isbn": isbn,
            "request_date": datetime.now().isoformat(),
            "borrow_date": None, # Onaylandığında dolacak
            "due_date": None,    # Onaylandığında dolacak
            "status": "Bekliyor" # YENİ DURUM YAPISI
        }
        
        self.transactions.append(transaction)
        self.save_transactions()
        return True, "Talep gönderildi. Personel onayı bekleniyor."

    # --- YENİ FONKSİYON: TALEBİ ONAYLA ---
    def approve_request(self, transaction_id):
        for t in self.transactions:
            if t.get("id") == transaction_id and t.get("status") == "Bekliyor":
                book = self.books.get(t["isbn"])
                if book and book["stock"] > 0:
                    book["stock"] -= 1 # Stok şimdi düşüyor
                    t["status"] = "Onaylandı"
                    t["borrow_date"] = datetime.now().isoformat()
                    t["due_date"] = (datetime.now() + timedelta(days=15)).isoformat()
                    self.save_books()
                    self.save_transactions()
                    return True, "Talep onaylandı."
                else:
                    return False, "Onay başarısız: Stok yetersiz."
        return False, "Talep bulunamadı veya zaten işlenmiş."

    # --- YENİ FONKSİYON: TALEBİ REDDET ---
    def reject_request(self, transaction_id):
        for t in self.transactions:
            if t.get("id") == transaction_id and t.get("status") == "Bekliyor":
                t["status"] = "Reddedildi"
                self.save_transactions()
                return True, "Talep reddedildi."
        return False, "Talep bulunamadı."

    # --- YENİ FONKSİYON: BEKLEYEN TALEPLERİ GETİR ---
    def get_pending_requests(self):
        return [t for t in self.transactions if t.get("status") == "Bekliyor"]

    # --- GÜNCELLENEN FONKSİYON: İADE SADECE 'ONAYLANDI' İSE YAPILABİLİR ---
    def return_book(self, username, isbn):
        if isbn not in self.books:
            return False, "Kitap bulunamadı."
        
        transaction = None
        for t in self.transactions:
            if t["username"] == username and t["isbn"] == isbn and t.get("status") == "Onaylandı":
                transaction = t
                break
        
        if not transaction:
            return False, "Bu kitap üzerinizde görünmüyor."
        
        book = self.books[isbn]
        book["stock"] += 1
        
        transaction["status"] = "İade Edildi"
        transaction["return_date"] = datetime.now().isoformat()
        
        self.save_books()
        self.save_transactions()
        return True, "Kitap başarıyla iade edildi."

    def get_user_overdue_books(self, username):
        overdue = []
        current_time = datetime.now()
        for t in self.transactions:
            if t["username"] == username and t.get("status") == "Onaylandı":
                due_date = datetime.fromisoformat(t["due_date"])
                if current_time > due_date:
                    overdue.append(t)
        return overdue

    def get_user_active_loans(self, username):
        active = []
        for t in self.transactions:
            # Öğrenci profilinde hem bekleyen taleplerini hem de onaylananları görebilmeli
            if t["username"] == username and t.get("status") in ["Bekliyor", "Onaylandı"]:
                active.append(t)
        return active

    def authenticate_user(self, username, password):
        if username in self.users:
            stored_hash = self.users[username]["password"]
            if stored_hash == self._hash_password(password):
                return self.users[username]["role"]
        return None

    def create_user(self, admin_username, username, password, role):
        creator_role = self.users.get(admin_username, {}).get("role")
        
        if creator_role == "Yönetici":
            pass 
        elif creator_role == "Personel" and role == "Öğrenci":
            pass 
        else:
            return False, "Yeterli yetki yok veya geçersiz rol."
        
        if username in self.users:
            return False, "Kullanıcı zaten mevcut."
        
        self.users[username] = {
            "password": self._hash_password(password),
            "role": role
        }
        self.save_users()
        return True, f"'{username}' başarıyla oluşturuldu."

    def get_all_books(self):
        books_list = []
        for isbn, info in self.books.items():
            books_list.append((isbn, info["title"], info["author"], info["stock"]))
        return books_list

    def search_books(self, query):
        results = []
        for isbn, info in self.books.items():
            if (query.lower() in info["title"].lower() or 
                query.lower() in info["author"].lower() or 
                query == isbn):
                results.append((isbn, info["title"], info["author"], info["stock"]))
        return results

    def get_user_transactions(self, username):
        user_transactions = []
        for t in self.transactions:
            if t["username"] == username:
                user_transactions.append(t)
        return user_transactions

    def get_overdue_books(self):
        overdue = []
        current_time = datetime.now()
        for t in self.transactions:
            if t.get("status") == "Onaylandı":
                due_date = datetime.fromisoformat(t["due_date"])
                if current_time > due_date:
                    overdue.append(t)
        return overdue