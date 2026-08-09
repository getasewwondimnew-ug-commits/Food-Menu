from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime

app = Flask(__name__)


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

    if not items:
        return jsonify({
            "error": "Order must contain at least one item"
        }), 400

    order = {
        "id": datetime.now().timestamp(),
        "items": items,
        "created_at": datetime.now().isoformat()
    }

    orders = []

    if os.path.exists("orders.json"):
        try:
            with open("orders.json", "r") as file:
                orders = json.load(file)

        except json.JSONDecodeError:
            orders = []

    orders.append(order)

    with open("orders.json", "w") as file:
        json.dump(orders, file, indent=4)

    return jsonify({
        "message": "Order placed successfully",
        "order": order
    }), 201


if __name__ == "__main__":
    app.run(debug=True)