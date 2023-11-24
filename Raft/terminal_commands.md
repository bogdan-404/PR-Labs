First service:

```
$env:NODE_ID = "node_1"
$env:PEERS = "localhost:5001,localhost:5002"
$env:PORT = "5000"
python app.py
```

Second service:

```
$env:NODE_ID = "node_2"
$env:PEERS = "localhost:5000,localhost:5002"
$env:PORT = "5001"
python app.py
```

Third service:

```
$env:NODE_ID = "node_3"
$env:PEERS = "localhost:5000,localhost:5001"
$env:PORT = "5002"
python app.py
```

Postman POST Request on Port 5000(if leader): http://localhost:5000/api/electro-scooters/

```
{
  "name": "New Scooter",
  "battery_level": 75.5
}
```
