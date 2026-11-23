from flask import Flask, jsonify
import os
import datetime

app = Flask(__name__)

notifications = [
    {"id": "NTF-1", "user_id": 1, "type": "EMAIL", "message": "Order ORD-501 has been confirmed.", "timestamp": "2026-11-23T10:00:00Z"},
    {"id": "NTF-2", "user_id": 2, "type": "SMS", "message": "Tracking info updated for order ORD-502.", "timestamp": "2026-11-23T11:15:00Z"},
    {"id": "NTF-3", "user_id": 3, "type": "SLACK", "message": "Deployment v1.0.0 successfully rolled out to EKS via ArgoCD.", "timestamp": "2026-11-23T12:00:00Z"}
]

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"service": "notification-service", "status": "healthy"}), 200

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    return jsonify({
        "service": "notification-service",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "count": len(notifications),
        "data": notifications
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5004))
    app.run(host='0.0.0.0', port=port)
