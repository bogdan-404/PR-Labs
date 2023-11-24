from flask import Flask, request, jsonify
from models import db, ElectroScooter
from RaftNode import RaftNode
import os

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"sqlite:///database_{os.getenv('NODE_ID', 'node_1')}.db"
db.init_app(app)

node_id = os.getenv("NODE_ID", "node_1")
peers = os.getenv("PEERS", "localhost:5001,localhost:5002").split(",")

raft_node = RaftNode(node_id, peers)


def init_db():
    with app.app_context():
        db.create_all()


@app.route("/api/electro-scooters/", methods=["POST"])
def create_electro_scooter():
    if raft_node.state != "leader":
        return jsonify({"error": "Not the leader"}), 403
    data = request.get_json()
    new_scooter = ElectroScooter(name=data["name"], battery_level=data["battery_level"])
    db.session.add(new_scooter)
    db.session.commit()
    raft_node.forward_request_to_followers("/api/electro-scooters/", data)
    return jsonify(new_scooter.id), 201


@app.route("/api/electro-scooters/<int:scooter_id>", methods=["GET"])
def get_electro_scooter(scooter_id):
    scooter = ElectroScooter.query.get(scooter_id)
    if scooter:
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
    return jsonify({"error": "Scooter not found"}), 404


@app.route("/api/electro-scooters/<int:scooter_id>", methods=["PUT"])
def update_electro_scooter(scooter_id):
    if raft_node.state != "leader":
        return jsonify({"error": "Not the leader"}), 403
    scooter = ElectroScooter.query.get(scooter_id)
    if not scooter:
        return jsonify({"error": "Scooter not found"}), 404
    data = request.get_json()
    scooter.name = data.get("name", scooter.name)
    scooter.battery_level = data.get("battery_level", scooter.battery_level)
    db.session.commit()
    raft_node.forward_request_to_followers(f"/api/electro-scooters/{scooter_id}", data)
    return jsonify({"message": "Updated"}), 200


@app.route("/api/electro-scooters/<int:scooter_id>", methods=["DELETE"])
def delete_electro_scooter(scooter_id):
    if raft_node.state != "leader":
        return jsonify({"error": "Not the leader"}), 403
    scooter = ElectroScooter.query.get(scooter_id)
    if not scooter:
        return jsonify({"error": "Scooter not found"}), 404
    db.session.delete(scooter)
    db.session.commit()
    raft_node.forward_request_to_followers(f"/api/electro-scooters/{scooter_id}", {})
    return jsonify({"message": "Deleted"}), 200


# if __name__ == "__main__":
#     db.create_all()
#     port = int(os.getenv("PORT", 5000))
#     app.run(port=port, debug=True)

if __name__ == "__main__":
    init_db()
    app.run(port=int(os.getenv("PORT", 5000)), debug=True)
