from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
from flask_cors import CORS
from sqlalchemy import func
from enum import Enum
from flask_mail import Mail, Message
from flask_caching import Cache
from celery import Celery
from celery.schedules import crontab, schedule
from datetime import datetime, timezone
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import and_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'librarymanagementsystem'  
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

#Configuring flask-mail
app.config['MAIL_SERVER'] = 'localhost'
app.config['MAIL_PORT'] = 1025  # Default Mailhog SMTP port
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False

#Configuring flask cache
# Caching configuration
app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'  # Using database 0 for caching
app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # 5 minutes default timeout

#Configure Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/1'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/2'



# Configure CORS
CORS(app, origins='*')
db = SQLAlchemy(app)
jwt = JWTManager(app)
mail = Mail(app)
cache = Cache(app)

# Create Celery app
celery = Celery(app.name)
celery.conf.update(app.config)

# Configure Celery to use Redis for task results
celery.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0'
)



#--------------------------------------------MODELS--------------------------------------------


# Enum for loan status
class LoanStatus(Enum):
    ACTIVE = 'active'
    RETURNED = 'returned'
    REVOKED = 'revoked'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    loans = db.relationship('Loan', backref='user', lazy=True)

class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    ebooks = db.relationship('Ebook', backref='section', lazy=True)

class Ebook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)  # Changed to Text for potentially longer content
    author = db.Column(db.String(150), nullable=False)
    date_issued = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    loans = db.relationship('Loan', backref='ebook', lazy=True)

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ebook_id = db.Column(db.Integer, db.ForeignKey('ebook.id'), nullable=False)
    date_loaned = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    due_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc) + timedelta(days=14))
    date_returned = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum(LoanStatus), default=LoanStatus.ACTIVE, nullable=False)





# Create the database tables
with app.app_context():
    db.create_all()
    print("Database tables created.")

#--------------------------------------------ROUTES--------------------------------------------


#Helper Function
def is_admin():
    current_user = User.query.get(get_jwt_identity())
    return current_user and current_user.role == 'admin'



#register
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({"message": "Missing required fields"}), 400
    
    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"message": "Username or email already exists"}), 400
    
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, email=email, password=hashed_password, role='user')
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully"}), 201


#-----------------login-----------------
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=1))
    user_info = {
        'user_id': user.id,
        'username': user.username,
        'role': user.role,
    }

    return jsonify({'access_token': access_token, 'user': user_info}), 200

#----------------logout-----------------
@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    resp = jsonify({'message': 'Logged out successfully'})
    unset_jwt_cookies(resp)
    return resp, 200

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "API is working"}), 200

#--------------------------------------------------Sections--------------------------------------------------
@app.route('/api/sections', methods=['GET'])
@cache.cached(timeout=60)  
def get_sections():
    sections = Section.query.all()
    return jsonify({
        'sections': [{
            'id': section.id,
            'name': section.name,
            'description': section.description,
        } for section in sections]
    }), 200

@app.route('/api/sections/<int:section_id>', methods=['GET'])
def get_section_books(section_id):
    section = Section.query.get_or_404(section_id)
    books = Ebook.query.filter_by(section_id=section_id).all()
    return jsonify({
        'section': {
            'id': section.id,
            'name': section.name,
            'description': section.description,
        },
        'books': [{
            'id': book.id,
            'name': book.name,
            'author': book.author,
            'date_issued': book.date_issued.isoformat()
        } for book in books]
    }), 200

@app.route('/api/sections', methods=['POST'])
@jwt_required()
def create_section():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'admin':
        return jsonify({'message': 'Unauthorized access'}), 403
    
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    
    if not name or not description:
        return jsonify({'message': 'Section name and description are required'}), 400
    
    new_section = Section(name=name, description=description)
    db.session.add(new_section)
    db.session.commit()
    cache.delete_memoized(get_sections)
    
    return jsonify({
        'message': 'Section created successfully',
        'section': {
            'id': new_section.id,
            'name': new_section.name,
            'description': new_section.description,
        }
    }), 201



#--------------------------------------------------Ebooks--------------------------------------------------
@app.route('/api/books', methods=['GET'])
@cache.cached(timeout=60)  
def get_books():
    books = Ebook.query.all()
    return jsonify({
        'books': [{
            'id': book.id,
            'name': book.name,
            'author': book.author,
            'section_id': book.section_id,
            'date_issued': book.date_issued.isoformat()
        } for book in books]
    }), 200

@app.route('/api/books', methods=['POST'])
@jwt_required()
def add_book():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'admin':
        return jsonify({'message': 'Unauthorized access'}), 403
    
    data = request.get_json()
    name = data.get('name')
    content = data.get('content')
    author = data.get('author')
    section_id = data.get('section_id')
    
    if not all([name, content, author, section_id]):
        return jsonify({'message': 'All fields are required'}), 400
    
    section = Section.query.get(section_id)
    if not section:
        return jsonify({'message': 'Invalid section ID'}), 400
    
    new_book = Ebook(name=name, content=content, author=author, section_id=section_id)
    db.session.add(new_book)
    db.session.commit()
    cache.delete_memoized(get_books)
    
    return jsonify({
        'message': 'Book added successfully',
        'book': {
            'id': new_book.id,
            'name': new_book.name,
            'author': new_book.author,
            'section_id': new_book.section_id,
            'date_issued': new_book.date_issued.isoformat()
        }
    }), 201



#------------------------------------------Update and Delete Routes------------------------------------------

@app.route('/api/sections/<int:section_id>', methods=['PUT'])
@jwt_required()
def update_section(section_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'admin':
        return jsonify({'message': 'Unauthorized access'}), 403
    
    section = Section.query.get_or_404(section_id)
    data = request.get_json()
    
    section.name = data.get('name', section.name)
    section.description = data.get('description', section.description)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Section updated successfully',
        'section': {
            'id': section.id,
            'name': section.name,
            'description': section.description,
        }
    }), 200

@app.route('/api/sections/<int:section_id>', methods=['DELETE'])
@jwt_required()
def delete_section(section_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'admin':
        return jsonify({'message': 'Unauthorized access'}), 403
    
    section = Section.query.get_or_404(section_id)
    
    # Get all books in the section
    books = Ebook.query.filter_by(section_id=section_id).all()
    
    # Delete all loans associated with each book
    for book in books:
        Loan.query.filter_by(ebook_id=book.id).delete()
    
    # Delete all books associated with this section
    Ebook.query.filter_by(section_id=section_id).delete()
    
    # Delete the section
    db.session.delete(section)
    db.session.commit()
    
    return jsonify({'message': 'Section, associated books, and loans deleted successfully'}), 200

@app.route('/api/books/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'admin':
        return jsonify({'message': 'Unauthorized access'}), 403
    
    book = Ebook.query.get_or_404(book_id)
    data = request.get_json()
    
    book.name = data.get('name', book.name)
    book.author = data.get('author', book.author)
    book.content = data.get('content', book.content)
    book.section_id = data.get('section_id', book.section_id)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Book updated successfully',
        'book': {
            'id': book.id,
            'name': book.name,
            'author': book.author,
            'section_id': book.section_id,
            'date_issued': book.date_issued.isoformat()
        }
    }), 200

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'admin':
        return jsonify({'message': 'Unauthorized access'}), 403
    
    book = Ebook.query.get_or_404(book_id)
    
    # Delete all loans associated with this book
    Loan.query.filter_by(ebook_id=book_id).delete()
    
    # Delete the book
    db.session.delete(book)
    db.session.commit()
    
    return jsonify({'message': 'Book and associated loans deleted successfully'}), 200





#--------------------------------------------------Loans--------------------------------------------------



@app.route('/api/books/<int:book_id>', methods=['GET'])
@jwt_required()
def get_book_details(book_id):
    book = Ebook.query.get_or_404(book_id)
    current_user_id = get_jwt_identity()

    active_loan = Loan.query.filter(
        and_(Loan.ebook_id == book_id, Loan.status == LoanStatus.ACTIVE)
    ).first()

    loan_info = {
        'status': 'available',
        'loan_id': None,
        'date_loaned': None,
        'due_date': None,
        'is_current_user_loan': False
    }

    if active_loan:
        loan_info.update({
            'status': 'active',
            'loan_id': active_loan.id,
            'date_loaned': active_loan.date_loaned.isoformat(),
            'due_date': active_loan.due_date.isoformat(),
            'is_current_user_loan': active_loan.user_id == current_user_id
        })

    return jsonify({
        'book': {
            'id': book.id,
            'name': book.name,
            'author': book.author,
            'content': book.content,
            'section_id': book.section_id,
            'date_issued': book.date_issued.isoformat(),
            'loan_info': loan_info
        }
    }), 200

@app.route('/api/loans', methods=['POST'])
@jwt_required()
def loan_book():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    book_id = data.get('book_id')

    if not book_id:
        return jsonify({'message': 'Book ID is required'}), 400

    book = Ebook.query.get(book_id)
    if not book:
        return jsonify({'message': 'Invalid book ID'}), 400

    # Check if the book is already loaned
    existing_loan = Loan.query.filter(
        and_(Loan.ebook_id == book_id, Loan.status == LoanStatus.ACTIVE)
    ).first()
    if existing_loan:
        return jsonify({'message': 'This book is already loaned'}), 400

    active_loans_count = Loan.query.filter_by(user_id=current_user_id, status=LoanStatus.ACTIVE).count()
    if active_loans_count >= 5:
        return jsonify({'message': 'You have reached the maximum number of active loans (5)'}), 400

    new_loan = Loan(user_id=current_user_id, ebook_id=book_id, status=LoanStatus.ACTIVE)
    db.session.add(new_loan)
    db.session.commit()

    return jsonify({
        'message': 'Book loaned successfully',
        'loan': {
            'id': new_loan.id,
            'book_id': new_loan.ebook_id,
            'date_loaned': new_loan.date_loaned.isoformat(),
            'due_date': new_loan.due_date.isoformat(),
            'status': new_loan.status.value
        }
    }), 201

@app.route('/api/loans/<int:loan_id>/return', methods=['POST'])
@jwt_required()
def return_book(loan_id):
    current_user_id = get_jwt_identity()
    loan = Loan.query.get(loan_id)

    if not loan:
        return jsonify({'message': 'Invalid loan ID'}), 400

    if loan.user_id != current_user_id:
        return jsonify({'message': 'Unauthorized access'}), 403

    if loan.status != LoanStatus.ACTIVE:
        return jsonify({'message': 'This loan is not active'}), 400

    loan.status = LoanStatus.RETURNED
    loan.date_returned = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({
        'message': 'Book returned successfully',
        'loan': {
            'id': loan.id,
            'book_id': loan.ebook_id,
            'date_loaned': loan.date_loaned.isoformat(),
            'date_returned': loan.date_returned.isoformat(),
            'status': loan.status.value
        }
    }), 200

@app.route('/api/user/loans', methods=['GET'])
@jwt_required()
def get_user_loans():
    current_user_id = get_jwt_identity()
    loans = Loan.query.filter_by(user_id=current_user_id).all()

    return jsonify({
        'loans': [{
            'id': loan.id,
            'book_id': loan.ebook_id,
            'book_name': loan.ebook.name,
            'date_loaned': loan.date_loaned.isoformat(),
            'due_date': loan.due_date.isoformat(),
            'date_returned': loan.date_returned.isoformat() if loan.date_returned else None,
            'status': loan.status.value
        } for loan in loans]
    }), 200

@app.route('/api/admin/loans/active', methods=['GET'])
@jwt_required()
def get_active_loans():
    if not is_admin():
        return jsonify({"msg": "Admin access required"}), 403
    
    active_loans = Loan.query.filter_by(status=LoanStatus.ACTIVE).all()
    return jsonify([{
        'id': loan.id,
        'user': loan.user.username,
        'ebook': loan.ebook.name,
        'date_loaned': loan.date_loaned.strftime('%Y-%m-%d %H:%M:%S'),
        'due_date': loan.due_date.strftime('%Y-%m-%d %H:%M:%S')
    } for loan in active_loans]), 200

@app.route('/api/admin/loans/all', methods=['GET'])
@jwt_required()
def get_all_loans():
    if not is_admin():
        return jsonify({"msg": "Admin access required"}), 403
    
    all_loans = Loan.query.all()
    return jsonify([{
        'id': loan.id,
        'user': loan.user.username,
        'ebook': loan.ebook.name,
        'date_loaned': loan.date_loaned.strftime('%Y-%m-%d %H:%M:%S'),
        'due_date': loan.due_date.strftime('%Y-%m-%d %H:%M:%S'),
        'date_returned': loan.date_returned.strftime('%Y-%m-%d %H:%M:%S') if loan.date_returned else None,
        'status': loan.status.value
    } for loan in all_loans]), 200

@app.route('/api/admin/loans/revoke/<int:loan_id>', methods=['POST'])
@jwt_required()
def revoke_loan(loan_id):
    if not is_admin():
        return jsonify({"msg": "Admin access required"}), 403
    
    loan = Loan.query.get_or_404(loan_id)
    loan.status = LoanStatus.REVOKED
    loan.date_returned = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"msg": "Loan revoked successfully"}), 200



#---------------------------------User Routes---------------------------------
@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    if not is_admin():
        return jsonify({"message": "Admin access required"}), 403
    
    users = User.query.filter(User.role != 'admin').all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role
    } for user in users]), 200

@app.route('/api/admin/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_details(user_id):
    if not is_admin():
        return jsonify({"message": "Admin access required"}), 403
    
    user = User.query.get_or_404(user_id)
    loans = Loan.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        },
        'loans': [{
            'id': loan.id,
            'ebook_id': loan.ebook_id,
            'ebook_name': loan.ebook.name,
            'date_loaned': loan.date_loaned.isoformat(),
            'due_date': loan.due_date.isoformat(),
            'date_returned': loan.date_returned.isoformat() if loan.date_returned else None,
            'status': loan.status.value
        } for loan in loans]
    }), 200

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    if not is_admin():
        return jsonify({"message": "Admin access required"}), 403
    
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        return jsonify({"message": "Cannot delete admin user"}), 400
    
    # Delete all loans associated with the user
    Loan.query.filter_by(user_id=user_id).delete()
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"message": "User deleted successfully"}), 200




#----------------------------CELERY TASKS--------------------------------


@celery.task
def revoke_overdue_loans():
    with app.app_context():
        overdue_loans = Loan.query.filter(
            and_(Loan.due_date < datetime.now(timezone.utc), Loan.status == LoanStatus.ACTIVE)
        ).all()
        for loan in overdue_loans:
            loan.status = LoanStatus.REVOKED
            loan.date_returned = datetime.now(timezone.utc)
        db.session.commit()
        print(f"Revoked {len(overdue_loans)} overdue loans.")
    return f"Revoked {len(overdue_loans)} overdue loans."

@celery.task
def send_daily_reminders():
    with app.app_context():
        active_loans = Loan.query.filter_by(status=LoanStatus.ACTIVE).all()
        for loan in active_loans:
            user = User.query.get(loan.user_id)
            book = Ebook.query.get(loan.ebook_id)
            msg = Message("Daily Library Reminder",
                          sender="library@example.com",
                          recipients=[user.email])
            msg.body = f"Hello {user.username},\n\nThis is a reminder that you have borrowed '{book.name}'. It is due on {loan.due_date.strftime('%Y-%m-%d')}.\n\nBest regards,\nYour Library"
            mail.send(msg)
        print(f"Sent {len(active_loans)} daily reminders.")
    return f"Sent {len(active_loans)} daily reminders."

@celery.task
def generate_monthly_report():
    with app.app_context():
        users = User.query.filter(User.role != 'admin').all()
        report_count = 0
        for user in users:
            # Get user's loans from the past month
            start_date = datetime.now(timezone.utc).replace(day=1) - timedelta(days=1)
            end_date = datetime.now(timezone.utc)
            loans = Loan.query.filter(
                and_(Loan.user_id == user.id, Loan.date_loaned >= start_date, Loan.date_loaned <= end_date)
            ).all()

            # Generate HTML report
            report = f"""
            <html>
            <body>
            <h1>Monthly Activity Report for {user.username}</h1>
            <h2>Books Borrowed:</h2>
            <ul>
            """
            for loan in loans:
                report += f"<li>{loan.ebook.name} - Borrowed on: {loan.date_loaned.strftime('%Y-%m-%d')}</li>"
            
            report += """
            </ul>
            </body>
            </html>
            """

            # Send email
            try:
                msg = Message("Monthly Library Activity Report",
                              sender="library@example.com",
                              recipients=[user.email])
                msg.html = report
                mail.send(msg)
                report_count += 1
            except Exception as e:
                print(f"Failed to send report to {user.email}: {str(e)}")
        
        print(f"Sent monthly reports to {report_count} users.")
    return f"Sent monthly reports to {report_count} users."


# Celery Beat Schedule
celery.conf.beat_schedule = {
    'revoke-overdue-loans-midnight': {
        'task': 'app.revoke_overdue_loans',
        'schedule': crontab(hour=0, minute=1),
    },
    'send-daily-reminders-9am': {
        'task': 'app.send_daily_reminders',
        'schedule': crontab(hour=9, minute=0),
    },
    'generate-monthly-reports': {
        'task': 'app.generate_monthly_report',
        'schedule': crontab(day_of_month=1, hour=6, minute=0),
    },
}

# Test routes to manually trigger Celery tasks
@app.route('/test/revoke-overdue-loans', methods=['GET'])
def test_revoke_overdue_loans():
    result = revoke_overdue_loans.delay()
    return jsonify({"message": "Task started", "task_id": result.id}), 202

@app.route('/test/send-daily-reminders', methods=['GET'])
def test_send_daily_reminders():
    result = send_daily_reminders.delay()
    return jsonify({"message": "Task started", "task_id": result.id}), 202

@app.route('/test/generate-monthly-report', methods=['GET'])
def test_generate_monthly_report():
    result = generate_monthly_report.delay()
    return jsonify({"message": "Task started", "task_id": result.id}), 202




#app run
if __name__ == '__main__':
    app.run(debug=True, 
            port=8000)
    
    
