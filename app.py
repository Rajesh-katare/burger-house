from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import datetime
import razorpay

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_burger_key_fallback')

# Razorpay Configuration
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_SdTuc0ah3PWYwr')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'emm75eBQZesbjDibdq2fhI99')
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Admin Credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'password')

# Configure SQLite Database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'burger_house.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

class MenuItem(db.Model):
    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    desc = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    icon = db.Column(db.String(10), nullable=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    delivery_address = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False, default="COD")
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default="Pending")
    lat = db.Column(db.Float, nullable=True)
    lng = db.Column(db.Float, nullable=True)
    razorpay_order_id = db.Column(db.String(100), nullable=True)
    razorpay_payment_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    menu_item_id = db.Column(db.String(20), db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    menu_item = db.relationship('MenuItem')

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/auth')
def auth():
    return render_template('auth.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('admin'))
        else:
            error = "Invalid Admin Credentials"
    return render_template('admin_login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
        
    users = User.query.all()
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin.html', users=users, orders=orders)

@app.route('/api/menu', methods=['GET'])
def get_menu():
    items = MenuItem.query.all()
    menu_list = []
    for item in items:
        menu_list.append({
            'id': item.id,
            'name': item.name,
            'price': item.price,
            'desc': item.desc,
            'image': item.image,
            'icon': item.icon
        })
    return jsonify(menu_list)

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    hashed_pw = generate_password_hash(password)
    new_user = User(name=name, email=email, password_hash=hashed_pw)
    db.session.add(new_user)
    db.session.commit()

    # Log user in
    session['user_id'] = new_user.id
    session['user_name'] = new_user.name
    
    return jsonify({"success": True, "user": {"name": new_user.name}})

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        session['user_name'] = user.name
        return jsonify({"success": True, "user": {"name": user.name}})
    
    return jsonify({"error": "Invalid email or password"}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return jsonify({"success": True})

@app.route('/api/auth/me', methods=['GET'])
def get_me():
    if 'user_id' in session:
        return jsonify({"authenticated": True, "user": {"name": session['user_name']}})
    return jsonify({"authenticated": False})

@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.json
    # data: { cart: [{id, qty}], address, phone, total_price }
    cart = data.get('cart', [])
    address = data.get('address')
    phone = data.get('phone')
    payment_method = data.get('payment_method', 'COD')
    total_price = data.get('total_price')
    lat = data.get('lat')
    lng = data.get('lng')

    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"error": "Unauthorized. Please log in first."}), 401

    new_order = Order(
        user_id=user_id,
        delivery_address=address,
        phone=phone,
        payment_method=payment_method,
        total_price=total_price,
        lat=lat,
        lng=lng
    )
    db.session.add(new_order)
    db.session.commit() # To get standard order_id

    for item in cart:
        order_item = OrderItem(
            order_id=new_order.id,
            menu_item_id=item['id'],
            quantity=item['qty']
        )
        db.session.add(order_item)
    
    db.session.commit()
    
    razorpay_order_id = None
    if payment_method != 'COD':
        # Create Razorpay order
        amount = int(total_price * 100) # Razorpay expects amount in paise
        currency = 'INR'
        
        try:
            payment = razorpay_client.order.create({
                "amount": amount,
                "currency": currency,
                "receipt": str(new_order.id),
                "payment_capture": 1
            })
            razorpay_order_id = payment['id']
            new_order.razorpay_order_id = razorpay_order_id
            db.session.commit()
        except Exception as e:
            print("Razorpay config error", e)
            # Will fail silently on frontend if key is placeholder, just return standard
    
    return jsonify({
        "success": True, 
        "order_id": new_order.id, 
        "razorpay_order_id": razorpay_order_id,
        "amount": int(total_price * 100)
    })

@app.route('/api/verify_payment', methods=['POST'])
def verify_payment():
    data = request.json
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_signature = data.get('razorpay_signature')
    order_id = data.get('order_id')
    
    try:
        # Verify the signature
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })
        
        # Payment is successful
        order = db.session.get(Order, order_id)
        if order:
            order.razorpay_payment_id = razorpay_payment_id
            order.status = "Preparing" # Skip Pending since payment is confirmed
            db.session.commit()
            
            # Explicitly capture the payment to allow real programmatic refunds later
            try:
                razorpay_client.payment.capture(razorpay_payment_id, int(order.total_price * 100))
                print(f"Successfully auto-captured payment {razorpay_payment_id}")
            except Exception as cap_e:
                print("Capture auto-skip, failed or already captured:", cap_e)
            
        return jsonify({"success": True})
    except Exception as e:
        print("Payment verification failed", e)
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/order/<int:order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
        
    user_id = session.get('user_id')
    if order.user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 401
        
    if order.status in ["Out for Delivery", "Delivered", "Cancelled"]:
        return jsonify({"error": "Order cannot be cancelled at this stage"}), 400
        
    refund_message = "Not Applicable"
    # Process Refund if paid online
    if order.razorpay_payment_id:
        try:
            # Refund requires amount in paise. Use speed: optimum to trigger Instant Refunds via Razorpay.
            razorpay_client.payment.refund(order.razorpay_payment_id, {
                'amount': int(order.total_price * 100),
                'speed': 'optimum'
            })
            refund_message = "Refund Initiated via Instant Transfer. It will reflect in your original payment method in under 10 minutes."
        except Exception as e:
            print("Refund failed, proceeding with manual refund flag", e)
            refund_message = "Automatic refund encountered an issue. Our support team will process your refund manually within 24 hours."
            
    order.status = "Cancelled"
    db.session.commit()
    return jsonify({
        "success": True, 
        "message": "Order cancelled successfully",
        "refund_message": refund_message
    })

@app.route('/order/<int:order_id>')
def order_tracking(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return "Order not found", 404
    return render_template('order_tracking.html', order=order)

@app.route('/api/order/<int:order_id>/status', methods=['GET'])
def order_status(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
        
    if order.status == "Cancelled":
        return jsonify({
            "order_id": order.id,
            "status": "Cancelled",
            "elapsed_seconds": 0,
            "total_expected_seconds": 2400,
            "created_at": order.created_at.isoformat() + 'Z'
        })
        
    now = datetime.datetime.utcnow()
    diff = (now - order.created_at).total_seconds()
    
    # Real-time progression (Total ~40 minutes / 2400 seconds)
    if diff < 120:          # 0-2 mins
        status = "Pending"
    elif diff < 900:        # 2-15 mins
        status = "Preparing"
    elif diff < 2400:       # 15-40 mins
        status = "Out for Delivery"
    else:
        status = "Delivered"
        
    # Optional: We can update the order status in the DB if we want it to persist for the admin view
    if order.status != status and status in ["Preparing", "Out for Delivery", "Delivered"]:
        order.status = status
        db.session.commit()
        
    return jsonify({
        "order_id": order.id,
        "status": status,
        "elapsed_seconds": diff,
        "total_expected_seconds": 2400,
        "created_at": order.created_at.isoformat() + 'Z'
    })

# Initialize DB tables if they don't exist (Must be outside __main__ for gunicorn/Render)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode)
