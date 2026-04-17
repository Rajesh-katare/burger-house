from app import app, db, MenuItem

menu_items = [
    { "id": 'm1', "name": 'Original Whopper', "price": 149, "desc": 'Flame-grilled beef patty, fresh lettuce, tomatoes, mayo.', "image": 'assets/burger_classic.png', "icon": '🍔' },
    { "id": 'm2', "name": 'Double Bacon Cheese', "price": 199, "desc": 'Two beef patties, thick-cut bacon, melted cheddar.', "image": 'assets/burger_bacon.png', "icon": '🥓' },
    { "id": 'm3', "name": 'Crispy Chicken', "price": 169, "desc": 'Crunchy chicken fillet, spicy mayo, pickles.', "image": 'assets/burger_chicken.png', "icon": '🍗' },
    { "id": 'm4', "name": 'Vegan Burger', "price": 179, "desc": 'Plant-based patty, vegan cheese, fresh veggies.', "image": 'assets/burger_vegan.png', "icon": '🌱' },
    { "id": 'm5', "name": 'Tacos Plate', "price": 189, "desc": 'Trio of delicious hard and soft-shell meat tacos.', "image": 'assets/tacos.png', "icon": '🌮' },
    { "id": 'm6', "name": 'Hot Latte Coffee', "price": 99, "desc": 'Steaming cup of artisan latte with beautiful latte art.', "image": 'assets/coffee.png', "icon": '☕' },
    { "id": 'm7', "name": 'Large Fries', "price": 89, "desc": 'Golden, crispy, and perfectly salted in a basket.', "image": 'assets/fries.png', "icon": '🍟' },
    { "id": 'm10', "name": 'Vanilla Shake', "price": 129, "desc": 'Thick hand-spun vanilla milk-shake.', "image": None, "icon": '🍦' }
]

def seed_db():
    with app.app_context():
        db.create_all()
        # Clean current menu items just in case
        MenuItem.query.delete()
        
        for item in menu_items:
            mi = MenuItem(
                id=item['id'],
                name=item['name'],
                price=item['price'],
                desc=item['desc'],
                image=item['image'],
                icon=item['icon']
            )
            db.session.add(mi)
        
        db.session.commit()
        print("Database seeded with menu items successfully!")

if __name__ == '__main__':
    seed_db()
