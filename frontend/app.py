from flask import Flask, render_template, jsonify
import os
import requests

app = Flask(__name__)

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:5001")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:5002")
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:5003")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:5004")

def fetch_service(url, endpoint, timeout=2.0):
    try:
        res = requests.get(f"{url}{endpoint}", timeout=timeout)
        if res.status_code == 200:
            return {"status": "UP", "data": res.json()}
        return {"status": f"ERROR ({res.status_code})", "data": None}
    except Exception as e:
        return {"status": "DOWN", "error": str(e), "data": None}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"service": "frontend", "status": "healthy"}), 200

@app.route('/', methods=['GET'])
def index():
    users_info = fetch_service(USER_SERVICE_URL, "/api/users")
    products_info = fetch_service(PRODUCT_SERVICE_URL, "/api/products")
    orders_info = fetch_service(ORDER_SERVICE_URL, "/api/orders")
    notifications_info = fetch_service(NOTIFICATION_SERVICE_URL, "/api/notifications")

    services = [
        {"name": "User Service", "url": USER_SERVICE_URL, "status": users_info["status"], "port": "5001"},
        {"name": "Product Service", "url": PRODUCT_SERVICE_URL, "status": products_info["status"], "port": "5002"},
        {"name": "Order Service", "url": ORDER_SERVICE_URL, "status": orders_info["status"], "port": "5003"},
        {"name": "Notification Service", "url": NOTIFICATION_SERVICE_URL, "status": notifications_info["status"], "port": "5004"},
    ]

    return render_template(
        "index.html",
        services=services,
        users=users_info.get("data", {}).get("data", []) if users_info.get("data") else [],
        products=products_info.get("data", {}).get("data", []) if products_info.get("data") else [],
        orders=orders_info.get("data", {}).get("data", []) if orders_info.get("data") else [],
        notifications=notifications_info.get("data", {}).get("data", []) if notifications_info.get("data") else [],
        app_version=os.getenv("APP_VERSION", "1.0.0"),
        environment=os.getenv("APP_ENV", "production")
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
