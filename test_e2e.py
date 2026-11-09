"""
Fish Dock Full End-to-End Workflow Verification Script
Tests:
1. Public Categories & Products fetching
2. Customer Guest Order submission
3. Verification of generated Order Reference and WhatsApp Deep Link
4. Admin JWT Login
5. Admin Order Lookup & Status Verification
6. Admin Price & Weight Adjustment (weighing confirmation)
7. Customer Order Tracking showing updated final confirmed amounts
"""

import urllib.request
import json
import urllib.parse

API_BASE = "http://127.0.0.1:8001/api/v1"

def req(url, method="GET", data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data else None
    request = urllib.request.Request(f"{API_BASE}{url}", data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))

def run_e2e_test():
    print("🚀 Starting Fish Dock End-to-End Integration Test...")

    # Step 1: Public Customer Browses Products
    status, products_res = req("/products/")
    assert status == 200, f"Expected 200, got {status}"
    assert len(products_res["results"]) > 0, "No products returned"
    hilsa = next((p for p in products_res["results"] if "Hilsa" in p["name"]), products_res["results"][0])
    prawn = next((p for p in products_res["results"] if "Prawn" in p["name"]), products_res["results"][1])
    print(f"✅ Step 1: Customer browsed products. Selected '{hilsa['name']}' (৳{hilsa['base_price']}) & '{prawn['name']}' (৳{prawn['base_price']})")

    # Step 2: Customer Submits Order Request (Guest Checkout)
    order_payload = {
        "customer_name": "Tariqul Islam",
        "customer_phone": "+8801819998877",
        "customer_email": "tariq@example.com",
        "delivery_address": "House 24, Road 7, Block D, Mirpur-12",
        "delivery_area": "Mirpur, Dhaka",
        "delivery_city": "Dhaka",
        "preferred_delivery_slot": "Morning (8:00 AM – 12:00 PM)",
        "customer_notes": "Please verify fresh morning catch gills and send scale photo on WhatsApp.",
        "items": [
            {
                "product_id": hilsa["id"],
                "quantity": 2.0,
                "cutting_instruction": "Curry Cut (Cleaned with head split)"
            },
            {
                "product_id": prawn["id"],
                "quantity": 1.5,
                "cutting_instruction": "Whole with Shell"
            }
        ]
    }
    status, order_res = req("/orders/", method="POST", data=order_payload)
    assert status == 201, f"Expected 201, got {status}: {order_res}"
    created_order = order_res["data"]["order"]
    whatsapp_data = order_res["data"]["whatsapp"]

    order_ref = created_order["order_reference"]
    order_id = created_order["id"]
    assert order_ref.startswith("FD-"), f"Invalid order reference: {order_ref}"
    assert created_order["status"] == "pending_confirmation"
    print(f"✅ Step 2: Customer submitted order. Reference: {order_ref}, Status: {created_order['status']}, Indicative Subtotal: ৳{created_order['indicative_subtotal']}")

    # Step 3: Validate WhatsApp Deep Link & Message Content
    assert "https://wa.me/" in whatsapp_data["deep_link"], "Invalid WhatsApp deep link"
    assert order_ref in whatsapp_data["message_text"], "Order reference missing in WhatsApp message"
    assert "Tariqul Islam" in whatsapp_data["message_text"], "Customer name missing in WhatsApp message"
    print(f"✅ Step 3: Generated WhatsApp link verified: {whatsapp_data['deep_link'][:70]}...")

    # Step 4: Admin Authenticates via JWT
    status, auth_res = req("/auth/token/", method="POST", data={"username": "admin", "password": "admin123"})
    assert status == 200, f"Login failed: {auth_res}"
    admin_token = auth_res["access"]
    print(f"✅ Step 4: Admin authenticated successfully via JWT.")

    # Step 5: Admin Retrieves the Order from Admin API
    status, admin_order = req(f"/orders/admin/{order_id}/", token=admin_token)
    assert status == 200, f"Admin order lookup failed: {admin_order}"
    assert admin_order["data"]["order_reference"] == order_ref
    print(f"✅ Step 5: Admin accessed order {order_ref} in Admin Dashboard.")

    # Step 6: Admin Weighs Fresh Catch, Confirms Final Prices & Quantities on WhatsApp
    hilsa_item = admin_order["data"]["items"][0]
    prawn_item = admin_order["data"]["items"][1]

    # Suppose scale weight of Hilsa is 2.15 kg and price confirmed at 1350/kg
    # and Prawn is 1.50 kg at 950/kg
    price_confirm_payload = {
        "status": "price_confirmed",
        "whatsapp_status": "confirmed_via_whatsapp",
        "admin_notes": "Customer confirmed via WhatsApp call. Scale photos sent. Exact Hilsa weight 2.15 kg.",
        "items": [
            {
                "id": hilsa_item["id"],
                "final_unit_price": 1350.00,
                "quantity_adjusted": 2.15,
                "adjustment_reason": "Morning catch Padma Ilish was exactly 2.15 kg on digital scale"
            },
            {
                "id": prawn_item["id"],
                "final_unit_price": 950.00,
                "quantity_adjusted": 1.50,
                "adjustment_reason": "Verified weight"
            }
        ]
    }
    status, confirm_res = req(f"/orders/admin/{order_id}/confirm-price/", method="POST", data=price_confirm_payload, token=admin_token)
    assert status == 200, f"Confirmation failed: {confirm_res}"
    confirmed_data = confirm_res["data"]
    assert confirmed_data["status"] == "price_confirmed"
    assert confirmed_data["whatsapp_status"] == "confirmed_via_whatsapp"
    assert confirmed_data["final_confirmed_amount"] is not None
    print(f"✅ Step 6: Admin confirmed live weighing & price on WhatsApp. Final Confirmed Total: ৳{confirmed_data['final_confirmed_amount']}")

    # Step 7: Customer Tracks Live Order
    status, track_res = req(f"/orders/track/?reference={order_ref}")
    assert status == 200, f"Tracking failed: {track_res}"
    tracked_order = track_res["data"]["order"]
    assert tracked_order["status"] == "price_confirmed"
    assert tracked_order["final_confirmed_amount"] == confirmed_data["final_confirmed_amount"]
    print(f"✅ Step 7: Customer live order tracking verified. Live status: '{tracked_order['status']}', Confirmed Amount: ৳{tracked_order['final_confirmed_amount']}")

    print("\n🎉 ALL END-TO-END WORKFLOW TESTS PASSED 100% SUCCESSFULLY! 🐟🌊")

if __name__ == "__main__":
    run_e2e_test()

