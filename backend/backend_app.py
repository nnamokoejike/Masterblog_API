import datetime
import json
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable Cors for all routes

POSTS_FILE = 'posts.json'


# Helper function to read posts from JSON file
def read_posts_from_file():
    if not os.path.exists(POSTS_FILE):
        return []
    try:
        with open(POSTS_FILE, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []  # Return empty list if JSON is invalid


# Helper function to write posts to JSON file
def write_posts_to_file(posts):
    with open(POSTS_FILE, 'w') as file:
        json.dump(posts, file, indent=4)


# Helper function to generate the current date in the format "YYY-MM-DD"
def get_current_date():
    return datetime.datetime.now().strftime('%Y-%m-%d')


def find_post_by_id(post_id):
    """
    Find the post with the id 'post_id'.
    If there is no post with this id, return None
    """
    posts = read_posts_from_file()
    for post in posts:
        if post["id"] == post_id:
            return post
    return None


def validate_post_data(data):
    if 'title' not in data or "content" not in data or 'author' not in data:
        return False
    return True


@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({"error": "Method Not Allowed"}), 405


# "List" endpoint - Return the list of all posts, with optionL SORTING
@app.route('/api/posts', methods=['GET'])
def get_posts():
    posts = read_posts_from_file()
    sort_by = request.args.get('sort')  # Get the sort query parameter
    direction = request.args.get('direction', 'asc')  # Get the direction query parameter (default is asc)

    # Validate sort field
    if sort_by and sort_by not in ['title', 'content', 'author', 'date']:
        return jsonify({"Error": "Invalid sort field. Must be 'title' or 'content' or 'author' or 'date'"}), 400

    # Validate sort direction
    if direction not in ['asc', 'desc']:
        return jsonify({"Error": "Invalid sort direction. Must be 'asc' or 'desc'"}), 400

    # If sorting is requested
    if sort_by:
        reverse_order = True if direction == 'desc' else False
        sorted_posts = sorted(posts, key=lambda x: x[sort_by].lower(), reverse=reverse_order)
        return jsonify(sorted_posts)
    # If no sorting, return the original list
    return jsonify(posts)


# Search endpoint - Allows searching posts by title or content
@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    # Get the query parameters
    search_title = request.args.get('title')
    search_content = request.args.get('content')
    search_author = request.args.get('author')
    search_date = request.args.get('date')

    posts = read_posts_from_file()
    # Filter the posts based on the search parameters
    results = []
    for post in posts:
        if (search_title and search_title.lower() in post['title'].lower()) or \
                (search_content and search_content.lower() in post['content'].lower()) or \
                (search_author and search_author.lower() in post['author'].lower()) or \
                (search_date and search_date == post['date']):
            results.append(post)

    # Return the filtered list of posts
    return jsonify(results)


@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()

    # Check if 'title' and 'content' are provided
    if not validate_post_data(data):
        return jsonify({"Error": "Invalid post data, 'title' and 'author' are required"}), 400

    posts = read_posts_from_file()

    # Generate a new unique ID
    new_id = max(post['id'] for post in posts) + 1 if posts else 1

    # Create a new post dictionary
    new_post = {
        'id': new_id,
        'title': data['title'],
        'content': data['content'],
        'author': data['author'],
        'date': get_current_date()  # Automatically set the current date
    }

    # Add the new post to the list
    posts.append(new_post)
    write_posts_to_file(posts)

    # Return the newly created post with status 201 (Created)
    return jsonify(new_post), 201


# Route to handle DELETE requests for a specific post
@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    # Find the post by ID
    posts = read_posts_from_file()
    post = find_post_by_id(id)

    # If the post wasn't found, return a 404 error
    if post is None:
        return jsonify({"Error": f"Post with id {id} not found."}), 404

    # Remove the post from the list
    posts.remove(post)
    write_posts_to_file(posts)

    # Return the deleted post
    return jsonify({"Message": f"Post with id {id} has been deleted successfully."}), 200


# Route to handle PUT requests to update a specific post
@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_post(id):
    # Find the post with the given ID
    posts = read_posts_from_file()
    post = find_post_by_id(id)

    # If the book wasn't found, return a 404 error
    if post is None:
        return jsonify(
            {"Error": f"Post with id {id} is not found in the data base. Please provide a valid post id"}), 404

    new_data = request.get_json()

    if 'title' in new_data:
        post['title'] = new_data['title']
    if 'content' in new_data:
        post['content'] = new_data['content']
    if 'author' in new_data:
        post['author'] = new_data['author']
    if 'date' in new_data:
        post['date'] = new_data['date']

    # Write the updated list back to the file
    for i, p in enumerate(posts):
        if p['id'] == id:
            posts[i] = post
            break
    write_posts_to_file(posts)
    return jsonify(posts)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
