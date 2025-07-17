
📖 Epicor PO Management – AI-Enhanced Procurement System
About the Project
The Epicor PO Management – AI-Enhanced Procurement System is a full-stack web application designed to demonstrate core Enterprise Resource Planning (ERP) functionalities, specifically Purchase Order (PO) management, enhanced with modern Artificial Intelligence capabilities. This project simulates how businesses, particularly in manufacturing and distribution, can streamline their procurement processes and gain predictive insights into demand.

Built with a focus on practical application and modern cloud technologies, it showcases robust data handling, intuitive user experience, and intelligent forecasting to address common operational challenges like inefficient manual processes, suboptimal inventory, and underutilized operational data.

🚀 Features
✅ Purchase Order (PO) Lifecycle Management: Create, view, update (approve/unapprove status), and delete purchase orders through a web interface.

✅ AI-Powered Demand Forecasting: Integrates with the Google Gemini API to generate demand forecasts for specific items based on simulated historical sales data.

✅ User Isolation: Data is stored and retrieved based on a unique user ID, simulating multi-tenancy or user-specific data segregation.

✅ Cloud-Based Data Storage: Utilizes Google Firestore for persistent and scalable data management.

✅ Responsive User Interface: Frontend built with HTML, CSS (Tailwind CSS), and JavaScript for a modern, mobile-friendly design.

✅ Custom Modals: Provides user feedback through non-intrusive modal messages.



🛠️ Tech Stack
Backend:

Python

Flask (Web Framework)

Firebase Admin SDK (for Firestore interaction)

Google Generative AI (for Gemini API)

NumPy (for simulated data generation)

Gunicorn (Production WSGI HTTP Server, for deployment)

Database:

Google Firestore (NoSQL Cloud Database)

Frontend:

HTML5

CSS3

JavaScript

Tailwind CSS (Utility-First CSS Framework)



🔧 Setup Instructions
This project consists of a Python Flask backend that serves the HTML frontend.

1. Clone the repository
git clone https://github.com/your-username/PO_management.git
cd po_management

2. Set up Python Virtual Environment and Install Dependencies
It's highly recommended to use a virtual environment to manage dependencies.

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows (Git Bash/MinGW64):
source .venv/Scripts/activate
# On macOS/Linux:
# source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

3. Configure Firebase and Gemini API Credentials
You need a Firebase project set up with Firestore enabled and a Google Gemini API key.

Firebase Service Account Key:

Download your Firebase service account JSON key file from your Firebase project settings (Project settings > Service accounts > Generate new private key).

Save this file (e.g., firebase_service_account.json) in your project's root directory.

Environment Variables:

Create a .env file in your project's root directory.

Add your API keys and configuration here for local development:

# .env
FIREBASE_SERVICE_ACCOUNT_PATH=firebase_service_account.json
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
FLASK_SECRET_KEY=YOUR_LONG_RANDOM_SECRET_KEY # Generate a strong, random string
APP_ID=demo-app

Replace YOUR_GEMINI_API_KEY and YOUR_LONG_RANDOM_SECRET_KEY with your actual keys.

4. Run the Flask Application
# Ensure your virtual environment is activated
# On Windows (Git Bash/MinGW64):
source .venv/Scripts/activate
# On macOS/Linux:
# source .venv/bin/activate

# Run the Flask app
python app.py

The application will typically run on http://127.0.0.1:5000. Open this URL in your web browser.