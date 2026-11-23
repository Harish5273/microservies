from flask import Flask, jsonify
import os

app = Flask(__name__)

products = [
    {"id": 101, "name": "Cloud Architecture Handbook", "price": 49.99, "stock": 120},
    {"id": 102, "name": "Kubernetes in Production", "price": 39.50, "stock": 85},
    {"id": 103, "name": "Terraform Up & Running", "price": 34.00, "stock": 210},
    {"id": 104, "name": "ArgoCD GitOps Guide", "price": 29.99, "stock": 65}
]

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"service": "product-service", "status": "healthy"}), 200

@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify({
        "service": "product-service",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "count": len(products),
        "data": products
    }), 200

@app.route('/api/products/<int:prod_id>', methods=['GET'])
def get_product(prod_id):
    product = next((p for p in products if p["id"] == prod_id), None)
    if product:
        return jsonify(product), 200
    return jsonify({"error": "Product not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port)
