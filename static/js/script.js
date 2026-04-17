let menuItems = [];
let cart = JSON.parse(localStorage.getItem('burger_cart')) || {};
let currentUser = null;

// Selectors
const menuGrid = document.getElementById('menu-grid');
const cartItemsContainer = document.getElementById('cart-items');
const totalPriceEl = document.getElementById('total-price');
const placeOrderBtn = document.getElementById('place-order-btn');
const deliveryForm = document.getElementById('delivery-form');
const formMessage = document.getElementById('form-message');

const loginBtn = document.getElementById('login-btn');
const loginForm = document.getElementById('login-form');
const signupForm = document.getElementById('signup-form');
const authTabs = document.querySelectorAll('.auth-tab');

const userProfile = document.getElementById('user-profile');
const userNameDisplay = document.getElementById('user-name-display');
const logoutBtn = document.getElementById('logout-btn');
const headerCartBtn = document.getElementById('header-cart-btn');

let currentTotal = 0;

// Save cart to disk
function saveCart() {
    localStorage.setItem('burger_cart', JSON.stringify(cart));
}

// API Calls
async function fetchMenu() {
    if (!menuGrid) return; // Only fetch if we are on the menu page
    try {
        const response = await fetch('/api/menu');
        menuItems = await response.json();
        renderMenu();
    } catch (err) {
        console.error("Failed to fetch menu:", err);
    }
}

async function checkAuth() {
    try {
        const response = await fetch('/api/auth/me');
        const data = await response.json();
        if (data.authenticated) {
            currentUser = data.user;
        } else {
            currentUser = null;
        }
        updateAuthUI();
    } catch (err) {
        console.error("Auth check failed:", err);
    }
}

// Menu Logic
function renderMenu() {
    if (!menuGrid) return;
    menuGrid.innerHTML = '';
    menuItems.forEach(item => {
        const div = document.createElement('div');
        div.className = 'menu-item';
        if (cart[item.id]) div.classList.add('selected');

        const imageSrc = item.image ? `/static/${item.image}` : null;
        const mediaHTML = item.image 
            ? `<img src="${imageSrc}" alt="${item.name}" class="menu-item-image">`
            : `<div class="menu-item-icon">${item.icon}</div>`;

        div.innerHTML = `
            ${mediaHTML}
            <h3 class="menu-item-name">${item.name}</h3>
            <p class="menu-item-desc">${item.desc}</p>
            <div class="menu-item-price">₹${item.price}</div>
        `;
        div.addEventListener('click', () => {
            addToCart(item);
        });
        menuGrid.appendChild(div);
    });
}

function addToCart(item) {
    if (cart[item.id]) {
        cart[item.id].qty += 1;
    } else {
        cart[item.id] = { ...item, qty: 1 };
    }
    updateCart();
    if (menuGrid) renderMenu(); // Re-render to show selection wrapper
}

function updateQty(id, delta) {
    if (cart[id]) {
        cart[id].qty += delta;
        if (cart[id].qty <= 0) {
            delete cart[id];
        }
        updateCart();
        if (menuGrid) renderMenu();
    }
}

function updateCart() {
    saveCart(); // Persist changes
    const cartArray = Object.values(cart);
    let total = 0;
    
    // Calculate Total
    cartArray.forEach(item => { total += item.price * item.qty; });
    currentTotal = total;
    
    // Update Header
    if (headerCartBtn) {
        headerCartBtn.textContent = `Cart: ₹${total}`;
    }

    // Update Checkout Page if active
    if (cartItemsContainer) {
        cartItemsContainer.innerHTML = '';
        if (cartArray.length === 0) {
            cartItemsContainer.innerHTML = '<p class="empty-cart">Your cart is empty.</p>';
            totalPriceEl.textContent = '₹0';
            placeOrderBtn.disabled = true;
            return;
        }

        cartArray.forEach(item => {
            const itemTotal = item.price * item.qty;
            const row = document.createElement('div');
            row.className = 'cart-item-row';
            row.innerHTML = `
                <div class="cart-item-info">
                    <div class="cart-item-title">${item.name}</div>
                    <div class="cart-item-qty">
                        <button type="button" class="qty-btn" onclick="updateQty('${item.id}', -1)">-</button>
                        <span>${item.qty}</span>
                        <button type="button" class="qty-btn" onclick="updateQty('${item.id}', 1)">+</button>
                    </div>
                </div>
                <div class="cart-item-subtotal">
                    ₹${itemTotal}
                </div>
            `;
            cartItemsContainer.appendChild(row);
        });

        totalPriceEl.textContent = '₹' + total;
        placeOrderBtn.disabled = false;
    }
}

// Delivery Form Submission
if (deliveryForm) {
    const paymentTabs = document.querySelectorAll('.payment-tab');
    const paymentPanels = document.querySelectorAll('.payment-panel');

    paymentTabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            // Remove active from all tabs and panels
            paymentTabs.forEach(t => t.classList.remove('active'));
            paymentPanels.forEach(p => p.classList.remove('active'));

            // Add active to clicked tab
            tab.classList.add('active');
            
            // Show corresponding panel
            const targetId = tab.getAttribute('data-target');
            document.getElementById(targetId).classList.add('active');
            
            // Check the hidden radio button
            const radio = tab.querySelector('input[type="radio"]');
            if(radio) radio.checked = true;
        });
    });

    deliveryForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!currentUser) {
            window.location.href = '/auth';
            return;
        }
        
        const cartArray = Object.values(cart);
        if(cartArray.length === 0) return;

        placeOrderBtn.textContent = 'Processing Payment...';
        placeOrderBtn.disabled = true;

        const fullName = document.getElementById('fullName').value; // Optional
        const selectedPayment = document.querySelector('input[name="payment_method"]:checked').value;

        const orderData = {
            cart: cartArray.map(i => ({ id: i.id, qty: i.qty })),
            address: document.getElementById('address').value,
            phone: document.getElementById('phone').value,
            payment_method: selectedPayment,
            total_price: currentTotal,
            lat: document.getElementById('lat') ? parseFloat(document.getElementById('lat').value) : null,
            lng: document.getElementById('lng') ? parseFloat(document.getElementById('lng').value) : null
        };

        try {
            const response = await fetch('/api/orders', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(orderData)
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                // If the backend generated a Razorpay Order ID, open gateway
                if (data.razorpay_order_id) {
                    var options = {
                        "key": "rzp_test_SdTuc0ah3PWYwr", // Same placeholder as backend
                        "amount": data.amount, 
                        "currency": "INR",
                        "name": "Burger House",
                        "description": "Food Delivery Transaction",
                        "image": "/static/images/burger_classic.png", // Assuming valid or broken fallback
                        "order_id": data.razorpay_order_id, 
                        "handler": async function (response) {
                            // On successful payment, verify with backend
                            const verifyRes = await fetch('/api/verify_payment', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({
                                    razorpay_payment_id: response.razorpay_payment_id,
                                    razorpay_order_id: response.razorpay_order_id,
                                    razorpay_signature: response.razorpay_signature,
                                    order_id: data.order_id
                                })
                            });
                            
                            const verifyData = await verifyRes.json();
                            if(verifyData.success) {
                                cart = {};
                                saveCart();
                                window.location.href = `/order/${data.order_id}`;
                            } else {
                                alert("Payment verification failed! Please contact support.");
                                placeOrderBtn.innerHTML = 'Place Order <span class="btn-glow"></span>';
                                placeOrderBtn.disabled = false;
                            }
                        },
                        "prefill": {
                            "name": fullName || "Customer",
                            "contact": document.getElementById('phone').value
                        },
                        "theme": {
                            "color": "#ff6b00"
                        }
                    };
                    var rzp1 = new Razorpay(options);
                    rzp1.on('payment.failed', function (response){
                        alert("Payment Failed: " + response.error.description);
                        placeOrderBtn.innerHTML = 'Place Order <span class="btn-glow"></span>';
                        placeOrderBtn.disabled = false;
                    });
                    rzp1.open();
                } else {
                    // COD or fallback
                    cart = {};
                    saveCart();
                    window.location.href = `/order/${data.order_id}`;
                }
            } else {
                throw new Error('Order creation failed');
            }
        } catch(err) {
            formMessage.className = 'form-message error-msg';
            formMessage.textContent = 'Failed to process payment/order. Please try again.';
            placeOrderBtn.innerHTML = 'Place Order <span class="btn-glow"></span>';
            placeOrderBtn.disabled = false;
        }

        setTimeout(() => { formMessage.textContent = ''; }, 5000);
    });
}

// --- Auth Handling ---
if (authTabs.length > 0) {
    authTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            authTabs.forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.auth-form').forEach(f => {
                f.style.display = 'none';
                f.classList.remove('active');
            });

            tab.classList.add('active');
            const targetFormId = tab.getAttribute('data-tab') + '-form';
            const targetForm = document.getElementById(targetFormId);
            targetForm.style.display = 'block';
            setTimeout(() => targetForm.classList.add('active'), 10);
        });
    });
}

if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        
        try {
            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email, password})
            });
            const data = await res.json();
            if (data.success) {
                window.location.href = '/'; // redirect home
            } else {
                alert(data.error || "Login Failed");
            }
        } catch(err) {
            console.error(err);
        }
    });

    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('signup-name').value;
        const email = document.getElementById('signup-email').value;
        const password = document.getElementById('signup-password').value;
        
        try {
            const res = await fetch('/api/auth/signup', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name, email, password})
            });
            const data = await res.json();
            if (data.success) {
                window.location.href = '/'; // redirect home
            } else {
                alert(data.error || "Signup Failed");
            }
        } catch(err) {
            console.error(err);
        }
    });
}

if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
        await fetch('/api/auth/logout', { method: 'POST' });
        window.location.reload(); // Refresh the page to clear identity
    });
}

function updateAuthUI() {
    if (currentUser) {
        if (loginBtn) loginBtn.style.display = 'none';
        if (userProfile) userProfile.style.display = 'flex';
        if (userNameDisplay) userNameDisplay.textContent = currentUser.name;
    } else {
        if (loginBtn) loginBtn.style.display = 'block';
        if (userProfile) userProfile.style.display = 'none';
        if (userNameDisplay) userNameDisplay.textContent = 'Guest';
    }
}

// Initial Flow
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    fetchMenu(); // Validates internally if menuGrid exists
    updateCart(); // Setups initial state
});

// Expose internal functions required for inline `onClick` html
window.updateQty = updateQty;
