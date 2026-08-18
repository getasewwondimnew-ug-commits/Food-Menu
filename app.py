from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(255), nullable=False)
    items = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'items': self.items,
            'quantity': self.quantity,
            'total_price': self.total_price,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/cart.html")
def cart():
    return render_template("cart.html")


@app.route("/api/menu")
def get_menu():
    return jsonify([
        {
            "id": "bruschetta",
            "name": "Classic Bruschetta",
            "desc": "Toasted sourdough topped with vine tomatoes, fresh basil, and a drizzle of extra-virgin olive oil.",
            "price": 8.5,
            "img": "img/image1.png",
            "category": "starters"
        },
        {
            "id": "mushroom-soup",
            "name": "Cream of Mushroom Soup",
            "desc": "Rich, velvety mushroom soup with a swirl of cream and fresh thyme garnish.",
            "price": 7.0,
            "img": "img/image2.png",
            "category": "starters"
        },
        {
            "id": "shrimp-cocktail",
            "name": "Shrimp Cocktail",
            "desc": "Chilled jumbo shrimp served with house-made cocktail sauce and lemon wedges.",
            "price": 13.0,
            "img": "img/image3.png",
            "category": "starters"
        },
        {
            "id": "ribeye-steak",
            "name": "Grilled Ribeye Steak",
            "desc": "12 oz prime ribeye, seasoned and flame-grilled, served with roasted potatoes and seasonal vegetables.",
            "price": 38.0,
            "img": "img/image4.png",
            "category": "main-course"
        },
        {
            "id": "pan-seared-salmon",
            "name": "Pan-Seared Salmon",
            "desc": "Atlantic salmon fillet with lemon-dill butter sauce, served over wild rice and steamed asparagus.",
            "price": 29.0,
            "img": "img/image5.png",
            "category": "main-course"
        },
        {
            "id": "truffle-pasta",
            "name": "Truffle Pasta",
            "desc": "House-made tagliatelle tossed in a black truffle cream sauce with parmesan and fresh parsley.",
            "price": 24.0,
            "img": "img/image5.png",
            "category": "main-course"
        },
        {
            "id": "roast-chicken",
            "name": "Herb Roast Chicken",
            "desc": "Half chicken slow-roasted with rosemary, garlic, and lemon, served with mashed potatoes and gravy.",
            "price": 22.0,
            "img": "img/image6.png",
            "category": "desserts"
        },
        {
            "id": "lava-cake",
            "name": "Chocolate Lava Cake",
            "desc": "Warm dark chocolate fondant with a molten centre, served with vanilla bean ice cream.",
            "price": 11.0,
            "img": "img/image7.png",
            "category": "desserts"
        },
        {
            "id": "creme-brulee",
            "name": "Crème Brûlée",
            "desc": "Classic French custard with a crisp caramelised sugar crust, topped with fresh berries.",
            "price": 10.0,
            "img": "img/image8.png",
            "category": "desserts"
        },
        {
            "id": "cheesecake",
            "name": "New York Cheesecake",
            "desc": "Dense and creamy cheesecake on a buttery graham cracker base with a fresh strawberry compote.",
            "price": 9.5,
            "img": "img/image9.png",
            "category": "desserts"
        }
    ])


@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No order data received"
        }), 400

    items = data.get("items", [])
    customer_name = data.get("customer_name", "Guest")
    
    if not items:
        return jsonify({
            "error": "Order must contain at least one item"
        }), 400

    total_quantity = sum(item.get("qty", item.get("quantity", 1)) for item in items)
    total_price = sum(item.get("price", 0) * item.get("qty", item.get("quantity", 1)) for item in items)
    
    import json
    items_json = json.dumps(items)
    order = Order(
        customer_name=customer_name,
        items=items_json,
        quantity=total_quantity,
        total_price=total_price,
        status='pending'
    )
    
    db.session.add(order)
    db.session.commit()

    return jsonify({
        "message": "Order placed successfully",
        "order": order.to_dict()
    }), 201


@app.route("/api/order/<int:order_id>")
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify({
        "order": order.to_dict()
    })


# Admin Routes
@app.route("/admin/orders")
def admin_orders():
    """Display all orders with options to cancel or delete"""
    orders = Order.query.all()
    return render_template("admin_orders.html", orders=orders)


@app.route("/admin/add", methods=["GET", "POST"])
def admin_add():
    if request.method == "POST":
        customer_name = request.form.get("customer_name", "").strip()
        
        if not customer_name:
            return render_template("admin_add.html", error="Customer name is required"), 400
        
        items = []
        total_price = 0
        total_quantity = 0
        menu = get_menu_data()
        
        for item in menu:
            qty = request.form.get(f"qty_{item['id']}")
            if qty and int(qty) > 0:
                qty = int(qty)
                items.append({
                    "id": item["id"],
                    "name": item["name"],
                    "price": item["price"],
                    "quantity": qty
                })
                total_price += item["price"] * qty
                total_quantity += qty
        
        if not items:
            return render_template("admin_add.html", menu=menu, error="Please select at least one item"), 400
        
        import json
        order = Order(
            customer_name=customer_name,
            items=json.dumps(items),
            quantity=total_quantity,
            total_price=total_price,
            status='pending'
        )
        
        db.session.add(order)
        db.session.commit()
        
        return redirect(url_for("admin_orders"))
    
    menu = get_menu_data()
    return render_template("admin_add.html", menu=menu)


@app.route("/admin/order/<int:order_id>/status", methods=["POST"])
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    status = request.form.get("status", "pending")
    
    if status in ['pending', 'confirmed', 'completed', 'cancelled']:
        order.status = status
        db.session.commit()
    
    return redirect(url_for("admin_orders"))


@app.route("/admin/order/<int:order_id>/cancel", methods=["POST"])
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = 'cancelled'
    db.session.commit()
    
    return redirect(url_for("admin_orders"))


@app.route("/admin/order/<int:order_id>/delete", methods=["POST"])
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    
    return redirect(url_for("admin_orders"))


def get_menu_data():
    return [
        {
            "id": "bruschetta",
            "name": "Classic Bruschetta",
            "desc": "Toasted sourdough topped with vine tomatoes, fresh basil, and a drizzle of extra-virgin olive oil.",
            "price": 8.5,
            "category": "starters"
        },
        {
            "id": "mushroom-soup",
            "name": "Cream of Mushroom Soup",
            "desc": "Rich, velvety mushroom soup with a swirl of cream and fresh thyme garnish.",
            "price": 7.0,
            "category": "starters"
        },
        {
            "id": "shrimp-cocktail",
            "name": "Shrimp Cocktail",
            "desc": "Chilled jumbo shrimp served with house-made cocktail sauce and lemon wedges.",
            "price": 13.0,
            "category": "starters"
        },
        {
            "id": "ribeye-steak",
            "name": "Grilled Ribeye Steak",
            "desc": "12 oz prime ribeye, seasoned and flame-grilled, served with roasted potatoes and seasonal vegetables.",
            "price": 38.0,
            "category": "main-course"
        },
        {
            "id": "pan-seared-salmon",
            "name": "Pan-Seared Salmon",
            "desc": "Atlantic salmon fillet with lemon-dill butter sauce, served over wild rice and steamed asparagus.",
            "price": 29.0,
            "category": "main-course"
        },
        {
            "id": "truffle-pasta",
            "name": "Truffle Pasta",
            "desc": "House-made tagliatelle tossed in a black truffle cream sauce with parmesan and fresh parsley.",
            "price": 24.0,
            "category": "main-course"
        },
        {
            "id": "roast-chicken",
            "name": "Herb Roast Chicken",
            "desc": "Half chicken slow-roasted with rosemary, garlic, and lemon, served with mashed potatoes and gravy.",
            "price": 22.0,
            "category": "desserts"
        },
        {
            "id": "lava-cake",
            "name": "Chocolate Lava Cake",
            "desc": "Warm dark chocolate fondant with a molten centre, served with vanilla bean ice cream.",
            "price": 11.0,
            "category": "desserts"
        },
        {
            "id": "creme-brulee",
            "name": "Crème Brûlée",
            "desc": "Classic French custard with a crisp caramelised sugar crust, topped with fresh berries.",
            "price": 10.0,
            "category": "desserts"
        },
        {
            "id": "cheesecake",
            "name": "New York Cheesecake",
            "desc": "Dense and creamy cheesecake on a buttery graham cracker base with a fresh strawberry compote.",
            "price": 9.5,
            "category": "desserts"
        }
    ]


if __name__ == "__main__":
    app.run(debug=True)