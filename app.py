
# app.py
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os
import uuid
import google.generativeai as genai
import datetime
import numpy as np
# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app) # Enable CORS for all routes (important for local development if frontend is separate)
app.secret_key = os.urandom(24) # Secret key for session management

# --- Firebase Initialization ---
# Path to your Firebase service account key
FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")

if not FIREBASE_SERVICE_ACCOUNT_PATH or not os.path.exists(FIREBASE_SERVICE_ACCOUNT_PATH):
    print(f"Error: Firebase service account key not found at {FIREBASE_SERVICE_ACCOUNT_PATH}")
    print("Please ensure 'firebase_service_account.json' is in the root directory and .env is configured.")
    exit(1)

try:
    cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase initialized successfully!")
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    exit(1)

# --- Gemini API Initialization ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found in .env file.")
    exit(1)
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.0-flash') # Using gemini-2.0-flash as requested
print("Gemini API initialized successfully!")

# --- Helper Functions ---
def get_user_id():
    """
    Retrieves user ID from session or generates a new one.
    For demonstration, we allow setting it via a form.
    In a real app, this would be handled by proper authentication.
    """
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4()) # Generate a unique ID if not present
    return session['user_id']

def get_user_po_collection_ref(user_id):
    """Returns the Firestore collection reference for the user's purchase orders."""
    # Using 'artifacts/{appId}/users/{userId}/purchaseOrders' structure as per previous instructions
    # For a standalone app, 'appId' can be a fixed string or derived from config.
    # We'll use a fixed 'epicor-demo-app' for this example.
    app_id_for_firestore = "epicor-demo-app"
    return db.collection(f'artifacts/{app_id_for_firestore}/users/{user_id}/purchaseOrders')

def generate_simulated_sales_data(item_name):
    """
    Generates simulated historical sales data for a given item.
    This simulates 12 months of data with some randomness and seasonality.
    """
    data = []
    today = datetime.date.today()
    for i in range(12): # 12 months of data
        date = datetime.date(today.year, today.month, 1) - datetime.timedelta(days=30 * i)
        month_year = date.strftime("%b %Y")
        # Simulate some seasonality and randomness
        base_sales = 50 + int(np.random.rand() * 50) # Base sales 50-100
        if i < 3: base_sales += 30 # Higher sales in recent months
        if i > 8: base_sales -= 20 # Lower sales in older months
        data.append({"month": month_year, "sales": base_sales})
    return list(reversed(data)) # Sort from oldest to newest

# --- Flask Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    """Renders the main application page."""
    current_user_id = get_user_id()
    if request.method == 'POST':
        # This handles the form submission for setting the user ID
        new_user_id = request.form.get('user_id_input')
        if new_user_id:
            session['user_id'] = new_user_id
            return redirect(url_for('index')) # Redirect to refresh with new user ID
    return render_template('index.html', user_id=current_user_id)

@app.route('/add_po', methods=['POST'])
def add_po():
    """Adds a new Purchase Order to Firestore."""
    user_id = get_user_id()
    data = request.json
    vendor_name = data.get('vendorName')
    item_name = data.get('itemName')
    quantity = data.get('quantity')
    unit_price = data.get('unitPrice')

    if not all([vendor_name, item_name, quantity, unit_price]):
        return jsonify({"success": False, "message": "Missing required fields."}), 400

    try:
        quantity = int(quantity)
        unit_price = float(unit_price)
        total_price = quantity * unit_price

        po_data = {
            "vendorName": vendor_name,
            "itemName": item_name,
            "quantity": quantity,
            "unitPrice": unit_price,
            "totalPrice": total_price,
            "status": "Pending",
            "createdAt": firestore.SERVER_TIMESTAMP,
            "createdBy": user_id
        }
        get_user_po_collection_ref(user_id).add(po_data)
        return jsonify({"success": True, "message": "Purchase Order added successfully!"})
    except ValueError:
        return jsonify({"success": False, "message": "Invalid quantity or unit price."}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error adding PO: {e}"}), 500

@app.route('/get_pos', methods=['GET'])
def get_pos():
    """Fetches all Purchase Orders for the current user from Firestore."""
    user_id = get_user_id()
    try:
        pos_ref = get_user_po_collection_ref(user_id)
        # Fetch documents and sort them in Python as orderBy in Firestore requires indexes
        docs = pos_ref.stream()
        purchase_orders = []
        for doc in docs:
            po_data = doc.to_dict()
            po_data['id'] = doc.id
            # Convert Firestore Timestamp to string for JSON serialization
            if 'createdAt' in po_data and po_data['createdAt']:
                po_data['createdAt'] = po_data['createdAt'].isoformat()
            if 'updatedAt' in po_data and po_data['updatedAt']:
                po_data['updatedAt'] = po_data['updatedAt'].isoformat()
            purchase_orders.append(po_data)

        # Sort by createdAt timestamp in descending order (newest first)
        purchase_orders.sort(key=lambda x: x.get('createdAt', ''), reverse=True)

        return jsonify({"success": True, "purchaseOrders": purchase_orders})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error fetching POs: {e}"}), 500

@app.route('/update_po_status', methods=['POST'])
def update_po_status():
    """Updates the status of a Purchase Order."""
    user_id = get_user_id()
    data = request.json
    po_id = data.get('poId')
    current_status = data.get('currentStatus')

    if not po_id or not current_status:
        return jsonify({"success": False, "message": "Missing PO ID or current status."}), 400

    new_status = "Approved" if current_status == "Pending" else "Pending"
    try:
        po_ref = get_user_po_collection_ref(user_id).document(po_id)
        po_ref.update({"status": new_status, "updatedAt": firestore.SERVER_TIMESTAMP})
        return jsonify({"success": True, "message": f"PO status updated to {new_status}!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error updating PO status: {e}"}), 500

@app.route('/delete_po', methods=['POST'])
def delete_po():
    """Deletes a Purchase Order."""
    user_id = get_user_id()
    data = request.json
    po_id = data.get('poId')

    if not po_id:
        return jsonify({"success": False, "message": "Missing PO ID."}), 400

    try:
        po_ref = get_user_po_collection_ref(user_id).document(po_id)
        po_ref.delete()
        return jsonify({"success": True, "message": "Purchase Order deleted successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error deleting PO: {e}"}), 500

@app.route('/forecast_demand', methods=['POST'])
def forecast_demand():
    """
    Receives an item name, generates simulated historical data,
    and uses Gemini API to get a demand forecast.
    """
    data = request.json
    item_name = data.get('itemName')

    if not item_name:
        return jsonify({"success": False, "message": "Missing item name for forecast."}), 400

    try:
        simulated_data = generate_simulated_sales_data(item_name)
        data_string = "\n".join([f"{d['month']}: {d['sales']} units" for d in simulated_data])

        prompt = f"""Based on the following historical sales data for "{item_name}", please provide a concise demand forecast for the next 3 months. Only provide the forecast, no additional text, just the forecast lines.
        Historical Sales Data:
        {data_string}

        Forecast for {item_name} (Next 3 Months):"""

        response = gemini_model.generate_content(prompt)
        forecast_text = response.text

        return jsonify({"success": True, "forecast": forecast_text})
    except Exception as e:
        print(f"Error during forecasting: {e}")
        return jsonify({"success": False, "message": f"Error generating forecast: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) # Run Flask app on port 5000