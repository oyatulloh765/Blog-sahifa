from flask import Flask, render_template, abort, redirect, url_for, request, flash, jsonify
import os
import markdown
import bleach
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from datetime import datetime, timedelta

from extensions import db, login_manager, migrate, mail
from models import User, Post, Category, Comment, Badge, Analytics, SiteSettings
from forms import LoginForm, PostForm, CommentForm, ContactForm, RegistrationForm, UpdateAccountForm, SiteSettingsForm

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # 100MB limit

# Initialize extensions
db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
login_manager.login_view = 'login'
mail.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# --- Helpers ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'webp'}

# --- Context Processors ---
@app.context_processor
def inject_categories():
    settings = SiteSettings.get_settings()
    return dict(categories=Category.query.all(), site_settings=settings)

# --- Routes ---

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=6)
    return render_template('index.html', posts=posts)

@app.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    category_slug = request.args.get('category')
    search_query = request.args.get('q')
    
    query = Post.query
    
    if category_slug:
        category = Category.query.filter_by(slug=category_slug).first_or_404()
        query = query.filter_by(category_id=category.id)
    
    if search_query:
        query = query.filter(Post.title.contains(search_query) | Post.content.contains(search_query))
        
    posts = query.order_by(Post.created_at.desc()).paginate(page=page, per_page=9)
    return render_template('blog.html', posts=posts, search_query=search_query)

@app.route('/post/<slug>', methods=['GET', 'POST'])
def post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    
    # Increment views
    post.views += 1
    db.session.commit()
    
    # Convert markdown
    md = markdown.Markdown(extensions=['fenced_code', 'codehilite'])
    content = md.convert(post.content)
    # Sanitize HTML
    allowed_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'ul', 'ol', 'li', 'a', 'strong', 'em', 'code', 'pre', 'img', 'blockquote']
    allowed_attrs = {'*': ['class'], 'a': ['href', 'rel'], 'img': ['src', 'alt']}
    clean_content = bleach.clean(content, tags=allowed_tags, attributes=allowed_attrs)
    
    # Comments
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(author=form.author.data, content=form.content.data, post_id=post.id)
        db.session.add(comment)
        db.session.commit()
        flash('Izoh qoldirildi!', 'success')
        return redirect(url_for('post', slug=post.slug))
        
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.desc()).all()
    
    # Related posts
    related = Post.query.filter(Post.category_id == post.category_id, Post.id != post.id).limit(3).all()
    
    return render_template('post.html', post=post, content=clean_content, form=form, comments=comments, related=related)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # TODO: Send email
        flash('Xabaringiz yuborildi!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)

# --- Gamification Logic ---
def check_badges(user):
    # Badge 1: First Step (1 point)
    if user.points >= 1:
        badge = Badge.query.filter_by(name='Boshlang\'ich').first()
        if not badge:
            badge = Badge(name='Boshlang\'ich', description='Ilk qadam!', icon='footprints', criteria='points_1')
            db.session.add(badge)
            db.session.commit()
            
        if badge not in user.badges:
            user.badges.append(badge)
            flash(f"Tabriklaymiz! Siz '{badge.name}' nishonini oldingiz!", 'success')

    # Badge 2: Reader (5 posts read = 5 points approx)
    if user.points >= 10:
         badge = Badge.query.filter_by(name='Kitobxon').first()
         if not badge:
            badge = Badge(name='Kitobxon', description='10 ta maqola o\'qildi', icon='book-open', criteria='points_10')
            db.session.add(badge)
            db.session.commit()
            
         if badge not in user.badges:
            user.badges.append(badge)
            flash(f"Tabriklaymiz! Siz '{badge.name}' nishonini oldingiz!", 'success')
            
    db.session.commit()

# --- Auth Routes ---

@app.route('/post/<slug>/like', methods=['POST'])
@login_required
def like_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    # In V2, we might want a Like model, but for now simple point system
    # If we had a Like model:
    # like = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    
    # Simple Gamification: Award point for liking
    if current_user.points is None: current_user.points = 0
    current_user.points += 1
    check_badges(current_user)
    db.session.commit()
    
    return jsonify({'status': 'success', 'points': current_user.points})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Hisobingiz muvaffaqiyatli yaratildi! Endi kirishingiz mumkin.', 'success')
        return redirect(url_for('login'))
    return render_template('auth/register.html', title='Ro\'yxatdan o\'tish', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        flash('Login yoki parol noto\'g\'ri', 'error')
    return render_template('auth/login.html', title='Kirish', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, 'avatars')
            current_user.avatar = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('Hisobingiz ma\'lumotlari yangilandi!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.bio.data = current_user.bio
    image_file = url_for('static', filename='uploads/avatars/' + current_user.avatar)
    return render_template('auth/account.html', title='Profil', image_file=image_file, form=form)

def save_picture(form_picture, subdir=''):
    random_hex = os.urandom(8).hex()
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    path = os.path.join(app.config['UPLOAD_FOLDER'], subdir)
    if not os.path.exists(path):
        os.makedirs(path)
    picture_path = os.path.join(path, picture_fn)
    
    # Resize image could go here (using Pillow)
    form_picture.save(picture_path)
    
    return picture_fn

# --- Admin Routes ---

@app.route('/admin')
@login_required
def admin_dashboard():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    total_comments = Comment.query.count()
    total_users = User.query.count()
    return render_template('admin/dashboard.html', posts=posts, total_comments=total_comments, total_users=total_users)

@app.route('/admin/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    # Populate categories
    categories = Category.query.all()
    print(f"DEBUG: Found {len(categories)} categories")
    form.category.choices = [(c.id, c.name) for c in categories]
    
    # Debug: Print form data processing
    if request.method == 'POST':
        print("DEBUG: POST request received")
        print("DEBUG: Form data:", request.form)
        print("DEBUG: Validate on submit:", form.validate_on_submit())
        if not form.validate_on_submit():
            print("DEBUG: Form errors:", form.errors)

    if form.validate_on_submit():
        # Manual content check since SimpleMDE may not sync properly
        content_data = form.content.data or request.form.get('content', '')
        if not content_data.strip():
            flash('Xatolik: Maqola matni kiritilmagan!', 'error')
            return render_template('admin/editor.html', form=form, title="Yangi maqola")
        
        image_filename = None
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_filename = filename
            
        video_filename = None
        if form.video.data:
            filename = secure_filename(form.video.data.filename)
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos')
            if not os.path.exists(video_path): os.makedirs(video_path)
            form.video.data.save(os.path.join(video_path, filename))
            video_filename = filename

        audio_filename = None
        if form.audio.data:
            filename = secure_filename(form.audio.data.filename)
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'audio')
            if not os.path.exists(audio_path): os.makedirs(audio_path)
            form.audio.data.save(os.path.join(audio_path, filename))
            audio_filename = filename
            
        post = Post(
            title=form.title.data,
            content=content_data,
            summary=form.summary.data,
            category_id=form.category.data,
            image_url=image_filename,
            video_url=video_filename,
            audio_url=audio_filename
        )
        db.session.add(post)
        db.session.commit()
        flash('Maqola yaratildi!', 'success')
        return redirect(url_for('admin_dashboard'))
    elif request.method == 'POST':
        print("Form Errors:", form.errors) # Debug purpose
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Xatolik ({field}): {error}", 'error')
        if not form.errors:
            flash('Noma\'lum xatolik yuz berdi. Formani tekshiring.', 'error')
        
    return render_template('admin/editor.html', form=form, title="Yangi maqola")

@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    form = PostForm(obj=post)
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.summary = form.summary.data
        post.category_id = form.category.data
        
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            post.image_url = filename
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
        if form.video.data:
            filename = secure_filename(form.video.data.filename)
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos')
            if not os.path.exists(video_path): os.makedirs(video_path)
            form.video.data.save(os.path.join(video_path, filename))
            post.video_url = filename

        if form.audio.data:
            filename = secure_filename(form.audio.data.filename)
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'audio')
            if not os.path.exists(audio_path): os.makedirs(audio_path)
            form.audio.data.save(os.path.join(audio_path, filename))
            post.audio_url = filename
            
        db.session.commit()
        flash('Maqola yangilandi!', 'success')
        return redirect(url_for('admin_dashboard'))
        
    return render_template('admin/editor.html', form=form, title="Tahrirlash")

@app.route('/admin/delete/<int:id>')
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash('Maqola o\'chirildi', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    settings = SiteSettings.get_settings()
    form = SiteSettingsForm(obj=settings)
    
    if form.validate_on_submit():
        settings.site_name = form.site_name.data
        settings.telegram = form.telegram.data
        settings.instagram = form.instagram.data
        settings.github = form.github.data
        settings.twitter = form.twitter.data
        settings.youtube = form.youtube.data
        db.session.commit()
        flash('Sozlamalar saqlandi!', 'success')
        return redirect(url_for('admin_settings'))
        
    return render_template('admin/settings.html', form=form, settings=settings)

# --- CLI Commands ---
@app.cli.command("seed-db")
def seed_db():
    print("Seeding database...")
    db.create_all()
    # Create default admin if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@example.com', is_admin=True, role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        print("Admin created.")
        
        # Create default categories
        if not Category.query.first():
            db.session.add(Category(name='Dasturlash'))
            db.session.add(Category(name='Texnologiya'))
            db.session.add(Category(name='Hayot'))
            print("Categories created.")
            
        db.session.commit()
        print("Database seeded successfully.")

# --- Analytics & Middleware ---
@app.before_request
def track_analytics():
    if request.path.startswith('/static') or request.path.startswith('/api'):
        return
        
    today = datetime.utcnow().date()
    analytics = Analytics.query.filter_by(date=today).first()
    
    if not analytics:
        analytics = Analytics(date=today, page_views=0, unique_visitors=0)
        db.session.add(analytics)
    
    analytics.page_views = (analytics.page_views or 0) + 1
    # Simple unique visitor tracking (IP based - not perfect but okay for v2)
    # in real app use redis or session checking
    analytics.unique_visitors = (analytics.unique_visitors or 0) + 1 
    db.session.commit()

@app.route('/api/dashboard/stats')
@login_required
def dashboard_stats():
    # Last 7 days data
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=6)
    
    stats = Analytics.query.filter(Analytics.date >= start_date).order_by(Analytics.date).all()
    
    labels = [s.date.strftime('%d-%b') for s in stats]
    views = [s.page_views for s in stats]
    visitors = [s.unique_visitors for s in stats]
    
    # Fill missing dates if needed (skipped for simplicity for now)
    
    return jsonify({
        'labels': labels,
        'views': views,
        'visitors': visitors,
        'total_views': sum(views),
        'total_visitors': sum(visitors)
    })

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True, port=8000)
