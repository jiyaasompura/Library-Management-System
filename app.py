# Import necessary libraries and modules

from flask import Flask, render_template, request, url_for, redirect, jsonify, make_response
import jwt
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure MongoDB
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

# Configure JWT authentication
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

# ----------------------------- Authentication Routes -----------------------------

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles user login for both librarian and member."""
    if request.method == "GET":
        return render_template("login.html")
    
    email = request.form.get("email")
    password = request.form.get("password")
    selected_role = request.form.get("role")
    user = mongo.db.users.find_one({"email": email})

    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid email or password"}), 401
    
    if user["role"] != selected_role:
        return jsonify({"error": "Incorrect role selected!"}), 403
    
    access_token = create_access_token(identity={"email": email, "role": user["role"]})
    
    if user["role"] == "librarian":
        return redirect(url_for("librarian_home"))
    elif user["role"] == "member":
        return redirect(url_for("member_home"))
    
    return jsonify({"token": access_token})

@app.route("/register", methods=["GET", "POST"])
def register():
    """Registers a new user as a librarian or member."""
    if request.method == "GET":
        return render_template("register.html")
    
    email = request.form.get("email")
    password = request.form.get("password")
    role = request.form.get("role")
    hashed_password = generate_password_hash(password)
    
    user_data = {"email": email, "password": hashed_password, "role": role}
    mongo.db.users.insert_one(user_data)
    return redirect(url_for("login"))

@app.route("/logout", methods=["GET"])
def logout():
    """Logs out the user and redirects to login page."""
    return redirect(url_for("login"))

# ----------------------------- Dashboard Routes -----------------------------

@app.route("/librarian_home", methods=["GET"])
def librarian_home():
    """Renders the librarian dashboard."""
    return render_template("librarian_home.html")

@app.route("/member_home")
def member_home():
    """Renders the member dashboard."""
    return render_template("member_home.html")

# ----------------------------- Book Management Routes -----------------------------

@app.route("/add_book", methods=["POST"])
def add_book():
    """Allows librarian to add a new book to the collection."""
    data = request.get_json()
    if not all(key in data for key in ["title", "author", "year", "book_id"]):
        return jsonify({"error": "All fields are required!"}), 400
    
    data["status"] = "AVAILABLE"
    mongo.db.books.insert_one(data)
    return jsonify({"success": True, "message": "Book added successfully!"}), 201

@app.route("/view_books", methods=["GET"])
def view_books():
    """Displays all books in the collection."""
    books = list(mongo.db.books.find({}, {"_id": 0}))
    return jsonify(books), 200

@app.route("/remove_book", methods=["POST"])
def remove_book():
    """Allows librarian to remove a book from the collection."""
    data = request.get_json()
    result = mongo.db.books.delete_one({"book_id": data.get("book_id")})
    return jsonify({"success": True, "message": "Book removed successfully!"}) if result.deleted_count > 0 else jsonify({"error": "Book not found!"}), 404

# ----------------------------- Member Management Routes -----------------------------

@app.route("/view_members", methods=["GET"])
def view_members():
    members = list(mongo.db.users.find({"role": "member"}, {"_id": 0, "password": 0}))  # Exclude `_id` & passwords
    return jsonify(members), 200

@app.route("/remove_member", methods=["POST"])
def remove_member():
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({"error": "Member email is required!"}), 400
    result = mongo.db.users.delete_one({"email": email, "role": "member"})  # Ensure the user is a member
    if result.deleted_count > 0:
        return jsonify({"success": True, "message": "Member removed successfully!"}), 200
    else:
        return jsonify({"error": "Member not found!"}), 404
    
@app.route("/add_member", methods=["POST"])
def add_member():
    data = request.get_json()
    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")
    if not full_name or not email or not password:
        return jsonify({"error": "All fields are required!"}), 400
    # Check if the user already exists
    existing_user = mongo.db.users.find_one({"email": email})
    if existing_user:
        return jsonify({"error": "Email already registered!"}), 409
    hashed_password = generate_password_hash(password)  # Encrypt the password before storing
    member = {
        "full_name": full_name,
        "email": email,
        "password": hashed_password,  # Store hashed password
        "role": "member"  # Default role as member
    }
    mongo.db.users.insert_one(member)
    return jsonify({"success": True, "message": "Member added successfully!"}), 201

@app.route("/delete_account", methods=["POST"])
def delete_account():
    """Allows a member to delete their own account."""
    data = request.get_json()
    result = mongo.db.users.delete_one({"email": data.get("email"), "role": "member"})
    return jsonify({"success": True, "message": "Your account has been deleted successfully!"}) if result.deleted_count > 0 else jsonify({"error": "Member account not found!"}), 404

# ----------------------------- Borrow & Return Book Routes -----------------------------

@app.route("/borrow_book", methods=["POST"])
def borrow_book():
    """Allows a member to borrow a book."""
    data = request.get_json()
    book = mongo.db.books.find_one({"book_id": data.get("book_id"), "status": "AVAILABLE"})
    
    if not book:
        return jsonify({"error": "Book is not available or does not exist!"}), 404
    
    mongo.db.books.update_one({"book_id": data.get("book_id")}, {"$set": {"status": "BORROWED", "borrowed_by": data.get("email")}})
    return jsonify({"success": True, "message": f"Book '{book['title']}' borrowed successfully!"}), 200

@app.route("/return_book", methods=["POST"])
def return_book():
    """Allows a member to return a borrowed book."""
    data = request.get_json()
    book = mongo.db.books.find_one({"book_id": data.get("book_id"), "status": "BORROWED", "borrowed_by": data.get("email")})
    
    if not book:
        return jsonify({"error": "Book is not borrowed by this member or does not exist!"}), 404
    
    mongo.db.books.update_one({"book_id": data.get("book_id")}, {"$set": {"status": "AVAILABLE"}, "$unset": {"borrowed_by": ""}})
    return jsonify({"success": True, "message": f"Book '{book['title']}' returned successfully!"}), 200

if __name__ == "__main__":
    app.run(debug=True)
