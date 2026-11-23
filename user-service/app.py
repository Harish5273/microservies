from flask import Flask, jsonify
import os

app = Flask(__name__)

users = [
    {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "role": "Admin"},
    {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "role": "Developer"},
    {"id": 3, "name": "Charlie Brown", "email": "charlie@example.com", "role": "DevOps Engineer"}
]

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"service": "user-service", "status": "healthy"}), 200

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify({
        "service": "user-service",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "count": len(users),
        "data": users
    }), 200

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if user:
        return jsonify(user), 200
    return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
