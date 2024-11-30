from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText

# Initialize the Flask application and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mail_app.db'
app.config['SECRET_KEY'] = 'gfhgfyj56765hgfjytvfy756vu67tvjhytu7v'
db = SQLAlchemy(app)


# ContactForm Model
class ContactForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Link to the user who submitted the form
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<ContactForm {self.name} - {self.email}>'

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# SentEmail Model
class SentEmail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    to_address = db.Column(db.String(150), nullable=False)
    subject = db.Column(db.String(150))
    body = db.Column(db.Text, nullable=False)

# Routes
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/about')
def about():
    return render_template('about.html')
# @app.route('/contact', methods=['GET', 'POST'])
# def contact():
#     if request.method == 'POST':
#         # Get form data
#         name = request.form['name']
#         email = request.form['email']
#         message = request.form['message']
        
#         # Here you can add logic to send the message via email or save it to a database
        
#         flash('Message has been successfully sent!', 'success')
#         return redirect(url_for('contact'))
    
#     return render_template('contact.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        
        new_user = User(username=username, email=email, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful!')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'danger')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    sent_emails = SentEmail.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html', sent_emails=sent_emails)

@app.route('/send_mail', methods=['POST'])
def send_mail():
    if 'user_id' not in session:
        flash('Please log in to send an email.', 'warning')
        return redirect(url_for('login'))

    # Email details from form
    from_address = request.form['from_address']
    app_password = request.form['app_password']
    to_address = request.form['to_address']
    subject = request.form['subject']
    body = request.form['body']
    
    # Set up SMTP connection
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    message = MIMEText(body)
    message['From'] = from_address
    message['To'] = to_address
    message['Subject'] = subject

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(from_address, app_password)
            server.sendmail(from_address, to_address, message.as_string())
        
        # Save email to database
        user_id = session['user_id']
        sent_email = SentEmail(user_id=user_id, to_address=to_address, subject=subject, body=body)
        db.session.add(sent_email)
        db.session.commit()

        flash('Email sent successfully!', 'success')
    except Exception as e:
        flash(f'Failed to send email: {str(e)}', 'danger')

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

OWNER_EMAIL = 'shubhamprajapati9537@gmail..com'  # Replace with the owner's email address

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        if 'user_id' not in session:
            flash('Please log in to submit the contact form.', 'warning')
            return redirect(url_for('login'))
        
        # Get form data
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        # Save the contact form details to the database
        try:
            user_id = session['user_id']
            contact_entry = ContactForm(user_id=user_id, name=name, email=email, message=message)
            db.session.add(contact_entry)
            db.session.commit()
            
            flash('Your message has been submitted successfully!', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting your message: {str(e)}', 'danger')
            return redirect(url_for('contact'))

    return render_template('contact.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True,host="0.0.0.0",port=5000)
