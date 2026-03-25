# ✦ StarMatch AI — Celebrity Look-Alike Finder

> Upload your photo and discover which celebrity you resemble most using AI-powered face matching!

## 🚀 Quick Setup

Open a terminal in the project folder and run these commands in order:

### 1. Install Dependencies
```bash
pip install django deepface tf-keras Pillow numpy opencv-python-headless
```

### 2. Run Database Migrations
```bash
python manage.py makemigrations accounts matcher
python manage.py migrate
```

### 3. Seed Celebrity Database (downloads 30 celebrity images)
```bash
python manage.py seed_celebrities
```

### 4. Create Admin User (optional)
```bash
python manage.py createsuperuser
```

### 5. Start the Server
```bash
python manage.py runserver
```

### 6. Open in Browser
Visit: **http://127.0.0.1:8000/**

---

## 🎯 Features

- **AI Face Matching** — DeepFace-powered face comparison with VGG-Face model
- **Match Percentages** — See how closely you resemble each celebrity (0-100%)
- **User Authentication** — Full register/login system with session management
- **Drag & Drop Upload** — Modern upload UI with image preview
- **Match History** — Track all your past look-alike results  
- **30 Celebrities** — Hollywood (RDJ, Scarlett), Bollywood (SRK, Deepika), Sports (Ronaldo, Virat), Music (Taylor Swift, Billie Eilish)
- **Premium Dark UI** — Glassmorphic design with animated gradients

## 🛠 Tech Stack

| Component | Technology |
|---|---|
| Backend | Django 5.x |
| AI Engine | DeepFace (VGG-Face model) |
| Database | SQLite |
| Frontend | Django Templates + Vanilla CSS/JS |
| Auth | Django built-in auth |

## 📂 Project Structure

```
look aalike/
├── manage.py             # Django CLI
├── requirements.txt      # Dependencies
├── lookalike/             # Django project config
├── accounts/              # Auth app (register, login, logout)
├── matcher/               # Core app (upload, match, results, history)
│   ├── services.py        # DeepFace integration
│   └── management/        # seed_celebrities command
├── templates/             # Base HTML template
├── static/                # CSS & JS
└── media/                 # User uploads & celebrity images
```

## 📝 Notes

- **First run**: DeepFace auto-downloads the VGG-Face model (~580MB). This is one-time.
- **Celebrity images**: Downloaded from Wikipedia (public domain). For production, use licensed images.
- **Privacy**: All processing is local. No data sent to external services.

---

## 🚀 Deployment

### Railway (Recommended - Free & Easy)

1. **Fork/Clone this repo** to your GitHub account

2. **Connect to Railway**:
   - Go to [railway.app](https://railway.app)
   - Sign up/login with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your forked repo

3. **Environment Variables** (in Railway dashboard):
   ```
   SECRET_KEY=your-super-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=your-app-name.railway.app
   ```

4. **Database Setup**:
   - Railway auto-creates PostgreSQL database
   - Update `settings.py` DATABASES section if needed

5. **Deploy & Seed**:
   ```bash
   # In Railway shell or locally:
   python manage.py migrate
   python manage.py seed_celebrities --use-placeholders
   python manage.py createsuperuser
   ```

6. **Access your app** at the Railway-provided URL!

### Other Deployment Options

#### Render
- Similar to Railway, supports Django
- Free tier available
- Use `build.sh` and `start.sh` scripts

#### Heroku
- Create `Procfile` and push to Heroku
- May need to upgrade to paid tier due to ML model size

#### Local Development
- Follow the Quick Setup above
- Use `python manage.py runserver`

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Run `python manage.py collectstatic`
- [ ] Use PostgreSQL in production (SQLite is fine for small apps)
- [ ] Set up proper logging
- [ ] Configure backup strategy for database/media files
