from flask import Flask, request, jsonify
import psycopg2
from config import DB_CONFIG

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

@app.route("/posts", methods=["GET"])
def get_posts():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, content, votes FROM posts ORDER BY created_at DESC;")
    posts = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"id": p[0], "title": p[1], "content": p[2], "votes": p[3]} for p in posts])

@app.route("/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, title, content, votes, created_at FROM posts WHERE id = %s;",
        (post_id,)
    )
    post = cur.fetchone()
    cur.close()
    conn.close()

    if post is None:
        return jsonify({"error": "Post not found"}), 404

    return jsonify({"id": post[0], "title": post[1], "content": post[2], "votes": post[3], "created_at": post[4].isoformat()})


@app.route("/posts", methods=["POST"])
def create_post():
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")

    if not title or not content:
        return jsonify({"error": "Title and content are required"}), 500

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("INSERT INTO posts (title, content) VALUES (%s, %s) RETURNING id, created_at;", (title, content))
    new_post = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "id": new_post[0],
        "title": title,
        "content": content,
        "votes": 0,
        "created_at": new_post[1].isoformat()
    }), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
