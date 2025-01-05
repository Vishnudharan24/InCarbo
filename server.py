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
login_collection = db.login  # Add login collection

# Route for serving index.html
@app.route('/')
def serve_index():
    # Dynamically find index.html file in the same directory
    file_path = os.path.join(os.path.dirname(__file__), 'index.html')
    if os.path.exists(file_path):
        return send_file(file_path)
    return jsonify({"error": "index.html not found"}), 404

# Route for serving login.html
@app.route('/login.html')
@app.route('/login', endpoint='login_page')
def serve_login():
    file_path = os.path.join(os.path.dirname(__file__), 'login.html')
    if os.path.exists(file_path):
        return send_file(file_path)
    return jsonify({"error": "login.html not found"}), 404

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

# Add login route
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        print("Received login data:", data)  # Debug print

        user_type = data.get('type')
        email = data.get('email')
        password = data.get('password')
        

        print(f"Attempting login - Email: {email}, Type: {user_type}")  # Debug print

        # Validate inputs
        if not user_type or not email or not password:
            return jsonify({"error": "Email, password and user type are required"}), 400

        # Debug print the query
        query = {
            "type": user_type,
            "email": email,
            "password": password,
            
        }
        print("Database query:", query)

        # Check if user exists in the database
        user = login_collection.find_one(query)
        print("Database result:", user)  # Debug print

        if user:
            # Modify redirect based on user type
            redirect_page = "BuyerDashboard.html" if user['type'] == "buyer" else "SellerDashboard.html"
            return jsonify({
                "message": "Login successful",
                "redirect": redirect_page
            }), 200
            
        return jsonify({"error": "Invalid credentials - User not found"}), 401

    except Exception as e:
        print("Login error:", str(e))  # Debug print
        return jsonify({"error": str(e)}), 500

# Add routes for dashboard pages
@app.route('/BuyerDashboard.html')
def serve_buyer_dashboard():
    file_path = os.path.join(os.path.dirname(__file__), 'BuyerDashboard.html')
    if os.path.exists(file_path):
        return send_file(file_path)
    return jsonify({"error": "BuyerDashboard.html not found"}), 404

@app.route('/SellerDashboard.html')
def serve_seller_dashboard():
    file_path = os.path.join(os.path.dirname(__file__), 'SellerDashboard.html')
    if os.path.exists(file_path):
        return send_file(file_path)
    return jsonify({"error": "SellerDashboard.html not found"}), 404

# Add routes for additional pages
@app.route('/portfolio.html')
def serve_portfolio():
    file_path = os.path.join(os.path.dirname(__file__), 'portfolio.html')
    if os.path.exists(file_path):
        return send_file(file_path)
    return jsonify({"error": "portfolio.html not found"}), 404

@app.route('/projects.html')
def serve_projects():
    file_path = os.path.join(os.path.dirname(__file__), 'projects.html')
    if os.path.exists(file_path):
        return send_file(file_path)
    return jsonify({"error": "projects.html not found"}), 404

@app.route('/TraceIDVerification.html')
def serve_trace_verification():
    file_path = os.path.join(os.path.dirname(__file__), 'TraceIDVerification.html')
    if os.path.exists(file_path):
        return send_file(file_path)
    return jsonify({"error": "TraceIDVerification.html not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
