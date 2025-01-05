from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pymongo import MongoClient
import os

app = Flask(__name__)
# Configure CORS to allow all origins
CORS(app)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB URI
db = client.InCarbo  # Corrected the database name to 'InCarbo'

# Collections
BuyerInitial_collection = db.BuyerInitial  # Corrected the collection name to 'BuyerInitial'
SellerInitial_collection = db.SellerInitial  # Corrected the collection name to 'SellerInitial'

# Route for serving index.html
@app.route('/')
def serve_index():
    # Dynamically find index.html file in the same directory
    file_path = os.path.join(os.path.dirname(__file__), 'index.html')
    if os.path.exists(file_path):
        return send_file(file_path)
    return jsonify({"error": "index.html not found"}), 404

# Route to Add Buyer
@app.route('/add-buyer', methods=['POST'])
def add_buyer():
    try:
        data = request.json
        BuyerInitial_collection.insert_one(data)  # Insert into 'BuyerInitial' collection
        return jsonify({"message": "Buyer added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to Add Seller
@app.route('/add-seller', methods=['POST'])
def add_seller():
    try:
        data = request.json
        SellerInitial_collection.insert_one(data)  # Insert into 'SellerInitial' collection
        return jsonify({"message": "Seller added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to Fetch Buyers
@app.route('/buyers', methods=['GET'])
def get_buyers():
    try:
        buyers = list(BuyerInitial_collection.find({}, {"_id": 0}))  # Fetch all from 'BuyerInitial'
        return jsonify(buyers), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to Fetch Sellers
@app.route('/sellers', methods=['GET'])
def get_sellers():
    try:
        sellers = list(SellerInitial_collection.find({}, {"_id": 0}))  # Fetch all from 'SellerInitial'
        return jsonify(sellers), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
