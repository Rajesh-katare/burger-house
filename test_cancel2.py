import requests

base_url = 'http://127.0.0.1:5000/api'
s = requests.Session()

# 1. Signup/Login
res = s.post(f'{base_url}/auth/login', json={
    'email': 'test@example.com',
    'password': 'password123'
})
print("Login status:", res.json())

# 2. Add an order and directly inject a fake payment id in the DB
# (Normally Razorpay gives a real one, but we'll try a fake one to trigger the error)
# Actually, wait, test keys are fine! If we provide a fake `razorpay_payment_id` that Razorpay doesn't know about, the refund endpoint will throw an exception!

# We can mimic it by placing an order, then making a sqlite call to update it
order_data = {
    'cart': [{'id': 'm1', 'qty': 1}],
    'address': 'Test Address',
    'phone': '1234567890',
    'payment_method': 'Online',
    'total_price': 10.0,
    'lat': 18.0,
    'lng': 73.0
}
res = s.post(f'{base_url}/orders', json=order_data)
order_id = res.json().get('order_id')
print("Order placed:", order_id)

import sqlite3
conn = sqlite3.connect('burger_house.db')
c = conn.cursor()
c.execute("UPDATE 'order' SET razorpay_payment_id = 'pay_fake_12345' WHERE id = ?", (order_id,))
conn.commit()
conn.close()

# 3. Try to cancel
res = s.post(f'{base_url}/order/{order_id}/cancel')
print("Cancel status:", res.status_code, res.text)
