# Librarian - Kütüphane Envanter Yönetim Sistemi

Librarian, Python programlama dili ve Pygame kütüphanesi kullanılarak geliştirilmiş, olay güdümlü bir kütüphane envanter yönetim sistemidir. Bu proje, geleneksel konsol uygulamalarından farklı olarak, kendi özel grafiksel kullanıcı arayüzünü sıfırdan inşa eden nesne yönelimli bir yaklaşımla tasarlanmıştır.

## Proje Hakkında

Bakırçay Üniversitesi Bilgisayar Mühendisliği Bölümü "Mühendislikte Proje Yönetimi" dersi kapsamında geliştirilen bu sistem, temel kütüphanecilik işlemlerini dijitalleştirmeyi amaçlamaktadır. Projede harici bir ilişkisel veritabanı yerine, algoritmik arama ve sıralama verimliliğini test etmek amacıyla JSON tabanlı yerel bir veri depolama mimarisi kullanılmıştır.

## Temel Özellikler

* **Özel Grafiksel Arayüz:** Pygame tabanlı state machine ile oluşturulmuş, butonlar, metin girdileri ve dinamik tablolar barındıran UI.
* **Rol Bazlı Yetkilendirme:** Yönetici (Admin), Personel (Staff) ve Öğrenci (User) olmak üzere üç farklı erişim seviyesi.
* **Güvenlik:** Kullanıcı parolalarının hashlib kütüphanesi ile SHA-256 algoritması kullanılarak şifrelenmesi.
* **Kalıcı Veri Depolama:** Verilerin bellek üzerinde Hash Map yapılarında $O(1)$ karmaşıklığında yönetilmesi ve eşzamanlı olarak JSON formatında dosyalara yazılması.
* **Gelişmiş Arama ve Sıralama:** Alt dize eşleştirme ve yerleşik algoritmalar ile hızlı envanter sorgulama.
* **Ödünç / İade Döngüsü:** Stok durumu ve `datetime` modülü ile zaman kısıtlamalı, gecikme tespitli işlem yönetimi.

## Kurulum ve Çalıştırma

1. Repoyu bilgisayarınıza klonlayın:
   `git clone https://github.com/efeatik/Librarian`
2. Gerekli kütüphaneleri yükleyin:
   `pip install pygame`
3. Ana dizindeki başlatıcı dosyayı çalıştırın:
   `python main.py`
