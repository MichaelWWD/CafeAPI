from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
import random

app = Flask(__name__)

#  Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        # Loops through each column in the data record
        for column in self.__table__.columns:
            # Creates a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route('/cafes')
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    all_cafes = [cafe.to_dict() for cafe in cafes]
    return jsonify(cafes=all_cafes)


@app.route('/cafe/<cafe_id>', methods=["GET"])
def get_a_cafe(cafe_id):
    cafe_to_view = Cafe.query.get(cafe_id)
    if cafe_to_view:
        return jsonify(cafe=cafe_to_view.to_dict()), 200
    else:
        return jsonify(error={"message": "Sorry a cafe with that id was not found "}), 404


@app.route('/random')
def get_random_cafe():
    all_cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(all_cafes)
    return jsonify(cafe=random_cafe.to_dict())


@app.route('/search')
def find_cafe_by_location():
    all_locations = [loc.location for loc in db.session.query(Cafe).all()]
    query_location = request.args.get("loc")
    if query_location in all_locations:
        cafes_at_query_location = Cafe.query.filter_by(location=query_location).all()
        if len(cafes_at_query_location) > 1:
            all_cafes = [cafe.to_dict() for cafe in cafes_at_query_location]
            return jsonify(cafes=all_cafes)
        else:
            return jsonify(cafe=cafes_at_query_location[0].to_dict()), 200
    else:
        return jsonify(error={"message": "Sorry we don't have a cafe at that location"}), 404


# HTTP POST - Create Record
@app.route('/add', methods=["POST"])
def add_cafe():
    new_cafe = Cafe(
        name=request.form["name"],
        map_url=request.form["map_url"],
        img_url=request.form["img_url"],
        location=request.form["location"],
        seats=request.form["seats"],
        has_toilet=int(request.form["has_toilet"]),
        has_wifi=int(request.form["has_wifi"]),
        has_sockets=int(request.form["has_sockets"]),
        can_take_calls=int(request.form["can_take_calls"]),
        coffee_price=request.form["coffee_price"],
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"message": "Successfully added new cafe "}), 201


# HTTP PUT/PATCH - Update Record
@app.route('/update-price/<cafe_id>', methods=["PATCH"])
def update_coffee_price(cafe_id):
    cafe_to_update = Cafe.query.get(cafe_id)
    if cafe_to_update:
        new_price = request.args.get("new_price")
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify({"message": "Successfully updated the price."}), 200
    else:
        return jsonify(error={"message": "Sorry a cafe with that id was not found "}), 404


# HTTP DELETE - Delete Record
@app.route('/report-closed/<cafe_id>', methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api_key")
    cafe_to_delete = Cafe.query.get(cafe_id)
    if api_key == "TopSecretAPIKey":
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify({"message": "Successfully deleted cafe."}), 200
        else:
            return jsonify(error={"message": "Sorry a cafe with that id was not found "}), 404
    else:
        return jsonify(error={"message": "Sorry, that's not allowed. Make sure you have the correct api_key"}), 403


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
