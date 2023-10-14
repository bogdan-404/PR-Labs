from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models.database import db
from flask import request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///your_database.db"
db.init_app(app)


class ElectroScooter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    battery_level = db.Column(db.Float, nullable=False)

    def __init__(self, name, battery_level):
        self.name = name
        self.battery_level = battery_level


@app.route("/api/electro-scooters/", methods=["POST"])
def create_electro_scooter():
    try:
        data = request.get_json()
        name = data["name"]
        battery_level = data["battery_level"]
        electro_scooter = ElectroScooter(name=name, battery_level=battery_level)
        db.session.add(electro_scooter)
        db.session.commit()
        return jsonify({"message": "Electro Scooter created successfully"}), 201
    except KeyError:
        return jsonify({"error": "Invalid request data"}), 400


@app.route("/api/electro-scooters/<int:scooter_id>", methods=["GET"])
def get_electro_scooter_by_id(scooter_id):
    scooter = ElectroScooter.query.get(scooter_id)
    if scooter is not None:
        return (
            jsonify(
                {
                    "id": scooter.id,
                    "name": scooter.name,
                    "battery_level": scooter.battery_level,
                }
            ),
            200,
        )
    else:
        return jsonify({"error": "Electro Scooter not found"}), 404


@app.route("/api/electro-scooters/<int:scooter_id>", methods=["PUT"])
def update_electro_scooter(scooter_id):
    try:
        scooter = ElectroScooter.query.get(scooter_id)
        if scooter is not None:
            data = request.get_json()
            scooter.name = data.get("name", scooter.name)
            scooter.battery_level = data.get("battery_level", scooter.battery_level)
            db.session.commit()
            return jsonify({"message": "Electro Scooter updated successfully"}), 200
        else:
            return jsonify({"error": "Electro Scooter not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/electro-scooters/<int:scooter_id>", methods=["DELETE"])
def delete_electro_scooter(scooter_id):
    try:
        scooter = ElectroScooter.query.get(scooter_id)
        if scooter is not None:
            password = request.headers.get("X-Delete-Password")
            if password == "1111":
                db.session.delete(scooter)
                db.session.commit()
                return jsonify({"message": "Electro Scooter deleted successfully"}), 200
            else:
                return jsonify({"error": "Incorrect password"}), 401
        else:
            return jsonify({"error": "Electro Scooter not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    blueprint = get_swaggerui_blueprint(
        "/documentation",
        "/static/swagger.json",
        config={"app_name": "Swagger Demo Presentation"},
    )
    app.register_blueprint(blueprint, url_prefix="/documentation")
    app.run()
