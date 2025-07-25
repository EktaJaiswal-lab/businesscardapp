from flask import Flask, render_template, request, redirect, url_for, session, send_file
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, BusinessCard
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import qrcode
from io import BytesIO
import base64
from sqlalchemy import not_, or_

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Use SQLite for simplicity - change to MySQL if needed
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///business_card_db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

# Ensure admin user exists on startup
def ensure_admin_user():
    from models import User, db
    admin_email = "admin@gmail.com"
    admin_password = "Ej87567@"
    admin = User.query.filter_by(email=admin_email).first()
    if not admin:
        admin = User(
            name="Admin",
            email=admin_email,
            password=generate_password_hash(admin_password),
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()

# Call this function when the app starts
if __name__ == "__main__":
    with app.app_context():
        ensure_admin_user()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = 'new'

        if User.query.filter_by(email=email).first():
            return render_template('register.html', error="⚠️ Email already registered")
        
        user = User(name=name, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="❌ Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if user:
        if user.role == 'admin':
            users = User.query.filter(User.role != 'admin').all()
            user_cards = {u.id: BusinessCard.query.filter_by(user_id=u.id).all() for u in users}
            stats = {
                'total_users': User.query.filter(or_(User.role == 'subscription', User.role == 'new')).count(),
                'total_cards': BusinessCard.query.count(),
                'subscribers': User.query.filter(or_(User.role == 'subscription', User.role == 'new')).count()
            }
            return render_template('admin_dashboard.html', user=user, users=users, user_cards=user_cards, stats=stats)
        else:
            cards = BusinessCard.query.filter_by(user_id=user.id).all()
            can_create = user.role != 'new' or len(cards) < 1
            return render_template('dashboard.html', user=user, cards=cards, can_create=can_create)
    else:
        return redirect(url_for('login'))

@app.route('/upgrade-user/<int:user_id>', methods=['POST'])
def upgrade_user(user_id):
    if 'user_id' not in session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'success': False, 'error': 'Not logged in'}, 401
        return redirect(url_for('login'))
    admin = User.query.get(session['user_id'])
    if not admin or admin.role != 'admin':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'success': False, 'error': 'Unauthorized'}, 403
        return render_template('error.html', error_title="Unauthorized", error_message="Only admin can upgrade users.")
    user = User.query.get_or_404(user_id)
    if user.role == 'new':
        user.role = 'subscription'
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'success': True}
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'success': False, 'error': 'User is not new'}, 400
    return redirect(url_for('dashboard'))

@app.route('/unsubscribe-user/<int:user_id>', methods=['POST'])
def unsubscribe_user(user_id):
    if 'user_id' not in session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'success': False, 'error': 'Not logged in'}, 401
        return redirect(url_for('login'))
    admin = User.query.get(session['user_id'])
    if not admin or admin.role != 'admin':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'success': False, 'error': 'Unauthorized'}, 403
        return render_template('error.html', error_title="Unauthorized", error_message="Only admin can unsubscribe users.")
    user = User.query.get_or_404(user_id)
    if user.role == 'subscription':
        user.role = 'new'
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'success': True}
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'success': False, 'error': 'User is not a subscriber'}, 400
    return redirect(url_for('dashboard'))

@app.route('/new-card', methods=['GET', 'POST'])
def new_card():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    if user.role == 'new' and BusinessCard.query.filter_by(user_id=user.id).count() >= 1:
        return render_template('error.html', 
                             error_title="Card Limit Reached",
                             error_message="⚠️ Only one card allowed for new users.",
                             error_icon="info-circle")

    if request.method == 'POST':
        name = request.form['name']
        designation = request.form['designation']
        company = request.form['company']
        mobile = request.form['mobile']
        email = request.form['email']
        
        # Handle logo upload
        logo_path = None
        if 'logo' in request.files and request.files['logo'].filename:
            logo_file = request.files['logo']
            filename = logo_file.filename
            if filename and filename.strip():
                filename = secure_filename(filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                logo_file.save(filepath)
                logo_path = f"/static/uploads/{filename}"

        # Generate PDF and QR
        pdf_filename = f"{name.replace(' ', '_')}_card.pdf"
        qr_filename = f"{name.replace(' ', '_')}_qr.png"
        vcf_filename = f"{name.replace(' ', '_')}.vcf"
        
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
        qr_path = os.path.join(app.config['UPLOAD_FOLDER'], qr_filename)
        vcf_path = os.path.join(app.config['UPLOAD_FOLDER'], vcf_filename)
        
        generate_pdf(name, designation, company, mobile, email, pdf_path)
        generate_qr(name, designation, company, mobile, email, qr_path)
        generate_vcard(name, designation, company, mobile, email, vcf_path)

        if user:
            card = BusinessCard(
                user_id=user.id,
                name=name,
                designation=designation,
                company=company,
                mobile=mobile,
                email=email,
                logo=logo_path,
                pdf=f"/static/uploads/{pdf_filename}",
                qr=f"/static/uploads/{qr_filename}",
                # Optionally, you can add a vcf field to the model if you want to store the path
            )
            db.session.add(card)
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            return render_template('error.html',
                                 error_title="User Not Found",
                                 error_message="❌ User not found",
                                 error_icon="user-times")

    return render_template('form.html', card=None)

@app.route('/edit-card/<int:card_id>', methods=['GET', 'POST'])
def edit_card(card_id):
    card = BusinessCard.query.get_or_404(card_id)
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    if not user or (card.user_id != user.id and user.role != 'admin'):
        return render_template('error.html',
                             error_title="Unauthorized Access",
                             error_message="❌ You don't have permission to access this card",
                             error_icon="lock")

    if request.method == 'POST':
        card.name = request.form['name']
        card.designation = request.form['designation']
        card.company = request.form['company']
        card.mobile = request.form['mobile']
        card.email = request.form['email']

        if 'logo' in request.files and request.files['logo'].filename:
            logo_file = request.files['logo']
            filename = logo_file.filename
            if filename and filename.strip():
                filename = secure_filename(filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                logo_file.save(filepath)
                card.logo = f"/static/uploads/{filename}"

        # Regenerate PDF and QR
        pdf_filename = f"{card.name.replace(' ', '_')}_card.pdf"
        qr_filename = f"{card.name.replace(' ', '_')}_qr.png"
        vcf_filename = f"{card.name.replace(' ', '_')}.vcf"
        
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
        qr_path = os.path.join(app.config['UPLOAD_FOLDER'], qr_filename)
        vcf_path = os.path.join(app.config['UPLOAD_FOLDER'], vcf_filename)
        
        generate_pdf(card.name, card.designation, card.company, card.mobile, card.email, pdf_path)
        generate_qr(card.name, card.designation, card.company, card.mobile, card.email, qr_path)
        generate_vcard(card.name, card.designation, card.company, card.mobile, card.email, vcf_path)
        
        card.pdf = f"/static/uploads/{pdf_filename}"
        card.qr = f"/static/uploads/{qr_filename}"

        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('form.html', card=card)

@app.route('/view-card/<int:card_id>')
def view_card(card_id):
    card = BusinessCard.query.get_or_404(card_id)
    if 'user_id' not in session or card.user_id != session['user_id']:
        return render_template('error.html',
                             error_title="Unauthorized Access",
                             error_message="❌ You don't have permission to access this card",
                             error_icon="lock")
    
    return render_template('card.html', card=card)

@app.route('/delete-card/<int:card_id>', methods=['POST'])
def delete_card(card_id):
    card = BusinessCard.query.get_or_404(card_id)
    if 'user_id' not in session or card.user_id != session['user_id']:
        return render_template('error.html', error_title="Unauthorized", error_message="You can't delete this card.")
    db.session.delete(card)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/download-vcard/<name>')
def download_vcard(name):
    vcf_filename = f"{name.replace(' ', '_')}.vcf"
    vcf_path = os.path.join(app.config['UPLOAD_FOLDER'], vcf_filename)
    if os.path.exists(vcf_path):
        return send_file(vcf_path, as_attachment=True, download_name=vcf_filename, mimetype='text/vcard')
    else:
        return render_template('error.html', error_title="File Not Found", error_message="❌ vCard file not found", error_icon="file")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

def generate_pdf(name, designation, company, mobile, email, output_path):
    """Generate a PDF business card"""
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    # Set up the card layout
    card_width = 3.5 * inch
    card_height = 2 * inch
    x = (width - card_width) / 2
    y = height - 2 * inch
    
    # Draw card border
    c.rect(x, y, card_width, card_height)
    
    # Add content
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x + 0.2 * inch, y + 1.5 * inch, name)
    
    c.setFont("Helvetica", 12)
    c.drawString(x + 0.2 * inch, y + 1.2 * inch, designation)
    c.drawString(x + 0.2 * inch, y + 0.9 * inch, company)
    c.drawString(x + 0.2 * inch, y + 0.6 * inch, f"Mobile: {mobile}")
    c.drawString(x + 0.2 * inch, y + 0.3 * inch, f"Email: {email}")
    
    c.save()

def generate_qr(name, designation, company, mobile, email, output_path):
    """Generate a QR code with contact information"""
    # Create vCard format
    vcard_data = f"""BEGIN:VCARD
VERSION:3.0
FN:{name}
TITLE:{designation}
ORG:{company}
TEL;TYPE=CELL:{mobile}
EMAIL:{email}
END:VCARD"""
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(vcard_data)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)

def generate_vcard(name, designation, company, mobile, email, output_path):
    """Generate a vCard (.vcf) file for contact saving"""
    vcard_data = f"""BEGIN:VCARD\nVERSION:3.0\nN:{name}\nFN:{name}\nTITLE:{designation}\nORG:{company}\nTEL;TYPE=CELL:{mobile}\nEMAIL:{email}\nEND:VCARD"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(vcard_data)

if __name__ == '__main__':
    print("🚀 Starting Flask app...")
    with app.app_context():
        print("🛠 Creating all tables...")
        db.create_all()
    app.run(debug=True, port=8000)
