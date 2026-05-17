import pygame
import config
from ui_elements import Button, TextBox, RoleSelector
from backend import LibrarySystem

def sync_borrow_buttons(books, font):
    return [Button(850, 0, 110, 30, "Talep Gönder", font) for _ in range(len(books))]

def sync_return_buttons(loans, font):
    return [Button(800, 0, 100, 30, "İade Et", font) for _ in range(len(loans))]

def sync_request_buttons(requests, font):
    app_btns = [Button(750, 0, 80, 30, "Onayla", font) for _ in range(len(requests))]
    rej_btns = [Button(840, 0, 80, 30, "Reddet", font) for _ in range(len(requests))]
    return app_btns, rej_btns

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption("Librarian - Kütüphane Sistemi")
    clock = pygame.time.Clock()
    
    font = pygame.font.SysFont("Arial", 20)
    sidebar_font = pygame.font.SysFont("Arial", 18, bold=True)
    title_font = pygame.font.SysFont("Arial", 32, bold=True)

    # --- UI ELEMANLARI ---
    role_selector = RoleSelector(340, 220, ["Öğrenci", "Personel", "Yönetici"], font)
    user_input = TextBox(340, 270, 350, 40, "Kullanıcı Adı", font=font)
    pass_input = TextBox(340, 330, 350, 40, "Şifre", is_password=True, font=font)
    login_btn = Button(340, 390, 350, 50, "Giriş Yap", font)

    btn_library = Button(10, 100, 200, 40, "📚 Kitaplık", sidebar_font)
    btn_profile = Button(10, 150, 200, 40, "👤 Profilim", sidebar_font)
    btn_inventory = Button(10, 200, 200, 40, "➕ Envanter Yönetimi", sidebar_font)
    btn_requests = Button(10, 250, 200, 40, "📋 Bekleyen Talepler", sidebar_font) # YENİ BUTON
    btn_penalties = Button(10, 300, 200, 40, "⚠️ Geciken İadeler", sidebar_font)
    btn_users = Button(10, 350, 200, 40, "👥 Kullanıcı İşlemleri", sidebar_font)

    search_input = TextBox(250, 80, 400, 40, "Kitap Adı, Yazar veya ISBN...", font=font)
    search_btn = Button(660, 80, 100, 40, "Ara", font)
    logout_btn = Button(900, 20, 100, 40, "Çıkış", font)
    back_btn = Button(900, 20, 100, 40, "Geri", font)
    
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

    active_loans = []
    overdue_loans = []
    return_buttons = []
    
    pending_requests = []
    approve_buttons = []
    reject_buttons = []

    new_user_input = TextBox(340, 270, 350, 40, "Yeni Kullanıcı Adı", font=font)
    new_pass_input = TextBox(340, 330, 350, 40, "Yeni Şifre", font=font)
    create_user_btn = Button(340, 390, 350, 50, "Kullanıcı Oluştur", font)
    new_role_selector = None

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
                role_selector.handle_event(event)
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
                        print("Hatalı Giriş")

            # ================= ORTAK MENÜ OLAYLARI =================
            elif current_state in [config.STATE_USER, config.STATE_PROFILE, config.STATE_INVENTORY, config.STATE_USER_MANAGEMENT, config.STATE_REQUESTS]:
                if logout_btn.handle_event(event) if current_state == config.STATE_USER else False:
                    current_state = config.STATE_LOGIN
                    logged_in_role = ""
                    logged_in_username = ""
                    user_input.text = ""
                    pass_input.text = ""
                    ui_message = ""

                # Ortak Sol Menü Yönlendirmeleri
                if back_btn.handle_event(event) or btn_library.handle_event(event):
                    current_state = config.STATE_USER
                    ui_message = ""
                    books_data = db.get_all_books()
                    borrow_buttons = sync_borrow_buttons(books_data, font)
                    scroll_y = 0

                if btn_profile.handle_event(event):
                    current_state = config.STATE_PROFILE
                    ui_message = ""
                    active_loans = db.get_user_active_loans(logged_in_username)
                    overdue_loans = db.get_user_overdue_books(logged_in_username)
                    return_buttons = sync_return_buttons(active_loans, font)
                    scroll_y = 0

                if logged_in_role in ["Personel", "Yönetici"]:
                    if btn_inventory.handle_event(event):
                        current_state = config.STATE_INVENTORY
                        ui_message = ""
                        scroll_y = 0
                    
                    if btn_requests.handle_event(event):
                        current_state = config.STATE_REQUESTS
                        ui_message = ""
                        pending_requests = db.get_pending_requests()
                        approve_buttons, reject_buttons = sync_request_buttons(pending_requests, font)
                        scroll_y = 0

                    if btn_users.handle_event(event): 
                        current_state = config.STATE_USER_MANAGEMENT
                        new_role_selector = RoleSelector(340, 220, ["Öğrenci", "Personel", "Yönetici"], font) if logged_in_role == "Yönetici" else RoleSelector(340, 220, ["Öğrenci"], font)
                        ui_message = ""
                        scroll_y = 0

                # ================= ANA EKRAN (KİTAPLIK) =================
                if current_state == config.STATE_USER:
                    search_input.handle_event(event)
                    
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
                        books_data = db.get_all_books() if not search_query or search_query == "Kitap Adı, Yazar veya ISBN..." else db.search_books(search_query)
                        borrow_buttons = sync_borrow_buttons(books_data, font)
                        scroll_y = 0

                # ================= PROFİL EKRANI =================
                elif current_state == config.STATE_PROFILE:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if event.type == pygame.MOUSEWHEEL and mouse_x > 220: scroll_y += event.y * scroll_speed

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

                # ================= TALEP YÖNETİMİ (YENİ EKRAN) =================
                elif current_state == config.STATE_REQUESTS:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if event.type == pygame.MOUSEWHEEL and mouse_x > 220: scroll_y += event.y * scroll_speed

                    clip_rect = pygame.Rect(250, 185, 750, 550)
                    if event.type == pygame.MOUSEBUTTONDOWN and clip_rect.collidepoint(mouse_x, mouse_y):
                        for i in range(len(pending_requests)):
                            approve_buttons[i].rect.y = 200 + (i * item_height) + scroll_y
                            reject_buttons[i].rect.y = 200 + (i * item_height) + scroll_y
                            
                            # Onayla Butonu
                            if approve_buttons[i].handle_event(event):
                                success, msg = db.approve_request(pending_requests[i]["id"])
                                ui_message = msg
                                pending_requests = db.get_pending_requests()
                                approve_buttons, reject_buttons = sync_request_buttons(pending_requests, font)
                                break
                            
                            # Reddet Butonu
                            if reject_buttons[i].handle_event(event):
                                success, msg = db.reject_request(pending_requests[i]["id"])
                                ui_message = msg
                                pending_requests = db.get_pending_requests()
                                approve_buttons, reject_buttons = sync_request_buttons(pending_requests, font)
                                break

                # ================= ENVANTER YÖNETİMİ =================
                elif current_state == config.STATE_INVENTORY:
                    book_isbn_input.handle_event(event)
                    book_title_input.handle_event(event)
                    book_author_input.handle_event(event)
                    book_stock_input.handle_event(event)
                        
                    if add_book_btn.handle_event(event):
                        isbn, title, author, stock_str = book_isbn_input.text.strip(), book_title_input.text.strip(), book_author_input.text.strip(), book_stock_input.text.strip()
                        
                        if not isbn or not title or not author or not stock_str: ui_message = "Lütfen tüm alanları doldurun!"
                        elif not stock_str.isdigit(): ui_message = "Stok adedi rakam olmalıdır!"
                        else:
                            db.add_book(isbn, title, author, int(stock_str))
                            ui_message = f"'{title}' eklendi!"
                            book_isbn_input.text = book_title_input.text = book_author_input.text = book_stock_input.text = ""

                # ================= KULLANICI YÖNETİMİ =================
                elif current_state == config.STATE_USER_MANAGEMENT:
                    if new_role_selector: new_role_selector.handle_event(event)
                    new_user_input.handle_event(event)
                    new_pass_input.handle_event(event)
                    
                    if create_user_btn.handle_event(event):
                        new_username, new_password = new_user_input.text, new_pass_input.text
                        new_role = new_role_selector.get_selected_role() if new_role_selector else "Öğrenci"
                        
                        if not new_username or not new_password: ui_message = "Kullanıcı adı ve şifre boş bırakılamaz!"
                        else:
                            success, message = db.create_user(logged_in_username, new_username, new_password, new_role)
                            ui_message = message
                            new_user_input.text = new_pass_input.text = ""

        # === ÇİZİM (RENDERING) KISMI ===
        screen.fill(config.WHITE)

        if current_state == config.STATE_LOGIN:
            screen.blit(title_font.render("Librarian Sistemine Giriş", True, config.BLACK), (340, 100))
            role_selector.draw(screen)
            user_input.draw(screen)
            pass_input.draw(screen)
            login_btn.draw(screen)
            
        elif current_state in [config.STATE_USER, config.STATE_PROFILE, config.STATE_INVENTORY, config.STATE_USER_MANAGEMENT, config.STATE_REQUESTS]:
            # ORTAK SOL MENÜ ÇİZİMİ
            pygame.draw.rect(screen, config.DARK_GRAY, (0, 0, 220, config.HEIGHT))
            screen.blit(font.render(f"Rol: {logged_in_role}", True, config.WHITE), (20, 30))
            pygame.draw.line(screen, config.WHITE, (10, 60), (210, 60), 1)

            btn_library.draw(screen)
            btn_profile.draw(screen)
            if logged_in_role in ["Personel", "Yönetici"]:
                btn_inventory.draw(screen)
                btn_requests.draw(screen) # YENİ BUTON ÇİZİMİ
                btn_penalties.draw(screen)
            if logged_in_role == "Yönetici":
                btn_users.draw(screen)

            # EKRANA ÖZEL ÇİZİMLER
            if current_state == config.STATE_USER:
                screen.blit(title_font.render("Kütüphane Envanteri", True, config.BLUE), (250, 30))
                logout_btn.draw(screen)
                search_input.draw(screen)
                search_btn.draw(screen)
                
                if ui_message: screen.blit(font.render(ui_message, True, (0, 150, 0) if "başarı" in ui_message.lower() or "gönderildi" in ui_message.lower() else (200, 0, 0)), (250, 130))

                for i, h in enumerate(["ISBN", "Kitap Adı", "Yazar", "Stok", "Durum", "İşlem"]): screen.blit(font.render(h, True, config.BLACK), (250 + i*120, 160))
                pygame.draw.line(screen, config.BLACK, (250, 185), (1000, 185), 2)
                
                clip_rect = pygame.Rect(250, 190, 750, 550)
                screen.set_clip(clip_rect)
                
                if scroll_y > 0: scroll_y = 0
                max_scroll = max(0, (len(books_data) * item_height) - 500)
                if scroll_y < -max_scroll: scroll_y = -max_scroll

                for index, book in enumerate(books_data):
                    row_y = 200 + (index * item_height) + scroll_y
                    stok = int(book[3])
                    
                    for i, val in enumerate(book):
                        if i == 1 and len(val) > 13: val = val[:10] + "..."
                        screen.blit(font.render(str(val), True, config.BLACK if stok == 0 else config.DARK_GRAY), (250 + i*120, row_y + 5))
                    
                    screen.blit(font.render("Müsait" if stok > 0 else "Tükendi", True, (0, 150, 0) if stok > 0 else (200, 0, 0)), (250 + 4*120, row_y + 5))
                    
                    if stok > 0 and logged_in_role == "Öğrenci":
                        borrow_buttons[index].rect.y = row_y
                        borrow_buttons[index].draw(screen)
                    elif stok <= 0: screen.blit(sidebar_font.render("Stokta Yok", True, (200, 0, 0)), (850, row_y + 5))
                screen.set_clip(None)

            elif current_state == config.STATE_PROFILE:
                screen.blit(title_font.render(f"Profilim - {logged_in_username}", True, config.BLUE), (250, 30))
                back_btn.draw(screen)
                if ui_message: screen.blit(font.render(ui_message, True, (0, 150, 0) if "başarı" in ui_message.lower() else (200, 0, 0)), (370, 30))

                for i, h in enumerate(["ISBN", "Kitap Adı", "Ödünç Tarihi", "İade Tarihi", "İşlem"]): screen.blit(font.render(h, True, config.BLACK), (250 + i*140, 150))
                pygame.draw.line(screen, config.BLACK, (250, 180), (1000, 180), 2)

                clip_rect = pygame.Rect(250, 185, 750, 550)
                screen.set_clip(clip_rect)

                if scroll_y > 0: scroll_y = 0
                max_scroll = max(0, (len(active_loans) * item_height) - 500)
                if scroll_y < -max_scroll: scroll_y = -max_scroll

                for index, loan in enumerate(active_loans):
                    row_y = 200 + (index * item_height) + scroll_y
                    isbn = loan["isbn"]
                    status = loan.get("status", "Onaylandı")
                    
                    book_info = db.get_book_by_isbn(isbn)
                    title = book_info["title"] if book_info else "Bilinmeyen"
                    if len(title) > 13: title = title[:10] + "..."
                    
                    if status == "Bekliyor":
                        b_date, d_date, text_color = "Onay Bekliyor", "-", (100, 100, 250)
                    else:
                        b_date, d_date = loan["borrow_date"][:10], loan["due_date"][:10]
                        text_color = (200, 0, 0) if any(t for t in overdue_loans if t["isbn"] == isbn and t.get("status") == "Onaylandı") else config.DARK_GRAY

                    screen.blit(font.render(isbn, True, text_color), (250, row_y + 5))
                    screen.blit(font.render(title, True, text_color), (390, row_y + 5))
                    screen.blit(font.render(b_date, True, text_color), (530, row_y + 5))
                    screen.blit(font.render(d_date, True, text_color), (670, row_y + 5))

                    if status == "Onaylandı":
                        return_buttons[index].rect.y = row_y
                        return_buttons[index].draw(screen)
                    else: screen.blit(sidebar_font.render("İşlemde", True, (150, 150, 150)), (800, row_y + 5))
                screen.set_clip(None)

            # === YENİ EKRAN: TALEP YÖNETİMİ ÇİZİMİ ===
            elif current_state == config.STATE_REQUESTS:
                screen.blit(title_font.render("Bekleyen Ödünç Talepleri", True, config.BLUE), (250, 30))
                back_btn.draw(screen)
                
                if ui_message: screen.blit(font.render(ui_message, True, (0, 150, 0) if "onaylandı" in ui_message.lower() else (200, 0, 0)), (370, 30))

                for i, h in enumerate(["Kullanıcı", "ISBN", "Kitap Adı", "Talep Tarihi", "İşlem"]): screen.blit(font.render(h, True, config.BLACK), (250 + i*130, 150))
                pygame.draw.line(screen, config.BLACK, (250, 180), (1000, 180), 2)

                clip_rect = pygame.Rect(250, 185, 750, 550)
                screen.set_clip(clip_rect)

                if scroll_y > 0: scroll_y = 0
                max_scroll = max(0, (len(pending_requests) * item_height) - 500)
                if scroll_y < -max_scroll: scroll_y = -max_scroll

                for index, req in enumerate(pending_requests):
                    row_y = 200 + (index * item_height) + scroll_y
                    
                    book_info = db.get_book_by_isbn(req["isbn"])
                    title = book_info["title"] if book_info else "Bilinmeyen"
                    if len(title) > 13: title = title[:10] + "..."

                    screen.blit(font.render(req["username"], True, config.DARK_GRAY), (250, row_y + 5))
                    screen.blit(font.render(req["isbn"], True, config.DARK_GRAY), (380, row_y + 5))
                    screen.blit(font.render(title, True, config.DARK_GRAY), (510, row_y + 5))
                    screen.blit(font.render(req["request_date"][:10], True, config.DARK_GRAY), (640, row_y + 5))

                    approve_buttons[index].rect.y = row_y
                    approve_buttons[index].color = (0, 150, 0) # Yeşil Onay
                    approve_buttons[index].draw(screen)
                    
                    reject_buttons[index].rect.y = row_y
                    reject_buttons[index].color = (200, 0, 0) # Kırmızı Red
                    reject_buttons[index].draw(screen)
                screen.set_clip(None)

            elif current_state == config.STATE_INVENTORY:
                screen.blit(title_font.render("Yeni Kitap Ekle", True, config.BLUE), (250, 30))
                back_btn.draw(screen)
                book_isbn_input.draw(screen); book_title_input.draw(screen); book_author_input.draw(screen); book_stock_input.draw(screen); add_book_btn.draw(screen)
                if ui_message: screen.blit(font.render(ui_message, True, (0, 150, 0) if "eklendi" in ui_message.lower() else (200, 0, 0)), (340, 460))

            elif current_state == config.STATE_USER_MANAGEMENT:
                screen.blit(title_font.render("Kullanıcı Yönetimi", True, config.BLUE), (250, 30))
                back_btn.draw(screen)
                if new_role_selector: new_role_selector.draw(screen)
                new_user_input.draw(screen); new_pass_input.draw(screen); create_user_btn.draw(screen)
                if ui_message: screen.blit(font.render(ui_message, True, (0, 150, 0) if "başarı" in ui_message.lower() else (200, 0, 0)), (340, 460))
        
        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()

if __name__ == "__main__":
    main()