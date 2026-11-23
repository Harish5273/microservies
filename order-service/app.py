from flask import Flask, jsonify, request
import os

app = Flask(__name__)

orders = [
    {"order_id": "ORD-501", "user_id": 1, "product_id": 102, "quantity": 1, "total": 39.50, "status": "CONFIRMED"},
    {"order_id": "ORD-502", "user_id": 2, "product_id": 101, "quantity": 2, "total": 99.98, "status": "SHIPPED"},
    {"order_id": "ORD-503", "user_id": 3, "product_id": 104, "quantity": 1, "total": 29.99, "status": "DELIVERED"}
]

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"service": "order-service", "status": "healthy"}), 200

@app.route('/api/orders', methods=['GET'])
def get_orders():
    return jsonify({
        "service": "order-service",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "count": len(orders),
        "data": orders
    }), 200

@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    order = next((o for o in orders if o["order_id"] == order_id), None)
    if order:
        return jsonify(order), 200
    return jsonify({"error": "Order not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port)
