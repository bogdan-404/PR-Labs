from flask import Flask, request, jsonify
from models import db, ElectroScooter
from RaftNode import RaftNode
import os
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
node_id = os.getenv("NODE_ID", "node_1")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///database_{node_id}.db"
db.init_app(app)

lock_file_path = "raft_leader.lock"
raft_node = RaftNode(node_id, lock_file_path)


@app.route("/api/electro-scooters/", methods=["POST"])
def create_electro_scooter():
    if raft_node.state != "leader":
        return jsonify({"error": "Not the leader"}), 403

    data = request.get_json()
    new_scooter = ElectroScooter(name=data["name"], battery_level=data["battery_level"])
    db.session.add(new_scooter)
    db.session.commit()
    return jsonify({"id": new_scooter.id}), 201


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
        return (
            jsonify(
                {
                    "error": "It is a follower. Only leader has privileges to the request."
                }
            ),
            403,
        )
    scooter = ElectroScooter.query.get(scooter_id)
    if not scooter:
        return jsonify({"error": "Scooter not found"}), 404
    db.session.delete(scooter)
    db.session.commit()
    raft_node.forward_request_to_followers(f"/api/electro-scooters/{scooter_id}", {})
    return jsonify({"message": "Deleted"}), 200


def init_db():
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    init_db()
    app.run(port=int(os.getenv("PORT", 5000)), debug=True)
