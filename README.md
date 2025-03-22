# 📚 Library Management System

A **Python Flask-based Library Management System** with **MongoDB Atlas** integration. This project allows users to register, log in, and manage books efficiently, providing an interactive and user-friendly experience.

## 🚀 Features

- **User Authentication**: Secure user registration and login.
- **Book Management**: Add, update, delete, and view books.
- **MongoDB Atlas Integration**: Cloud-based database for efficient storage.
- **Interactive UI**: Built with Flask and HTML/CSS.
- **RESTful API Endpoints**: Enables easy interaction with the system.

## 🛠 Tech Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB Atlas
- **Frontend**: HTML, CSS, JavaScript
- **IDE**: VS Code

## 📂 Project Structure
```
Library-Management-System/
│-- static/             # CSS, JavaScript, images
│-- templates/          # HTML templates
│-- app.py              # Flask application
│-- config.py           # Configuration settings
│-- requirements.txt    # Dependencies
│-- README.md           # Project documentation
```

## 📊 Database Structure

### Tables and Fields

1. **Users**
   - `_id` (ObjectId, Primary Key)
   - `username` (String, Unique)
   - `password` (String, Hashed)
   - `email` (String, Unique)
   - `role` (String, Admin/User)

2. **Books**
   - `_id` (ObjectId, Primary Key)
   - `title` (String, Required)
   - `author` (String, Required)
   - `genre` (String)
   - `published_year` (Integer)
   - `status` (String, Available/Borrowed)

3. **Borrowed_Books**
   - `_id` (ObjectId, Primary Key)
   - `user_id` (ObjectId, Foreign Key to Users)
   - `book_id` (ObjectId, Foreign Key to Books)
   - `borrow_date` (Date)
   - `return_date` (Date)

## 🔗 API Endpoints

### User Authentication

| Endpoint      | Method | Description | Input | Output | Errors |
|--------------|--------|-------------|--------|--------|--------|
| `/register`  | POST   | Register a new user | `{username, email, password}` | `{message: 'User created'}` | `400: User exists` |
| `/login`     | POST   | User login | `{username, password}` | `{token}` | `401: Invalid credentials` |

### Book Management

| Endpoint      | Method | Description | Input | Output | Errors |
|--------------|--------|-------------|--------|--------|--------|
| `/books`     | GET    | View all books | None | `[ {book data} ]` | `500: Server error` |
| `/books/add` | POST   | Add a new book | `{title, author, genre}` | `{message: 'Book added'}` | `400: Missing fields` |
| `/books/<id>/edit` | PUT | Edit book details | `{title, author}` | `{message: 'Book updated'}` | `404: Book not found` |
| `/books/<id>/delete` | DELETE | Delete a book | None | `{message: 'Book deleted'}` | `404: Book not found` |

## 🎨 Frontend and Flow

1. **Login Page**: Users log in with credentials.
2. **Home Page**: Displays available books and options.
3. **Book Management**:
   - Add new books.
   - Edit or delete books.
   - Borrow/return books.
4. **User Profile**: Displays borrowed books and history.

## 🌐 Hosting Instructions

1. **Deploy on Heroku** (or any cloud service):
   - Install Heroku CLI.
   - Login via `heroku login`.
   - Create a new app: `heroku create my-library-app`.
   - Deploy: `git push heroku main`.
2. **Set Up MongoDB Atlas**:
   - Create a free cluster at [MongoDB Atlas](https://www.mongodb.com/atlas).
   - Add the connection string to `.env` file.
3. **Run Locally**:
   ```bash
   python app.py
   ```
   Access at `http://localhost:5000`.

## 🤝 Contributing
Contributions are welcome! Please fork this repository and submit a pull request.

## 📜 License
This project is licensed under the MIT License.

---

🚀 **Happy Coding!**

