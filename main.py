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