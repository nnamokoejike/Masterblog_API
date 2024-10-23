import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable Cors for all routes

# POSTS = [
#     {"id": 1, "title": "First post", "content": "This is the first post."},
#     {"id": 2, "title": "Second post", "content": "This is the second post."}
# ]


# POSTS = [
#     {"id": 1, "title": "The Importance of Good Sleep",
#      "content": "Quality sleep is essential for maintaining physical and mental health."},
#     {"id": 2, "title": "How to Stay Productive While Working From Home",
#      "content": "Remote work can be challenging, but with the right habits, you can stay productive."},
#     {"id": 3, "title": "The Rise of Electric Vehicles",
#      "content": "Electric vehicles are becoming more popular as sustainable alternatives to traditional cars."},
#     {"id": 4, "title": "Benefits of a Plant-Based Diet",
#      "content": "Switching to a plant-based diet has numerous health benefits, including better digestion."},
#     {"id": 5, "title": "How to Create a Personal Budget",
#      "content": "A well-planned budget helps you manage your money effectively and save for the future."},
#     {"id": 6, "title": "Top 5 Destinations for Adventure Travel",
#      "content": "Explore some of the most exciting places in the world for adventure and thrill-seekers."},
#     {"id": 7, "title": "The Future of Artificial Intelligence",
#      "content": "AI is transforming industries, and its potential applications are virtually limitless."},
#     {"id": 8, "title": "Simple Ways to Reduce Stress",
#      "content": "Reducing stress is important for a balanced life; try meditation or exercise to ease tension."},
#     {"id": 9, "title": "The Ultimate Guide to Remote Collaboration Tools",
#      "content": "Remote teams can stay connected and efficient using tools like Slack and Zoom."},
#     {"id": 10, "title": "How to Improve Your Fitness Routine",
#      "content": "Small changes in your fitness routine can make a big difference in your overall health."}
# ]

POSTS = [
    {"id": 1, "title": "The Importance of Good Sleep",
     "content": "Quality sleep is essential for maintaining physical and mental health.", "author": "Alice Smith",
     "date": "2024-10-01"},
    {"id": 2, "title": "How to Stay Productive While Working From Home",
     "content": "Remote work can be challenging, but with the right habits, you can stay productive.",
     "author": "Bob Johnson", "date": "2024-10-02"},
    # Add more posts as needed...
]


# Helper function to generate the current date in the format "YYY-MM-DD"
def get_current_date():
    return datetime.datetime.now().strftime('%Y-%m-%d')


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


# "List" endpoint - Return the list of all posts, with optionL SORTING
@app.route('/api/posts', methods=['GET'])
def get_posts():
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
        sorted_posts = sorted(POSTS, key=lambda x: x[sort_by].lower(), reverse=reverse_order)
        return jsonify(sorted_posts)
    # If no sorting, return the original list
    return jsonify(POSTS)


# Search endpoint - Allows searching posts by title or content
@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    # Get the query parameters
    search_title = request.args.get('title')
    search_content = request.args.get('content')
    search_author = request.args.get('author')
    search_date = request.args.get('date')

    # Filter the posts based on the search parameters
    results = []
    for post in POSTS:
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

    # Generate a new unique ID
    new_id = max(post['id'] for post in POSTS) + 1 if POSTS else 1

    # Create a new post dictionary
    new_post = {
        'id': new_id,
        'title': data['title'],
        'content': data['content'],
        'author': data['author'],
        'date': get_current_date()   # Automatically set the current date
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


# Route to handle PUT requests to update a specific post
@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_post(id):
    # Find the post with the given ID
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

    return jsonify(POSTS)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
