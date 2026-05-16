# ui_elements.py
import pygame
import config

class Button:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = config.BLUE
        self.is_hovered = False

    def draw(self, surface):
        # Fare üzerine gelince renk değiştirme efekti
        current_color = config.HOVER_BLUE if self.is_hovered else self.color
        
        # Butonun arkaplanını çiz
        pygame.draw.rect(surface, current_color, self.rect, border_radius=8)
        
        # Metni oluştur ve butonun ortasına hizala
        text_surface = self.font.render(self.text, True, config.WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        # Farenin pozisyonunu al
        mouse_pos = pygame.mouse.get_pos()
        
        # Fare butonun üzerinde mi kontrol et (AABB mantığı)
        if self.rect.collidepoint(mouse_pos):
            self.is_hovered = True
            # Eğer sol tıklandıysa True döndür
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return True
        else:
            self.is_hovered = False
            
        return False
    


class TextBox:
    def __init__(self, x, y, width, height, placeholder="", is_password=False, font=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = config.GRAY
        self.text = ""
        self.placeholder = placeholder
        self.font = font
        self.active = False # Kutuya tıklandı mı? (Focus)
        self.is_password = is_password
        self.cursor_visible = True
        self.cursor_timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Kutunun içine tıklandı mı kontrolü
            if self.rect.collidepoint(event.pos):
                self.active = True
                self.color = config.BLUE # Aktifken renk değiştir
            else:
                self.active = False
                self.color = config.GRAY

        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return "SUBMIT"
            elif len(self.text) < 20: # Karakter sınırı
                self.text += event.unicode
        return None

    def draw(self, surface):
        # Arkaplan ve çerçeve
        pygame.draw.rect(surface, config.WHITE, self.rect)
        pygame.draw.rect(surface, self.color, self.rect, 2)

        # Metni hazırla (Şifreyse yıldız göster)
        display_text = "*" * len(self.text) if self.is_password else self.text
        
        # Boşsa placeholder göster
        if not self.text and not self.active:
            text_surface = self.font.render(self.placeholder, True, (150, 150, 150))
        else:
            text_surface = self.font.render(display_text, True, config.BLACK)

        surface.blit(text_surface, (self.rect.x + 10, self.rect.y + (self.rect.height - text_surface.get_height()) // 2))


class RoleSelector:
    def __init__(self, x, y, roles, font):
        self.rects = []
        self.roles = roles
        self.selected_index = 0  # Varsayılan olarak ilk rol seçili başlar
        self.font = font
        self.color = config.GRAY
        self.active_color = config.BLUE
        
        # Her bir rol için yan yana buton dikdörtgenleri (rect) oluştur
        btn_width = 110
        for i, role in enumerate(roles):
            rect = pygame.Rect(x + i * (btn_width + 10), y, btn_width, 35)
            self.rects.append(rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.rects):
                if rect.collidepoint(event.pos):
                    self.selected_index = i
                    return True
        return False
        
    def get_selected_role(self):
        # Seçili olan rolün metnini döndürür (Örn: "Personel")
        return self.roles[self.selected_index]

    def draw(self, surface):
        for i, rect in enumerate(self.rects):
            # Seçili olan kutuyu mavi, diğerlerini gri yap
            color = self.active_color if i == self.selected_index else self.color
            pygame.draw.rect(surface, color, rect, border_radius=5)
            
            # Seçili kutunun metnini beyaz, diğerlerini siyah yap
            text_color = config.WHITE if i == self.selected_index else config.BLACK
            text_surf = self.font.render(self.roles[i], True, text_color)
            text_rect = text_surf.get_rect(center=rect.center)
            surface.blit(text_surf, text_rect)