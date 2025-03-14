from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pymongo import MongoClient
import os
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
CORS(app)  # Allow CORS for all origins

# JWT Configuration
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a strong secret key in production
TOKEN_EXPIRATION = 24  # hours

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.InCarbo

# Collections
BuyerInitial_collection = db.BuyerInitial
SellerInitial_collection = db.SellerInitial
Buyer_collection = db.Buyer
Seller_collection = db.Seller
Projects_collection = db.projects

# JWT token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Decode the token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['username']
            user_type = data['user_type']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except:
            return jsonify({'error': 'Token is invalid'}), 401
            
        return f(current_user, user_type, *args, **kwargs)
    
    return decorated

@app.before_request
def handle_options_request():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

@app.route('/')
def serve_index():
    file_path = os.path.abspath('index.html')
    if os.path.exists(file_path):
        return send_file(file_path)
    return jsonify({"error": "index.html not found"}), 404

@app.route('/login.html')
@app.route('/login', endpoint='login_page')
def serve_login():
    file_path = os.path.abspath('login.html')
    if os.path.exists(file_path):
        return send_file(file_path)
    return jsonify({"error": "login.html not found"}), 404

@app.route('/add-buyer', methods=['POST'])
def add_buyer():
    try:
        data = request.get_json()
        required_fields = ["project_name", "technology", "country", "vintages", "integrity_status", "amount_for_sale", "price_per_ton", "registry", "trace_id"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"'{field}' is required"}), 400
        BuyerInitial_collection.insert_one(data)
        return jsonify({"message": "Buyer added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/add-seller', methods=['POST'])
def add_seller():
    try:
        data = request.get_json(force=True)
        data['projects'] = []  # Ensure projects field is initialized as an empty array
        SellerInitial_collection.insert_one(data)
        return jsonify({"message": "Seller added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/buyers', methods=['GET'])
def get_buyers():
    try:
        buyers = list(BuyerInitial_collection.find({}, {"_id": 0}))
        return jsonify(buyers), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sellers', methods=['GET'])
def get_sellers():
    try:
        sellers = list(SellerInitial_collection.find({}, {"_id": 0}))
        return jsonify(sellers), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        user_type = data.get('type')
        email = data.get('email')
        password = data.get('password')
        username = data.get('username')

        if not user_type or not email or not password or not username:
            return jsonify({"error": "Email, password, username, and user type are required"}), 400

        collection = Buyer_collection if user_type == "buyer" else Seller_collection

        query = {
            "email": email,
            "password": password,
            "username": username
        }
        user = collection.find_one(query)

        if user:
            # Generate JWT token
            token = jwt.encode({
                'username': username,
                'user_type': user_type,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRATION)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            
            redirect_page = "BuyerDashboard.html" if user_type == "buyer" else "SellerDashboard.html"
            return jsonify({
                "message": "Login successful",
                "redirect": redirect_page,
                "token": token
            }), 200

        return jsonify({"error": "Invalid credentials - User not found"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/BuyerDashboard.html')
def serve_buyer_dashboard():
    file_path = os.path.abspath('BuyerDashboard.html')
    if os.path.exists(file_path):
        return send_file(file_path)
    return jsonify({"error": "BuyerDashboard.html not found"}), 404

@app.route('/SellerDashboard.html')
def serve_seller_dashboard():
    file_path = os.path.abspath('SellerDashboard.html')
    if os.path.exists(file_path):
        return send_file(file_path)
    return jsonify({"error": "SellerDashboard.html not found"}), 404

@app.route('/add-project', methods=['POST'])
@token_required
def add_project(current_user, user_type):
    try:
        # Check if the user is a seller
        if user_type != "seller":
            return jsonify({"error": "Only sellers can add projects"}), 403
            
        data = request.json
        print("Incoming Data:", data)  # Debug log to inspect incoming payload
        
        # Restructure received data to match expected format
        project_data = {
            "project_name": data.get("project_name"),
            "technology": data.get("technology"),
            "country": data.get("country"),
            "vintages": data.get("vintages"),
            "integrity_status": data.get("integrity_status"),
            "amount_for_sale": {
                "current": data.get("amount_for_sale")
            },
            "price_per_ton": data.get("price_per_ton"),
            "registry": {
                "name": data.get("registry_name"),
                "id": data.get("trace_id")
            },
            "trace_id": data.get("trace_id")
        }

        print("Processed project data:", project_data)

        # Append the new project to the project array for the specific user
        update_result = Seller_collection.update_one(
            {"username": current_user},
            {"$push": {"project": project_data}}
        )

        if update_result.modified_count == 0:
            return jsonify({"error": "User not found or project not added"}), 404

        return jsonify({"message": "Project added successfully"}), 201

    except Exception as e:
        print("Error:", str(e))  # Debug log to catch errors
        return jsonify({"error": str(e)}), 500

@app.route('/get-projects', methods=['GET'])
@token_required
def get_projects(current_user, user_type):
    try:
        # Check if the user is a seller
        if user_type != "seller":
            return jsonify({"error": "Only sellers can view their projects"}), 403

        seller = Seller_collection.find_one({"username": current_user}, {"_id": 0, "project": 1})
        if not seller:
            return jsonify({"error": "Seller not found"}), 404

        # Return the projects array or an empty array if not found
        return jsonify(seller.get("project", [])), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test-db', methods=['GET'])
def test_db():
    try:
        result = list(BuyerInitial_collection.find({}, {"_id": 0}))
        return jsonify({"message": "Connected to MongoDB", "buyers": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)