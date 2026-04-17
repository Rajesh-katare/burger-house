<h1 align="center">🍔 Burger House</h1>

<p align="center">
  <strong>A Full-Stack, E-Commerce Food Delivery Web Application</strong>
</p>

## 📸 Overview

Burger House is a modern, responsive web application inspired by premium fast-food delivery services. It provides a complete end-to-end user experience, from browsing a dynamic menu to placing orders via Secure Online Payments or Cash on Delivery, and tracking the delivery in real-time.

Built as a showcase of robust full-stack engineering, beautiful UI/UX utilizing modern glassmorphism, and secure REST APIs.

## ✨ Features

- **Dynamic Interactive Menu:** Browse detailed items with smooth micro-animations.
- **Real-Time Order Tracking:** Integrated with Leaflet.js to securely track the delivery rider's live route on a map. Includes a chronological order state timeline (Pending ➝ Preparing ➝ Out for Delivery ➝ Delivered).
- **Secure Authentication:** User signup and login system utilizing secure hashed passwords (Werkzeug).
- **Online Payments Integration:** Built-in seamless integration with the Razorpay API to authorize and capture online transactions securely.
- **Instant Automated Refunds:** Canceling an online order executes a Server-to-Server API call to automatically refund the transaction to the original payment method in under 10 minutes.
- **Glassmorphic UI:** A visually stunning dark-mode aesthetic utilizing CSS back-drop filters and custom modal animations, optimized for mobile (Android/iOS) and desktop screens.
- **Admin Dashboard:** A protected route to allow store managers to view registered users and monitor all active orders.

## 🛠️ Tech Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy (SQLite)
- **Frontend:** HTML5, Vanilla Modern CSS, JavaScript (Fetch API)
- **Integrations:** Razorpay API (Payments & Refunds), Leaflet.js & Nominatim / OpenStreetMap (Geolocation & Routing)
- **Deployment:** Ready for deployment on Render.com with Gunicorn.

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.9+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/burger-house.git
   cd burger-house
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   For convenience in local testing, an `.env.example` file is included. Rename it to `.env` to load the mock database keys and Razorpay test credentials.
   ```bash
   cp .env.example .env
   ```

5. **Run the Application**
   ```bash
   python app.py
   ```
   The application will automatically build the SQLite database on launch. Visit `http://127.0.0.1:5000` in your browser.

## 🌐 Deploying to Render.com

This project is pre-configured for free deployment on Render.
1. Connect this GitHub repository to Render.
2. Build Command: `./build.sh`
3. Start Command: `gunicorn app:app`
4. *Note:* Using SQLite on Render's ephemeral free tier means the database will periodically automatically reset—acting as an excellent auto-cleaning instance for your portfolio!

---
*Created as a demonstration of modern full-stack web development principles.*
