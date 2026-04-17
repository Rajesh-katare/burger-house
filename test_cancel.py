import requests

base_url = 'http://127.0.0.1:5000/api'
s = requests.Session()

# 1. Signup/Login
res = s.post(f'{base_url}/auth/signup', json={
    'name': 'Test User',
    'email': 'test@example.com',
    'password': 'password123'
})
if res.status_code == 400:
    res = s.post(f'{base_url}/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })

print("Login status:", res.json())

# 2. Place Order
order_data = {
    'cart': [{'id': 'm1', 'qty': 1}],
    'address': 'Test Address',
    'phone': '1234567890',
    'payment_method': 'COD',
    'total_price': 10.0,
    'lat': 18.0,
    'lng': 73.0
}
res = s.post(f'{base_url}/orders', json=order_data)
print("Order status:", res.json())
order_id = res.json().get('order_id')

if order_id:
    # 3. Cancel Order
    res = s.post(f'{base_url}/order/{order_id}/cancel')
    print("Cancel status:", res.status_code, res.text)
