from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
import os
import time
import random

app = Flask(__name__)

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 定义 Blog 表
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content
        }
    
def random_string(length):
    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ''.join(random.choice(letters) for i in range(length))

@app.route('/init')
def init():
    start = time.time()
    db.drop_all()
    db.create_all()
    end = time.time()
    return 'Database initialized! Time taken: ' + str(end - start)

@app.route('/get-all-env')
def get_all_env():
    return jsonify(dict(os.environ))

# 首页：展示所有博客并提供新增博客表单
@app.route('/')
def home():
    start = time.time()
    blogs = Blog.query.order_by(Blog.id.desc()).all()
    blogs_html = "".join(
        f"<a href='/blogs/{blog.id}'>{blog.title}</a><br>{blog.content}<br><br>" for blog in blogs
    )
    end = time.time()
    form_html = '''
        <form action="/blogs" method="post">
            <label for="title">Title:</label><br>
            <input type="text" id="title" name="title" required><br>
            <label for="content">Content:</label><br>
            <textarea id="content" name="content" required></textarea><br>
            <button type="submit">Create</button>
        </form>
        <hr>
    '''

    t_html = f'<p>Time taken: {end - start:.6f} seconds</p>'

    return render_template_string(form_html + blogs_html + t_html)

@app.route('/insert_random')
def insert_random():
    times = request.args.get('times', 10)
    start = time.time()
    for i in range(int(times)):
        new_blog = Blog(title=random_string(10), content=random_string(100))
        db.session.add(new_blog)
    db.session.commit()
    end = time.time()
    return 'Inserted ' + str(times) + ' random blogs! Time taken: ' + str(end - start)

# 创建博客
@app.route('/blogs', methods=['POST'])
def create_blog():
    start = time.time()
    title = request.form.get('title')
    content = request.form.get('content')

    if not title or not content:
        return jsonify({'error': 'Title and content are required!'}), 400

    new_blog = Blog(title=title, content=content)
    db.session.add(new_blog)
    db.session.commit()
    end = time.time()
    return jsonify({'message': 'Blog created successfully!', 'blog': new_blog.to_dict(), 'time_taken': end - start}), 201

# 获取所有博客
@app.route('/blogs', methods=['GET'])
def get_all_blogs():
    start = time.time()
    blogs = Blog.query.all()
    end = time.time()
    return jsonify({'blogs': [blog.to_dict() for blog in blogs], 'time_taken': end - start}), 200

# 获取单个博客
@app.route('/blogs/<int:blog_id>', methods=['GET'])
def get_blog(blog_id):
    start = time.time()
    blog = Blog.query.get(blog_id)
    if not blog:
        return jsonify({'error': 'Blog not found!'}), 404
    end = time.time()
    return "<a href='/'>Back</a><br><br>" + f"<h1>{blog.title}</h1><p>{blog.content}</p><p>Time taken: {end - start:.6f} seconds</p>"

# 更新博客
@app.route('/blogs/<int:blog_id>', methods=['PUT'])
def update_blog(blog_id):
    start = time.time()
    blog = Blog.query.get(blog_id)
    if not blog:
        return jsonify({'error': 'Blog not found!'}), 404

    data = request.json
    blog.title = data.get('title', blog.title)
    blog.content = data.get('content', blog.content)

    db.session.commit()
    end = time.time()
    return jsonify({'message': 'Blog updated successfully!', 'blog': blog.to_dict(), 'time_taken': end - start}), 200

# 删除博客
@app.route('/blogs/<int:blog_id>', methods=['DELETE'])
def delete_blog(blog_id):
    start = time.time()
    blog = Blog.query.get(blog_id)
    if not blog:
        return jsonify({'error': 'Blog not found!'}), 404

    db.session.delete(blog)
    db.session.commit()
    end = time.time()
    return jsonify({'message': 'Blog deleted successfully!', 'time_taken': end - start}), 200

if __name__ == '__main__':
    app.run(debug=True)
