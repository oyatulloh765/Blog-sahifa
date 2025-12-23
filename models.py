from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from slugify import slugify
from extensions import db

# Association table for User Badges
user_badges = db.Table('user_badges',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('badge_id', db.Integer, db.ForeignKey('badge.id'), primary_key=True),
    db.Column('earned_at', db.DateTime, default=datetime.utcnow)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    google_id = db.Column(db.String(100), unique=True, nullable=True)  # Google OAuth ID
    is_admin = db.Column(db.Boolean, default=False)
    
    # Profile & Gamification
    avatar = db.Column(db.String(255), default='default_avatar.png')
    bio = db.Column(db.Text)
    role = db.Column(db.String(20), default='reader') # reader, author, admin
    points = db.Column(db.Integer, default=0)
    streak = db.Column(db.Integer, default=0)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    posts = db.relationship('Post', backref='author_ref', lazy=True)
    comments = db.relationship('Comment', backref='author_ref', lazy=True)
    badges = db.relationship('Badge', secondary=user_badges, lazy='subquery',
                           backref=db.backref('users', lazy=True))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(20), default='blue') # Tailwind color name
    posts = db.relationship('Post', backref='category', lazy=True)

    def __init__(self, name):
        self.name = name
        self.slug = slugify(name)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    video_url = db.Column(db.String(255)) # [NEW]
    audio_url = db.Column(db.String(255)) # [NEW]
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='published') # draft, published
    views = db.Column(db.Integer, default=0)
    
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)
        if self.title:
            self.slug = slugify(self.title)
    
    @property
    def read_time(self):
        words = len(self.content.split()) if self.content else 0
        return max(1, round(words / 200))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=True)
    
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # If user is not logged in
    author_name = db.Column(db.String(80)) 

class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    icon = db.Column(db.String(50)) # Valid lucide icon name
    criteria = db.Column(db.String(100)) # Internal code for award logic

class Analytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    page_views = db.Column(db.Integer, default=0)
    unique_visitors = db.Column(db.Integer, default=0)

class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(100), default='Mening Blogim')
    telegram = db.Column(db.String(100), default='@brend_ferghana')
    instagram = db.Column(db.String(200), default='https://www.instagram.com/oyatullomuxtorov/')
    github = db.Column(db.String(200), default='https://github.com/oyatulloh765')
    twitter = db.Column(db.String(200))
    youtube = db.Column(db.String(200))
    
    @staticmethod
    def get_settings():
        settings = SiteSettings.query.first()
        if not settings:
            settings = SiteSettings()
            db.session.add(settings)
            try:
                db.session.commit()
            except:
                db.session.rollback()
        return settings
