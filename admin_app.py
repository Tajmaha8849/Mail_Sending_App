from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash  # Import the missing function
from app import db, User  # Import the models from app.py
from app import ContactForm  # or from your app file where the model is defined


# Initialize the Flask application for admin
admin_app = Flask(__name__)
admin_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mail_app.db'
admin_app.config['SECRET_KEY'] = 'admin_secret_key'  # Secret key for admin app
db.init_app(admin_app)

# Hardcoded admin credentials
ADMIN_USERNAME = "shubham"
ADMIN_PASSWORD_HASH = generate_password_hash("admin9898")  # Replace "admin123" with your desired password

# Utility function to check admin login status
def is_admin():
    return session.get("is_admin", False)

# Admin login route
@admin_app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['is_admin'] = True
            session['admin_username'] = username
            flash('Admin session out successfully', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'danger')
    return render_template('admin_login.html')


# Admin logout route
@admin_app.route('/admin/logout')
def admin_logout():
    session.pop('admin_username', None)  # Remove the session variable
    # flash("Admin logged out", "success")  # Flash a success message for logged-out state
    return redirect(url_for('admin_login'))  # Redirect to the login page



# Admin dashboard route to view all users
@admin_app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin():
        flash("Admin access required to view this page", "danger")
        return redirect(url_for('admin_login'))

    users = User.query.all()  # List all users
    return render_template('admin_dashboard.html', users=users)

# Route to delete a user
@admin_app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if not is_admin():
        flash("Admin access required to perform this action", "danger")
        return redirect(url_for('admin_login'))

    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.username} has been deleted', 'success')
    else:
        flash('User not found', 'danger')
    
    return redirect(url_for('admin_dashboard'))
# Admin route to view user contact form details
@admin_app.route('/admin/contact_forms')
def view_contact_forms():
    if not is_admin():
        flash("Admin access required to view this page", "danger")
        return redirect(url_for('admin_login'))

    contact_forms = ContactForm.query.all()  # Fetch all contact forms from the database
    return render_template('admin_contact_forms.html', contact_forms=contact_forms)


# Run the admin application
if __name__ == "__main__":
    with admin_app.app_context():
        db.create_all()  # Ensure tables are created
    admin_app.run(debug=True, host="127.0.0.1", port=5001)  # Run on a different port
