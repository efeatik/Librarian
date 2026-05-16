# config.py

# Sistem Durumları (States)
STATE_LOGIN = "LOGIN"
STATE_ADMIN = "ADMIN_DASHBOARD"
STATE_STAFF = "STAFF_DASHBOARD"
STATE_USER = "USER_DASHBOARD"
STATE_USER_MANAGEMENT = "USER_MANAGEMENT"  # Yeni durum

# Ekran Ayarları
WIDTH, HEIGHT = 1024, 768
FPS = 60

# Renk Paleti (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
BLUE = (0, 122, 255)
HOVER_BLUE = (0, 100, 200) # Fare üzerine gelinceki renk
LIGHT_BLUE = (235, 245, 255) # Yumuşak mavi arka plan