# main.py

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
    btn_users = Button(10, 300, 200, 40, "⚙️ Kullanıcıları Yönet", sidebar_font)

    # Sağ taraf (İçerik) Elemanları - X koordinatları 250'ye kaydırıldı
    search_input = TextBox(250, 80, 400, 40, "Kitap Adı, Yazar veya ISBN...", font=font)
    search_btn = Button(660, 80, 100, 40, "Ara", font)
    logout_btn = Button(900, 20, 100, 40, "Çıkış", font)
    
    # --- BACKEND INITIALIZATION ---
    # Backend sistemini başlat
    db = LibrarySystem()
    
    # --- BOOK DATA INITIALIZATION ---
    # Dummy veri yerine backend'ten kitapları al
    dummy_books = db.get_all_books_as_list()
    
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
                    if btn_users.handle_event(event): print("Kullanıcı Yönetimi Sekmesi")

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
                                print(f"{dummy_books[i][1]} kitabını ödünç aldınız.")
                                break

        # === ÇİZİM (RENDERING) ===
        screen.fill(config.WHITE)
        
        # === GİRİŞ EKRANI ÇİZİMİ ===
        if current_state == config.STATE_LOGIN:
            # Başlık
            title = title_font.render("Librarian - Giriş", True, config.BLACK)
            screen.blit(title, (340, 150))
            
            # Rol Seçici
            role_selector.draw(screen)
            # Kullanıcı Adı
            user_input.draw(screen)
            # Şifre
            pass_input.draw(screen)
            # Giriş Butonu
            login_btn.draw(screen)
            
        # === ANA EKRAN ÇİZİMİ ===
        elif current_state == config.STATE_USER:
            # Sol Menü
            btn_library.draw(screen)
            btn_profile.draw(screen)
            if logged_in_role in ["Personel", "Yönetici"]:
                btn_inventory.draw(screen)
                btn_penalties.draw(screen)
            if logged_in_role == "Yönetici":
                btn_users.draw(screen)
            
            # Sağ Taraf Başlık
            title = title_font.render("Kitaplık", True, config.BLACK)
            screen.blit(title, (250, 30))
            
            # Arama Alanı
            search_input.draw(screen)
            search_btn.draw(screen)
            logout_btn.draw(screen)
            
            # Kitap Tablosu Başlıkları
            header_y = 185
            for i, header in enumerate(headers):
                text_surf = sidebar_font.render(header, True, config.BLACK)
                screen.blit(text_surf, (250 + i * 120, header_y))
            
            # Kitap Verileri ve Butonlar
            clip_rect = pygame.Rect(250, 185, 750, 550)
            screen.set_clip(clip_rect)
            
            for i, book in enumerate(dummy_books):
                row_y = 185 + (i * item_height) - scroll_y
                if row_y > 185 and row_y < 735:  # Sadece ekranın içindekileri çiz
                    # Kitap bilgilerini yaz
                    for j, data in enumerate(book):
                        text_surf = font.render(str(data), True, config.BLACK)
                        screen.blit(text_surf, (250 + j * 120, row_y + 5))
                    
                    # Ödünç Al Butonu (Sadece öğrenci ve stok varsa)
                    stok_sayisi = int(book[3])
                    if stok_sayisi > 0 and logged_in_role == "Öğrenci":
                        borrow_buttons[i].rect.y = row_y
                        borrow_buttons[i].draw(screen)
                    elif stok_sayisi == 0:
                        # Stokta yoksa uyarı yazısı
                        out_surf = sidebar_font.render("Stokta Yok", True, (200, 0, 0))
                        screen.blit(out_surf, (850, row_y + 5))
                    elif logged_in_role in ["Personel", "Yönetici"]:
                        # Personel ve Yönetici için başka işlemler olabilir
                        pass
                    
            screen.set_clip(None)
            
        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()

if __name__ == "__main__":
    main()