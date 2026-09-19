import json
import os
import re
from datetime import datetime
from typing import Optional

def load_orders() -> dict:
    orders_path = os.path.join(os.path.dirname(__file__), "..", "data", "orders.json")
    with open(orders_path, "r", encoding="utf-8") as f:
        return json.load(f)

def lookup_order(order_id: str) -> dict:
    """
    Looks up the current status of an order.
    Returns safe, summarized information about the order.
    """
    if not order_id:
        return {"error": "Order ID is missing. Please ask the customer for their Order ID."}

    # Normalize order ID
    order_id = order_id.strip().upper()
    # Strip any punctuation around it just in case
    order_id = re.sub(r'^[^\w]+|[^\w]+$', '', order_id)

    data = load_orders()
    orders = data.get("orders", [])
    snapshot_at = data.get("snapshot_at")

    order = next((o for o in orders if o["order_id"] == order_id), None)
    
    if not order:
        return {"error": f"Order {order_id} was not found. Please check the order ID or contact support."}
    
    status = order.get("status")
    
    # Base safe response
    safe_response = {
        "order_id": order.get("order_id"),
        "status": status,
        "items": [{"name": i.get("name"), "quantity": i.get("quantity"), "final_sale": i.get("final_sale")} for i in order.get("items", [])],
        "carrier": order.get("carrier"),
    }
    
    if status in ["cancelled", "returned"]:
        safe_response["message"] = f"The order is {status}. It will not be shipped."
        # Never give a stale estimated delivery if cancelled/returned
        safe_response["estimated_delivery"] = None
    elif status == "shipped":
        if order.get("estimated_delivery"):
            safe_response["estimated_delivery"] = order.get("estimated_delivery")
            safe_response["message"] = f"Order has shipped via {order.get('carrier')}. Estimated delivery: {order.get('estimated_delivery')}."
        else:
            safe_response["message"] = f"Order has shipped via {order.get('carrier')}, but a delivery estimate is unavailable."
    elif status == "exception":
        safe_response["message"] = "Support review is required for this order. Please recommend a human handoff."
    else:
        safe_response["message"] = order.get("customer_safe_message")

    # Important Privacy filter: Never expose customer info, internal notes, etc.
    # safe_response is already explicitly constructed to omit internal/customer fields.
    return safe_response
