from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Configure SQLite database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'posts.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure file upload directory
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(300), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_post', methods=['POST'])
def add_post():
    title = request.form.get('title')
    content = request.form.get('content')
    file = request.files.get('file')
    file_path = None
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        file_path = f"uploads/{filename}"  # Store relative path

    new_post = Post(title=title, content=content, file_path=file_path)
    db.session.add(new_post)
    db.session.commit()
    
    return jsonify({"message": "Post added successfully!"})

@app.route('/get_posts', methods=['GET'])
def get_posts():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    posts_list = [
        {
            "id": post.id, 
            "title": post.title, 
            "content": post.content, 
            "file_path": post.file_path, 
            "timestamp": post.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for post in posts
    ]
    return jsonify(posts_list)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
