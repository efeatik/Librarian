# main.py

import pygame
import config
from ui_elements import Button, TextBox, RoleSelector

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
    
    # Özel örnek veri listesi
    dummy_books = [
        ["978-01", "İnsanlığımı Yitirirken", "Osamu Dazai", "3", "Müsait"],
        ["978-02", "Yeraltından Notlar", "Dostoyevski", "5", "Müsait"],
        ["978-03", "Budala", "Dostoyevski", "2", "Müsait"],
        ["978-04", "Beyaz Geceler", "Dostoyevski", "0", "Ödünç Verildi"],
        ["978-05", "Öteki", "Dostoyevski", "1", "Müsait"]
    ]
    # Kaydırma testi için ekstra kitaplar dolduruyoruz
    for i in range(6, 25):
        dummy_books.append([f"978-{i:02d}", f"Test Kitabı {i}", f"Yazar {i}", f"{i%4}", "Müsait"])

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
                    logged_in_role = role_selector.get_selected_role()
                    print(f"{logged_in_role} yetkisiyle giriş yapıldı.")
                    current_state = config.STATE_USER
                    scroll_y = 0 # Sayfa değişiminde scroll'u sıfırla
            
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

                mouse_x, mouse_y = pygame.mouse.get_pos()
                clip_rect = pygame.Rect(250, 185, 750, 550)

                # Scroll İşlemi (Sadece farenin x pozisyonu tablonun üzerindeyse çalışsın)
                mouse_x, _ = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEWHEEL and mouse_x > 220:
                    scroll_y += event.y * scroll_speed
                
                # Sadece fare tablo alanındaysa buton tıklamalarını dinle
                if clip_rect.collidepoint(mouse_x, mouse_y):
                    for i, btn in enumerate(borrow_buttons):
                        stok_sayisi = int(dummy_books[i][3])
                        
                        # Eğer stok 0'dan büyükse ve öğrenci yetkisiyle girildiyse
                        if stok_sayisi > 0 and logged_in_role == "Öğrenci":
                            # Butonun sanal Y koordinatını anlık olarak güncelle (World -> Screen)
                            btn.rect.y = 200 + (i * item_height) + scroll_y
                            
                            # Tıklama kontrolünü yap
                            if btn.handle_event(event):
                                print(f"[TALEP] {dummy_books[i][1]} kitabı için ödünç alma işlemi başlatıldı!")
                                # İleride burada borrow_book(user_id, isbn) fonksiyonu çağrılacak

        # SCROLL SINIRLARI
        if scroll_y > 0: scroll_y = 0
        max_scroll = max(0, (len(dummy_books) * item_height) - 500)
        if scroll_y < -max_scroll: scroll_y = -max_scroll

        # === ÇİZİM (RENDERING) ===
        screen.fill(config.WHITE)

        if current_state == config.STATE_LOGIN:
            screen.blit(title_font.render("Librarian Sistemine Giriş", True, config.BLACK), (340, 150))
            role_selector.draw(screen)
            user_input.draw(screen)
            pass_input.draw(screen)
            login_btn.draw(screen)

        elif current_state == config.STATE_USER:
            # 1. SOL MENÜ (SIDEBAR) ÇİZİMİ
            pygame.draw.rect(screen, config.DARK_GRAY, (0, 0, 220, config.HEIGHT))
            
            # Menü Başlığı
            role_surf = font.render(f"Rol: {logged_in_role}", True, config.WHITE)
            screen.blit(role_surf, (20, 30))
            pygame.draw.line(screen, config.WHITE, (10, 60), (210, 60), 1)

            # Rol Yetkilerine Göre Buton Çizimi (Conditional Rendering)
            btn_library.draw(screen)
            btn_profile.draw(screen)
            
            if logged_in_role in ["Personel", "Yönetici"]:
                btn_inventory.draw(screen)
                btn_penalties.draw(screen)
            
            if logged_in_role == "Yönetici":
                btn_users.draw(screen)

            # 2. SAĞ TARAF (İÇERİK) ÇİZİMİ
            screen.blit(title_font.render("Kütüphane Envanteri", True, config.BLUE), (250, 30))
            logout_btn.draw(screen)
            search_input.draw(screen)
            search_btn.draw(screen)
            
            # Tablo Başlıkları
            # Başlıkları Çiz
            for i, h in enumerate(headers):
                header_surf = font.render(h, True, config.BLACK)
                # Sütunları daha sıkı yerleştirmek için 130 px aralık
                screen.blit(header_surf, (250 + i*120, 150))
            
            pygame.draw.line(screen, config.BLACK, (250, 180), (1000, 180), 2)
            
            # Scroll Edilebilir Liste Alanı Maskesi
            clip_rect = pygame.Rect(250, 185, 750, 550)
            screen.set_clip(clip_rect)
            
            for index, book in enumerate(dummy_books):
                row_y = 200 + (index * item_height) + scroll_y
                stok = int(book[3])
                
                # Kitap bilgilerini metin olarak bas
                for i, val in enumerate(book):
                    color = config.BLACK if stok == 0 else config.DARK_GRAY
                    val_surf = font.render(val, True, color)
                    screen.blit(val_surf, (250 + i*120, row_y + 5))
                
                # Stok kontrolü 
                if stok > 0:
                    if logged_in_role == "Öğrenci":
                        # Butonun çizim pozisyonunu güncelle ve ekrana bas
                        borrow_buttons[index].rect.y = row_y
                        borrow_buttons[index].draw(screen)
                    elif logged_in_role in ["Personel", "Yönetici"]:
                        # Personel görüyorsa düzenle butonu olabilir, şimdilik boş
                        pass 
                else:
                    # Stok bittiyse butonu gizle, kırmızı uyarı yazısı koy
                    out_surf = sidebar_font.render("Stokta Yok", True, (200, 0, 0))
                    screen.blit(out_surf, (850, row_y + 5))
                    
            screen.set_clip(None)
            
        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()

if __name__ == "__main__":
    main()