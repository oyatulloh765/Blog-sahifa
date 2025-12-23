# 🦉 ProBlog - Professional Blog Platform V2

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Flask-3.x-green?style=for-the-badge&logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/Tailwind-CSS-38B2AC?style=for-the-badge&logo=tailwind-css" alt="Tailwind">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License">
</p>

Zamonaviy, professional va gamifikatsiyalashgan blog platformasi. Flask, Tailwind CSS, Alpine.js va GSAP texnologiyalari asosida qurilgan.

## ✨ Xususiyatlar

### 🎨 Frontend
- **Modern UI/UX** - Tailwind CSS bilan chiroyli dizayn
- **Dark/Light Mode** - Avtomatik qorong'u rejim
- **Responsive** - Barcha qurilmalarga moslashgan
- **GSAP Animatsiyalar** - Silliq animatsiyalar

### 🦉 Mascot (Interaktiv Hamroh)
- Har sahifada paydo bo'ladigan yashil qush
- Click qilganda gapiradi
- Turli holatlar: Idle, Happy, Reading

### 📊 Admin Panel
- **Dashboard** - Statistika va grafiklar (Chart.js)
- **Post Management** - CRUD operatsiyalari
- **Multimedia** - Rasm, Video, Audio yuklash
- **Site Settings** - Ijtimoiy tarmoqlar sozlamalari

### 🎮 Gamification
- **Point System** - Maqola o'qish uchun ballar
- **Badges** - Yutuq nishonlari
- **Reading Progress** - O'qish jarayoni ko'rsatkichi

### 👤 Foydalanuvchi Tizimi
- Ro'yxatdan o'tish / Kirish
- Profil sozlamalari (Avatar, Bio)
- "Like" va Izohlar

## 🚀 O'rnatish

### 1. Reponi klonlash
```bash
git clone https://github.com/oyatulloh765/Blog-sahifa.git
cd Blog-sahifa
```

### 2. Virtual muhit yaratish
```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# yoki
.\venv\Scripts\activate  # Windows
```

### 3. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 4. Ma'lumotlar bazasini sozlash
```bash
flask db upgrade
flask seed-db  # Admin va kategoriyalar yaratish
```

### 5. Serverni ishga tushirish
```bash
python app.py
```

Brauzerda ochish: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## 🔐 Admin Kirish
- **Username:** `admin`
- **Password:** `admin123`

## 📁 Loyiha Strukturasi

```
Blog-sahifa/
├── app.py              # Asosiy Flask ilovasi
├── models.py           # SQLAlchemy modellari
├── forms.py            # WTForms
├── extensions.py       # Flask extensionlar
├── requirements.txt    # Python kutubxonalari
├── static/
│   ├── js/
│   │   ├── mascot.js   # Mascot logikasi
│   │   └── charts.js   # Dashboard grafiklari
│   ├── uploads/        # Yuklangan fayllar
│   └── style.css
├── templates/
│   ├── base.html       # Asosiy shablon
│   ├── index.html      # Bosh sahifa
│   ├── post.html       # Maqola sahifasi
│   ├── admin/          # Admin shablonlari
│   └── auth/           # Auth shablonlari
└── migrations/         # Alembic migratsiyalari
```

## 🛠 Texnologiyalar

| Backend | Frontend | Database |
|---------|----------|----------|
| Flask 3.x | Tailwind CSS | SQLite |
| SQLAlchemy | Alpine.js | Flask-Migrate |
| Flask-Login | GSAP | Alembic |
| Flask-WTF | Chart.js | |

## 📸 Skrinshotlar

*Coming soon...*

## 📝 License

MIT License - Batafsil ma'lumot uchun [LICENSE](LICENSE) faylini ko'ring.

## 👨‍💻 Muallif

**Oyatulloh Muxtorov**
- GitHub: [@oyatulloh765](https://github.com/oyatulloh765)
- Telegram: [@brend_ferghana](https://t.me/brend_ferghana)
- Instagram: [@oyatullomuxtorov](https://instagram.com/oyatullomuxtorov)

---

<p align="center">Made with ❤️ in Uzbekistan 🇺🇿</p>
