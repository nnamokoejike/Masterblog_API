from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable Cors for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."}
]


def find_post_by_id(post_id):
    """
    Find the post with the id 'post_id'.
    If there is no post with this id, return None
    """
    for post in POSTS:
        if post["id"] == post_id:
            return post
    return None


def validate_post_data(data):
    if 'title' not in data or "content" not in data:
        return False
    return True


@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({"error": "Method Not Allowed"}), 405


@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(POSTS)


@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()

    # Check if 'title' and 'content' are provided
    if not validate_post_data(data):
        return jsonify({"Error": "Invalid post data, 'title' and 'author' are required"}), 400

    # Generate a new unique ID
    new_id = max(post['id'] for post in POSTS) + 1 if POSTS else 1

    # Create a new post dictionary
    new_post = {
        'id': new_id,
        'title': data['title'],
        'content': data['content']
    }

    # Add the new post to the list
    POSTS.append(new_post)

    # Return the newly created post with status 201 (Created)
    return jsonify(new_post), 201


# Route to handle DELETE requests for a specific post
@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    # Find the post by ID
    post = find_post_by_id(id)

    # If the post wasn't found, return a 404 error
    if post is None:
        return jsonify({"Error": f"Post with id {id} not found."}), 404

    # Remove the post from the list
    POSTS.remove(post)

    # Return the deleted post
    return jsonify({"Message": f"Post with id {id} has been deleted successfully."}), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
