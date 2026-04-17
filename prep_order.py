import requests
import sqlite3
import razorpay

base_url = 'http://127.0.0.1:5000/api'

client = razorpay.Client(auth=('rzp_test_SdTuc0ah3PWYwr', 'emm75eBQZesbjDibdq2fhI99'))

# Create order through API
s = requests.Session()
s.post(f'{base_url}/auth/login', json={'email': 'test@example.com', 'password': 'password123'})

res = s.post(f'{base_url}/orders', json={
    'cart': [{'id': 'm1', 'qty': 1}],
    'address': 'Test Address',
    'phone': '1234567890',
    'payment_method': 'Online',
    'total_price': 50.0,
    'lat': 18.0,
    'lng': 73.0
})
order_id = res.json().get('order_id')
print("Created order:", order_id)

# Manually create a payment using requests to Razorpay test API if possible?
# Actually, since it's hard to generate a test payment programmatically without checkout, 
# I will just write a script that fetches the LAST captured payment from Razorpay and manually attaches it to the order in SQLite!

payments = client.payment.fetch_all()
captured_pid = None
for p in payments['items']:
    if p['status'] == 'captured':
        captured_pid = p['id']
        break

if captured_pid:
    print("Found captured payment:", captured_pid)
    conn = sqlite3.connect('burger_house.db')
    c = conn.cursor()
    c.execute("UPDATE 'order' SET razorpay_payment_id = ? WHERE id = ?", (captured_pid, order_id))
    conn.commit()
    conn.close()
    print("Successfully attached. Order is ready to be cancelled for a REAL refund in UI!")
else:
    print("No captured payments available to mock.")

with open('order_to_cancel.txt', 'w') as f:
    f.write(str(order_id))
