import pygame
import config
from ui_elements import Button, TextBox, RoleSelector
from backend import LibrarySystem

def sync_borrow_buttons(books, font):
    return [Button(850, 0, 100, 30, "Ödünç Al", font) for _ in range(len(books))]

def sync_return_buttons(loans, font):
    return [Button(800, 0, 100, 30, "İade Et", font) for _ in range(len(loans))]

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption("Librarian - Kütüphane Sistemi")
    clock = pygame.time.Clock()
    
    font = pygame.font.SysFont("Arial", 20)
    sidebar_font = pygame.font.SysFont("Arial", 18, bold=True)
    title_font = pygame.font.SysFont("Arial", 32, bold=True)

    # --- LOGO YÜKLEME ---
    logo_img = None
    try:
        raw_logo = pygame.image.load("logo.png")
        logo_img = pygame.transform.scale(raw_logo, (120, 120))
    except Exception as e:
        print(f"Logo yüklenemedi: {e}")

    # --- UI ELEMANLARI ---
    # Giriş ekranı için RoleSelector KALDIRILDI! Artık rol otomatik bulunuyor.
    user_input = TextBox(337, 340, 350, 45, "Kullanıcı Adı", font=font)
    pass_input = TextBox(337, 400, 350, 45, "Şifre", is_password=True, font=font)
    login_btn = Button(337, 470, 350, 50, "Giriş Yap", font)

    # Sol menü butonları
    btn_library = Button(10, 230, 200, 40, "Kitaplık", sidebar_font)
    btn_profile = Button(10, 280, 200, 40, "Profilim", sidebar_font)
    btn_inventory = Button(10, 330, 200, 40, "Envanter Yönetimi", sidebar_font)
    btn_penalties = Button(10, 380, 200, 40, "Geciken İadeler", sidebar_font)
    btn_users = Button(10, 430, 200, 40, "Kullanıcı İşlemleri", sidebar_font)

    # Sağ üst bileşenler (Geri butonu sağ üste sabitlendi)
    search_input = TextBox(250, 80, 400, 40, "Kitap Adı, Yazar veya ISBN...", font=font)
    search_btn = Button(660, 80, 100, 40, "Ara", font)
    logout_btn = Button(880, 20, 100, 40, "Çıkış", font)
    back_btn = Button(880, 20, 100, 40, "Geri", font) # KOORDİNATLAR GÜNCELLENDİ
    
    # --- BACKEND BAŞLATMA ---
    db = LibrarySystem()
    books_data = db.get_all_books()
    borrow_buttons = sync_borrow_buttons(books_data, font)
    
    # --- DURUM VE VERİ DEĞİŞKENLERİ ---
    current_state = config.STATE_LOGIN
    logged_in_role = ""
    logged_in_username = ""
    ui_message = ""
    running = True

    scroll_y = 0
    scroll_speed = 25
    item_height = 40 

    # Profil Ekranı
    active_loans = []
    overdue_loans = []
    return_buttons = []

    # Kullanıcı Yönetimi
    new_user_input = TextBox(340, 270, 350, 40, "Yeni Kullanıcı Adı", font=font)
    new_pass_input = TextBox(340, 330, 350, 40, "Yeni Şifre", font=font)
    create_user_btn = Button(340, 390, 350, 50, "Kullanıcı Oluştur", font)
    new_role_selector = None

    # --- ENVANTER YÖNETİMİ ELEMANLARI ---
    book_isbn_input = TextBox(340, 150, 350, 40, "ISBN (Örn: 978-01)", font=font)
    book_title_input = TextBox(340, 210, 350, 40, "Kitap Adı", font=font)
    book_author_input = TextBox(340, 270, 350, 40, "Yazar", font=font)
    book_stock_input = TextBox(340, 330, 350, 40, "Stok Adedi (Sayı)", font=font)
    add_book_btn = Button(340, 390, 350, 50, "Sisteme Ekle", font)

    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            
            # ================= GİRİŞ EKRANI =================
            if current_state == config.STATE_LOGIN:
                user_input.handle_event(event)
                pass_input.handle_event(event)
                
                if login_btn.handle_event(event):
                    username = user_input.text
                    password = pass_input.text
                    role = db.authenticate_user(username, password)
                    
                    if role:
                        logged_in_role = role
                        logged_in_username = username
                        current_state = config.STATE_USER
                        scroll_y = 0
                        ui_message = ""
                    else:
                        ui_message = "Hatalı kullanıcı adı veya şifre!"

            # ================= ANA EKRAN (KİTAPLIK) =================
            elif current_state == config.STATE_USER:
                search_input.handle_event(event)
                
                if logout_btn.handle_event(event):
                    current_state = config.STATE_LOGIN
                    logged_in_role = ""
                    logged_in_username = ""
                    user_input.text = ""
                    pass_input.text = ""
                    ui_message = ""

                if btn_profile.handle_event(event):
                    current_state = config.STATE_PROFILE
                    scroll_y = 0
                    ui_message = ""
                    active_loans = db.get_user_active_loans(logged_in_username)
                    overdue_loans = db.get_user_overdue_books(logged_in_username)
                    return_buttons = sync_return_buttons(active_loans, font)

                # Envanter Yönetimi Menüsü
                if logged_in_role in ["Personel", "Yönetici"] and btn_inventory.handle_event(event):
                    current_state = config.STATE_INVENTORY
                    ui_message = ""

                # Personel için de kullanıcı yönetimi menüsü açılacak, ancak sadece "Öğrenci" rolü oluşturabilecek
                if logged_in_role in ["Yönetici", "Personel"] and btn_users.handle_event(event): 
                    current_state = config.STATE_USER_MANAGEMENT
                    if logged_in_role == "Yönetici":
                        new_role_selector = RoleSelector(340, 220, ["Öğrenci", "Personel", "Yönetici"], font)
                    else:
                        # Personel sadece "Öğrenci" rolü oluşturabilir
                        new_role_selector = RoleSelector(340, 220, ["Öğrenci"], font)
                    ui_message = ""
                
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEWHEEL and mouse_x > 220:
                    scroll_y += event.y * scroll_speed
                
                clip_rect = pygame.Rect(250, 185, 750, 550)
                if event.type == pygame.MOUSEBUTTONDOWN and clip_rect.collidepoint(mouse_x, mouse_y):
                    for i, btn in enumerate(borrow_buttons):
                        stok_sayisi = int(books_data[i][3])
                        if stok_sayisi > 0 and logged_in_role == "Öğrenci":
                            btn.rect.y = 200 + (i * item_height) + scroll_y
                            if btn.handle_event(event):
                                success, msg = db.borrow_book(logged_in_username, books_data[i][0])
                                ui_message = msg
                                books_data = db.get_all_books()
                                borrow_buttons = sync_borrow_buttons(books_data, font)
                                break

                if search_btn.handle_event(event):
                    search_query = search_input.text.strip()
                    if not search_query or search_query == "Kitap Adı, Yazar veya ISBN...":
                        books_data = db.get_all_books()
                    else:
                        books_data = db.search_books(search_query)
                    borrow_buttons = sync_borrow_buttons(books_data, font)
                    scroll_y = 0

            # ================= PROFİL EKRANI =================
            elif current_state == config.STATE_PROFILE:
                if back_btn.handle_event(event) or btn_library.handle_event(event):
                    current_state = config.STATE_USER
                    ui_message = ""
                    books_data = db.get_all_books()
                    borrow_buttons = sync_borrow_buttons(books_data, font)

                mouse_x, mouse_y = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEWHEEL and mouse_x > 220:
                    scroll_y += event.y * scroll_speed

                clip_rect = pygame.Rect(250, 185, 750, 550)
                if event.type == pygame.MOUSEBUTTONDOWN and clip_rect.collidepoint(mouse_x, mouse_y):
                    for i, btn in enumerate(return_buttons):
                        btn.rect.y = 200 + (i * item_height) + scroll_y
                        if btn.handle_event(event):
                            isbn = active_loans[i]["isbn"]
                            success, msg = db.return_book(logged_in_username, isbn)
                            ui_message = msg
                            active_loans = db.get_user_active_loans(logged_in_username)
                            overdue_loans = db.get_user_overdue_books(logged_in_username)
                            return_buttons = sync_return_buttons(active_loans, font)
                            break

            # ================= ENVANTER YÖNETİMİ =================
            elif current_state == config.STATE_INVENTORY:
                book_isbn_input.handle_event(event)
                book_title_input.handle_event(event)
                book_author_input.handle_event(event)
                book_stock_input.handle_event(event)
                
                if back_btn.handle_event(event) or btn_library.handle_event(event):
                    current_state = config.STATE_USER
                    ui_message = ""
                    books_data = db.get_all_books()
                    borrow_buttons = sync_borrow_buttons(books_data, font)
                    
                if add_book_btn.handle_event(event):
                    isbn = book_isbn_input.text.strip()
                    title = book_title_input.text.strip()
                    author = book_author_input.text.strip()
                    stock_str = book_stock_input.text.strip()
                    
                    if not isbn or not title or not author or not stock_str:
                        ui_message = "Lütfen tüm alanları doldurun!"
                    elif not stock_str.isdigit():
                        ui_message = "Stok adedi sadece rakamlardan oluşmalıdır!"
                    else:
                        stock = int(stock_str)
                        db.add_book(isbn, title, author, stock)
                        ui_message = f"'{title}' sisteme eklendi!"
                        book_isbn_input.text = ""
                        book_title_input.text = ""
                        book_author_input.text = ""
                        book_stock_input.text = ""

            # ================= KULLANICI YÖNETİMİ =================
            elif current_state == config.STATE_USER_MANAGEMENT:
                if new_role_selector: new_role_selector.handle_event(event)
                new_user_input.handle_event(event)
                new_pass_input.handle_event(event)
                
                if back_btn.handle_event(event) or btn_library.handle_event(event):
                    current_state = config.STATE_USER
                    ui_message = ""
                
                if create_user_btn.handle_event(event):
                    new_username = new_user_input.text
                    new_password = new_pass_input.text
                    new_role = new_role_selector.get_selected_role() if new_role_selector else "Öğrenci"
                    
                    if not new_username or not new_password:
                        ui_message = "Kullanıcı adı ve şifre boş bırakılamaz!"
                    else:
                        success, message = db.create_user(logged_in_username, new_username, new_password, new_role)
                        ui_message = message
                        new_user_input.text = ""
                        new_pass_input.text = ""

        # === ÇİZİM (RENDERING) KISMI ===
        screen.fill(config.WHITE)

        if current_state == config.STATE_LOGIN:
            # Modern Koyu Arka Plan
            screen.fill((30, 45, 65))
            
            # Kart Gölgesi
            pygame.draw.rect(screen, (20, 30, 45), (305, 139, 424, 450), border_radius=15)
            # Kart (Card) Tasarımı
            pygame.draw.rect(screen, config.WHITE, (300, 134, 424, 450), border_radius=15)
            
            # Logo Ortalama
            if logo_img:
                logo_rect = logo_img.get_rect(center=(512, 210))
                screen.blit(logo_img, logo_rect)
                
            # Modernleştirilmiş Başlık
            title_surf = title_font.render("Librarian Sistemine Giriş", True, config.BLACK)
            title_rect = title_surf.get_rect(center=(512, 290))
            screen.blit(title_surf, title_rect)
            
            user_input.draw(screen)
            pass_input.draw(screen)
            login_btn.draw(screen)
            
            # Hata veya Bilgi Mesajı
            if ui_message:
                err_surf = font.render(ui_message, True, (200, 0, 0))
                err_rect = err_surf.get_rect(center=(512, 550))
                screen.blit(err_surf, err_rect)
            
        elif current_state in [config.STATE_USER, config.STATE_PROFILE, config.STATE_INVENTORY, config.STATE_USER_MANAGEMENT]:
            # ORTAK SOL MENÜ
            pygame.draw.rect(screen, config.DARK_GRAY, (0, 0, 220, config.HEIGHT))
            
            # Logo Çizimi
            if logo_img:
                screen.blit(logo_img, (50, 20))
            
            # Kullanıcı ve Rol Çizimi
            user_surf = font.render(f"Kullanıcı: {logged_in_username}", True, config.WHITE)
            role_surf = font.render(f"Rol: {logged_in_role}", True, config.WHITE)
            screen.blit(user_surf, (15, 150))
            screen.blit(role_surf, (15, 180))
            
            # Ayırıcı Çizgi
            pygame.draw.line(screen, config.WHITE, (10, 215), (210, 215), 1)

            btn_library.draw(screen)
            btn_profile.draw(screen)
            if logged_in_role in ["Personel", "Yönetici"]:
                btn_inventory.draw(screen)
                btn_penalties.draw(screen)
            if logged_in_role in ["Personel", "Yönetici"]:
                btn_users.draw(screen)

            # Sağ Taraf Arka Planı
            pygame.draw.rect(screen, config.LIGHT_BLUE, (220, 0, config.WIDTH - 220, config.HEIGHT))

            # EKRANA ÖZEL ÇİZİMLER
            if current_state == config.STATE_USER:
                screen.blit(title_font.render("Kütüphane Envanteri", True, config.BLUE), (250, 30))
                logout_btn.draw(screen)
                search_input.draw(screen)
                search_btn.draw(screen)
                
                if ui_message:
                    msg_color = (0, 150, 0) if "başarı" in ui_message.lower() else (200, 0, 0)
                    screen.blit(font.render(ui_message, True, msg_color), (250, 130))

                headers = ["ISBN", "Kitap Adı", "Yazar", "Stok", "Durum", "İşlem"]
                for i, h in enumerate(headers):
                    screen.blit(font.render(h, True, config.BLACK), (250 + i*120, 160))
                pygame.draw.line(screen, config.BLACK, (250, 185), (1000, 185), 2)
                
                clip_rect = pygame.Rect(250, 190, 750, 550)
                screen.set_clip(clip_rect)
                
                if scroll_y > 0: scroll_y = 0
                max_scroll = max(0, (len(books_data) * item_height) - 500)
                if scroll_y < -max_scroll: scroll_y = -max_scroll

                for index, book in enumerate(books_data):
                    row_y = 200 + (index * item_height) + scroll_y
                    stok = int(book[3])
                    
                    # 1. Mevcut 4 veriyi (ISBN, Ad, Yazar, Stok) çiz
                    for i, val in enumerate(book):
                        if i == 1 and len(val) > 13: val = val[:10] + "..."
                        color = config.BLACK if stok == 0 else config.DARK_GRAY
                        screen.blit(font.render(str(val), True, color), (250 + i*120, row_y + 5))
                    
                    # 2. Durum bilgisini stok sayısına göre hesapla ve çiz
                    durum_metni = "Müsait" if stok > 0 else "Tükendi"
                    durum_renk = (0, 150, 0) if stok > 0 else (200, 0, 0)
                    screen.blit(font.render(durum_metni, True, durum_renk), (250 + 4*120, row_y + 5))
                    
                    # 3. İşlem sütunundaki Butonları çiz
                    if stok > 0 and logged_in_role == "Öğrenci":
                        borrow_buttons[index].rect.y = row_y
                        borrow_buttons[index].draw(screen)
                    elif stok <= 0:
                        screen.blit(sidebar_font.render("Stokta Yok", True, (200, 0, 0)), (850, row_y + 5))
                screen.set_clip(None)

            elif current_state == config.STATE_PROFILE:
                screen.blit(title_font.render(f"Profilim - {logged_in_username}", True, config.BLUE), (250, 30))
                back_btn.draw(screen)
                
                if ui_message:
                    msg_color = (0, 150, 0) if "başarı" in ui_message.lower() else (200, 0, 0)
                    screen.blit(font.render(ui_message, True, msg_color), (370, 30))

                prof_headers = ["ISBN", "Kitap Adı", "Ödünç Tarihi", "İade Tarihi", "İşlem"]
                for i, h in enumerate(prof_headers):
                    screen.blit(font.render(h, True, config.BLACK), (250 + i*140, 150))
                pygame.draw.line(screen, config.BLACK, (250, 180), (1000, 180), 2)

                clip_rect = pygame.Rect(250, 185, 750, 550)
                screen.set_clip(clip_rect)

                if scroll_y > 0: scroll_y = 0
                max_scroll = max(0, (len(active_loans) * item_height) - 500)
                if scroll_y < -max_scroll: scroll_y = -max_scroll

                for index, loan in enumerate(active_loans):
                    row_y = 200 + (index * item_height) + scroll_y
                    isbn = loan["isbn"]
                    status = loan.get("status", "Onaylandi") # Varsayılan durum "Onaylandi" olarak alındı
                    
                    book_info = db.get_book_by_isbn(isbn)
                    title = book_info["title"] if book_info else "Bilinmeyen Kitap"
                    if len(title) > 13: title = title[:10] + "..."
                    
                    if status == "Bekliyor":
                        borrow_date = "Onay Bekliyor"
                        due_date = "-"
                        text_color = (100, 100, 250) # Bekleyen talepler için mavi ton
                    else:
                        borrow_date = loan["borrow_date"][:10]
                        due_date = loan["due_date"][:10]

                        # Gecikmiş mi kontrol et
                        is_overdue = any(t for t in overdue_loans if t["isbn"] == isbn and t.get("status") == "Onaylandı")
                        text_color = (200, 0, 0) if is_overdue else config.DARK_GRAY

                    # Ekrana çizimler
                    screen.blit(font.render(isbn, True, text_color), (250, row_y + 5))
                    screen.blit(font.render(title, True, text_color), (390, row_y + 5))
                    screen.blit(font.render(borrow_date, True, text_color), (530, row_y + 5))
                    screen.blit(font.render(due_date, True, text_color), (670, row_y + 5))


                    if status == "Onaylandı":
                        return_buttons[index].rect.y = row_y
                        return_buttons[index].draw(screen)
                    else:
                        screen.blit(sidebar_font.render("İşlemde", True, (150, 150, 150)), (800, row_y + 5))
                

            elif current_state == config.STATE_INVENTORY:
                screen.blit(title_font.render("Yeni Kitap Ekle", True, config.BLUE), (250, 30))
                back_btn.draw(screen)
                
                book_isbn_input.draw(screen)
                book_title_input.draw(screen)
                book_author_input.draw(screen)
                book_stock_input.draw(screen)
                add_book_btn.draw(screen)
                
                if ui_message:
                    msg_color = (0, 150, 0) if "eklendi" in ui_message.lower() else (200, 0, 0)
                    screen.blit(font.render(ui_message, True, msg_color), (340, 460))

            elif current_state == config.STATE_USER_MANAGEMENT:
                screen.blit(title_font.render("Kullanıcı Yönetimi", True, config.BLUE), (250, 30))
                back_btn.draw(screen)
                if new_role_selector: new_role_selector.draw(screen)
                new_user_input.draw(screen)
                new_pass_input.draw(screen)
                create_user_btn.draw(screen)
                
                if ui_message:
                    msg_color = (0, 150, 0) if "başarı" in ui_message.lower() else (200, 0, 0)
                    screen.blit(font.render(ui_message, True, msg_color), (340, 460))
        
        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()

if __name__ == "__main__":
    main()