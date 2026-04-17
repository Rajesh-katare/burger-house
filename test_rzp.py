import razorpay

RAZORPAY_KEY_ID = 'rzp_test_SdTuc0ah3PWYwr'
RAZORPAY_KEY_SECRET = 'emm75eBQZesbjDibdq2fhI99'
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Fetch latest payments to find one that is authorized
payments = client.payment.fetch_all()
for p in payments['items']:
    print(f"Payment ID: {p['id']}, Status: {p['status']}, Amount: {p['amount']}")
    if p['status'] == 'authorized':
        print("Found authorized payment:", p['id'])
        try:
            # Try to refund it directly
            client.payment.refund(p['id'], {'amount': p['amount']})
            print("Refund succeeded on authorized payment!")
        except Exception as e:
            print("Refund failed on authorized payment:", e)
            print("Attempting to capture first...")
            try:
                client.payment.capture(p['id'], p['amount'])
                print("Capture succeeded. Now refunding...")
                client.payment.refund(p['id'], {'amount': p['amount']})
                print("Refund completely succeeded on captured payment!")
            except Exception as e2:
                print("Capture/Refund pipeline failed:", e2)
        break
    elif p['status'] == 'captured':
        print("Found captured payment:", p['id'])
        try:
            client.payment.refund(p['id'], {'amount': p['amount']})
            print("Refund completely succeeded on captured payment!")
        except Exception as e3:
            print("Refund failed on captured payment:", e3)
        break
