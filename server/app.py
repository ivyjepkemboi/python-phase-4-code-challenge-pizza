#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

# Define API resources

class RestaurantsResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict() for restaurant in restaurants], 200

class RestaurantByIdResource(Resource):
    def get(self, id):
        restaurant = db.session.get(Restaurant, id)
        if restaurant:
            return restaurant.to_dict(rules=('restaurant_pizzas', 'restaurant_pizzas.pizza')), 200
        return {"error": "Restaurant not found"}, 404

    
    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return {}, 204
        return {"error": "Restaurant not found"}, 404

class PizzasResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [pizza.to_dict() for pizza in pizzas], 200

class RestaurantPizzasResource(Resource):
    def post(self):
        data = request.get_json()
        
        try:
            new_restaurant_pizza = RestaurantPizza(
                price=data['price'],
                pizza_id=data['pizza_id'],
                restaurant_id=data['restaurant_id']
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            return new_restaurant_pizza.to_dict(rules=('pizza', 'restaurant')), 201
        except ValueError:
            return {"errors": ["validation errors"]}, 400
        except Exception as e:
            return {"errors": [str(e)]}, 400


# Add Resources to API
api.add_resource(RestaurantsResource, '/restaurants')
api.add_resource(RestaurantByIdResource, '/restaurants/<int:id>')
api.add_resource(PizzasResource, '/pizzas')
api.add_resource(RestaurantPizzasResource, '/restaurant_pizzas')

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

if __name__ == "__main__":
    app.run(port=5555, debug=True)
