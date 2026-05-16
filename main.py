import pygame
import config
from ui_elements import Button, TextBox, RoleSelector
from backend import LibrarySystem  # Backend'i içe aktar

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption("Librarian")
    clock = pygame.time.Clock()
    
    font = pygame.font.SysFont("Arial", 20)
    sidebar_font = pygame.font.SysFont("Arial", 18, bold=True)
    title_font = pygame.font.SysFont("Arial", 32, bold=True)

    # --- GİRİŞ EKRANI ELEMANLARI ---
    role_selector = RoleSelector(340, 220, ["Öğrenci", "Personel", "Yönetici"], font)
    user_input = TextBox(340, 270, 350, 40, "Kullanıcı Adı", font=font)
    pass_input = TextBox(340, 330, 350, 40, "Şifre", is_password=True, font=font)
    login_btn = Button(340, 390, 350, 50, "Giriş Yap", font)

    # --- ANA EKRAN / SOL MENÜ ELEMANLARI ---
    # Ortak butonlar
    btn_library = Button(10, 100, 200, 40, "📚 Kitaplık", sidebar_font)
    btn_profile = Button(10, 150, 200, 40, "👤 Profilim", sidebar_font)
    # Personel ve Admin butonları
    btn_inventory = Button(10, 200, 200, 40, "➕ Envanter Yönetimi", sidebar_font)
    btn_penalties = Button(10, 250, 200, 40, "⚠️ Geciken İadeler", sidebar_font)
    # Sadece Admin butonu
    btn_users = Button(10, 300, 200, 40, "👥 Kullanıcı İşlemleri", sidebar_font)

    # Sağ taraf (İçerik) Elemanları - X koordinatları 250'ye kaydırıldı
    search_input = TextBox(250, 80, 400, 40, "Kitap Adı, Yazar veya ISBN...", font=font)
    search_btn = Button(660, 80, 100, 40, "Ara", font)
    logout_btn = Button(900, 20, 100, 40, "Çıkış", font)
    
    # --- BACKEND INITIALIZATION ---
    # Backend sistemini başlat
    db = LibrarySystem()
    
    # --- BOOK DATA INITIALIZATION ---
    # Dummy veri yerine backend'ten kitapları al
    dummy_books = db.get_all_books()
    
    # Durum Yönetimi
    current_state = config.STATE_LOGIN
    logged_in_role = "" # Hangi rolde giriş yapıldığını tutar
    running = True

    # Scroll Değişkenleri
    scroll_y = 0
    scroll_speed = 25
    item_height = 40 

    # Tablo Başlıkları (İşlem sütunu eklendi)
    headers = ["ISBN", "Kitap Adı", "Yazar", "Stok", "Durum", "İşlem"]
    
    # Her kitap için bir Ödünç Al butonu oluşturuyoruz
    borrow_buttons = []
    for i in range(len(dummy_books)):
        # X koordinatı 850, Y koordinatı geçici olarak 0 veriliyor (Scroll'da güncellenecek)
        btn = Button(850, 0, 100, 30, "Ödünç Al", font)
        borrow_buttons.append(btn)

    # === LOGO INTEGRATION ===
    logo = None
    try:
        logo = pygame.image.load("logo.png")
        logo = pygame.transform.scale(logo, (150, 150))
    except pygame.error:
        pass  # Logo bulunamazsa None kalır

    # === USER MANAGEMENT UI ELEMENTS ===
    new_user_input = TextBox(340, 270, 350, 40, "Yeni Kullanıcı Adı", font=font)
    new_pass_input = TextBox(340, 330, 350, 40, "Yeni Şifre", font=font)
    create_user_btn = Button(340, 390, 350, 50, "Kullanıcı Oluştur", font)
    back_btn = Button(250, 20, 100, 40, "Geri", font)
    new_role_selector = None
    ui_message = ""

    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            
            # === GİRİŞ EKRANI OLAYLARI ===
            if current_state == config.STATE_LOGIN:
                role_selector.handle_event(event)
                user_input.handle_event(event)
                pass_input.handle_event(event)
                
                if login_btn.handle_event(event):
                    # Backend ile kimlik doğrulama
                    username = user_input.text
                    password = pass_input.text
                    role = db.authenticate_user(username, password)
                    if role:
                        logged_in_role = role
                        print(f"{logged_in_role} yetkisiyle giriş yapıldı.")
                        current_state = config.STATE_USER
                        scroll_y = 0 # Sayfa değişiminde scroll'u sıfırla
                    else:
                        print("Giriş başarısız: Kullanıcı adı veya şifre hatalı.")
            
            # === ANA EKRAN OLAYLARI ===
            elif current_state == config.STATE_USER:
                search_input.handle_event(event)
                
                # Çıkış İşlemi
                if logout_btn.handle_event(event):
                    current_state = config.STATE_LOGIN
                    logged_in_role = ""
                    user_input.text = ""
                    pass_input.text = ""

                # Sol Menü Buton Dinlemeleri (Role Göre Koşullu)
                if btn_library.handle_event(event): print("Kitaplık Sekmesi")
                if btn_profile.handle_event(event): print("Profil Sekmesi")
                
                if logged_in_role in ["Personel", "Yönetici"]:
                    if btn_inventory.handle_event(event): print("Envanter Yönetimi Sekmesi")
                    if btn_penalties.handle_event(event): print("Cezalar Sekmesi")
                
                if logged_in_role == "Yönetici":
                    if btn_users.handle_event(event): 
                        current_state = config.STATE_USER_MANAGEMENT
                        # Rol seçiciyi başlat
                        if logged_in_role == "Yönetici":
                            new_role_selector = RoleSelector(340, 220, ["Öğrenci", "Personel", "Yönetici"], font)
                        else:
                            new_role_selector = RoleSelector(340, 220, ["Öğrenci"], font)
                        ui_message = ""
                
                # Scroll İşlemi (Sadece farenin x pozisyonu tablonun üzerindeyse çalışsın)
                mouse_x, _ = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEWHEEL and mouse_x > 220:
                    scroll_y += event.y * scroll_speed
                
                # Buton tıklamalarını dinle (Sadece tablo alanındaysa)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    clip_rect = pygame.Rect(250, 185, 750, 550)
                    if clip_rect.collidepoint(mouse_x, mouse_y):
                        for i, btn in enumerate(borrow_buttons):
                            # Butonun konumunu hesapla ve tıklama kontrolü yap
                            row_y = 185 + (i * item_height) - scroll_y
                            btn.rect.y = row_y
                            if btn.rect.collidepoint(mouse_x, mouse_y):
                                # Ödünç alma işlemi
                                success, message = db.borrow_book(logged_in_role, dummy_books[i][0])
                                print(message)
                                # Tabloyu yenile
                                dummy_books = db.get_all_books()
                                scroll_y = 0
                                break

                # === SEARCH EVENT ===
                if search_btn.handle_event(event):
                    search_query = search_input.text.strip()
                    if not search_query or search_query == "Kitap Adı, Yazar veya ISBN...":
                        dummy_books = db.get_all_books()
                    else:
                        dummy_books = db.search_books(search_query)
                    scroll_y = 0  # Tabloyu yenile

            # === USER MANAGEMENT OLAYLARI ===
            elif current_state == config.STATE_USER_MANAGEMENT:
                if new_role_selector:
                    new_role_selector.handle_event(event)
                new_user_input.handle_event(event)
                new_pass_input.handle_event(event)
                
                if back_btn.handle_event(event):
                    current_state = config.STATE_USER
                    new_role_selector = None
                    ui_message = ""
                
                if create_user_btn.handle_event(event):
                    # Kullanıcı oluştur
                    new_username = new_user_input.text
                    new_password = new_pass_input.text
                    new_role = "Öğrenci"  # Varsayılan rol
                    if new_role_selector:
                        selected_role = new_role_selector.get_selected_role()  # FIXED: get_selected_role kullanılıyor
                        if selected_role:
                            new_role = selected_role
                    success, message = db.create_user(logged_in_role, new_username, new_password, new_role)
                    ui_message = message
                    new_user_input.clear()
                    new_pass_input.clear()
                        if selected_role:
                            new_role = selected_role
                    
                    success, message = db.create_user(logged_in_role, new_username, new_password, new_role)
                    ui_message = message
                    new_user_input.clear()
                    new_pass_input.clear()

        # === ÇİZİM ===
        screen.fill((255, 255, 255))  # Arka planı beyaz yap

        if current_state == config.STATE_LOGIN:
            # Giriş ekranı çizimi
            screen.fill((255, 255, 255))  # Arka planı beyaz yap
            
            # Başlık çizimi
            title_text = title_font.render("Kütüphane Sistemi", True, (0, 0, 0))
            screen.blit(title_text, (350, 100))
            
            # Giriş formu çizimi
            role_selector.draw(screen)
            user_input.draw(screen)
            pass_input.draw(screen)
            login_btn.draw(screen)
            
        elif current_state == config.STATE_USER:
            # Sidebar çizimi
            pygame.draw.rect(screen, (50, 50, 50), (0, 0, 220, 600))  # Sidebar
            
            # İçerik alanı çizimi
            pygame.draw.rect(screen, (200, 200, 200), (220, 0, 780, 600))  # İçerik alanı
            
            # Menü butonları çizimi
            btn_library.draw(screen)
            btn_profile.draw(screen)
            btn_inventory.draw(screen)
            btn_penalties.draw(screen)
            btn_users.draw(screen)
            
            # Arama alanı çizimi
            search_input.draw(screen)
            search_btn.draw(screen)
            logout_btn.draw(screen)
            
            # Kitap listesi çizimi
            # (Bu kısmı kısalttık ama gerçek uygulamada daha fazla çizim olur)
            
        elif current_state == config.STATE_USER_MANAGEMENT:
            # Sidebar çizimi
            pygame.draw.rect(screen, (50, 50, 50), (0, 0, 220, 600))  # Sidebar
            
            # İçerik alanı çizimi
            pygame.draw.rect(screen, (200, 200, 200), (220, 0, 780, 600))  # İçerik alanı
            
            # Geri butonu
            back_btn.draw(screen)
            
            # Kullanıcı oluşturma formu
            if new_role_selector:
                new_role_selector.draw(screen)
            new_user_input.draw(screen)
            new_pass_input.draw(screen)
            create_user_btn.draw(screen)
            
            # Mesajı çiz
            if ui_message:
                message_text = font.render(ui_message, True, (0, 0, 0))
                screen.blit(message_text, (340, 450))
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()