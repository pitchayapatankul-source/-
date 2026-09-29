#!/usr/bin/env python3
"""
TableChain Backend HTTP Server & REST API
Built with Python 3 standard library (http.server + sqlite3).
Zero external dependencies required.
"""

import sys
import os
import json
import sqlite3
import random
import string
from urllib.parse import urlparse, parse_qs
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from datetime import datetime, date

from database import init_db, seed_db, get_connection

PORT = 3000
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "public")

class TableChainRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode("utf-8"))

    def _read_json_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        raw = self.rfile.read(content_length)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path.startswith("/api/"):
            return self.handle_api_get(path, query)

        # SPA routing: if path doesn't have an extension (like .js, .css, .png), serve index.html
        if not os.path.splitext(path)[1]:
            self.path = "/index.html"
            return super().do_GET()

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/"):
            return self.handle_api_post(path)
        self._send_json(404, {"error": "Endpoint not found"})

    def do_PATCH(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/"):
            return self.handle_api_patch(path)
        self._send_json(404, {"error": "Endpoint not found"})

    # ================= API HANDLERS ================= #

    def handle_api_get(self, path, query):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            # 1. GET /api/restaurants
            if path == "/api/restaurants":
                cursor.execute("SELECT * FROM restaurants ORDER BY rating DESC")
                restaurants = [dict(row) for row in cursor.fetchall()]
                for r in restaurants:
                    if r.get("gallery"):
                        try: r["gallery"] = json.loads(r["gallery"])
                        except: pass
                    if r.get("facilities"):
                        try: r["facilities"] = json.loads(r["facilities"])
                        except: pass
                    if r.get("menu"):
                        try: r["menu"] = json.loads(r["menu"])
                        except: pass
                    
                    # Fetch tables count
                    cursor.execute("SELECT COUNT(*) as total_tables FROM tables WHERE restaurant_id = ?", (r["id"],))
                    r["total_tables"] = cursor.fetchone()["total_tables"]
                return self._send_json(200, {"success": True, "restaurants": restaurants})

            # 2. GET /api/restaurants/<id>
            elif path.startswith("/api/restaurants/"):
                rest_id = path.split("/")[-1]
                cursor.execute("SELECT * FROM restaurants WHERE id = ?", (rest_id,))
                row = cursor.fetchone()
                if not row:
                    return self._send_json(404, {"error": "Restaurant not found"})
                restaurant = dict(row)
                if restaurant.get("gallery"):
                    try: restaurant["gallery"] = json.loads(restaurant["gallery"])
                    except: pass
                if restaurant.get("facilities"):
                    try: restaurant["facilities"] = json.loads(restaurant["facilities"])
                    except: pass
                if restaurant.get("menu"):
                    try: restaurant["menu"] = json.loads(restaurant["menu"])
                    except: pass

                # Get tables
                cursor.execute("SELECT * FROM tables WHERE restaurant_id = ? ORDER BY table_number ASC", (rest_id,))
                restaurant["tables"] = [dict(t) for t in cursor.fetchall()]
                return self._send_json(200, {"success": True, "restaurant": restaurant})

            # 3. GET /api/reservations
            elif path == "/api/reservations":
                wallet = query.get("wallet", [None])[0]
                rest_id = query.get("restaurant_id", [None])[0]
                booking_id = query.get("booking_id", [None])[0]

                sql = """
                SELECT r.*, res.name as restaurant_name, res.location as restaurant_location, 
                       res.cuisine as restaurant_cuisine, res.image_url as restaurant_image,
                       t.table_number, t.capacity as table_capacity
                FROM reservations r
                JOIN restaurants res ON r.restaurant_id = res.id
                JOIN tables t ON r.table_id = t.id
                WHERE 1=1
                """
                params = []
                if wallet:
                    sql += " AND LOWER(r.wallet_address) = LOWER(?)"
                    params.append(wallet)
                if rest_id:
                    sql += " AND r.restaurant_id = ?"
                    params.append(rest_id)
                if booking_id:
                    sql += " AND r.booking_id = ?"
                    params.append(booking_id)

                sql += " ORDER BY r.reservation_date DESC, r.reservation_time DESC"
                cursor.execute(sql, params)
                reservations = [dict(row) for row in cursor.fetchall()]
                return self._send_json(200, {"success": True, "reservations": reservations})

            # 4. GET /api/tables
            elif path == "/api/tables":
                rest_id = query.get("restaurant_id", [None])[0]
                if rest_id:
                    cursor.execute("SELECT * FROM tables WHERE restaurant_id = ? ORDER BY table_number ASC", (rest_id,))
                else:
                    cursor.execute("SELECT * FROM tables ORDER BY restaurant_id, table_number ASC")
                tables = [dict(row) for row in cursor.fetchall()]
                return self._send_json(200, {"success": True, "tables": tables})

            # 5. GET /api/check-availability
            elif path == "/api/check-availability":
                rest_id = query.get("restaurant_id", [None])[0]
                date_val = query.get("date", [None])[0]
                time_val = query.get("time", [None])[0]
                guests = int(query.get("guests", [1])[0])

                if not (rest_id and date_val and time_val):
                    return self._send_json(400, {"error": "Missing restaurant_id, date, or time"})

                # Find all tables capable of holding guests
                cursor.execute("""
                SELECT * FROM tables 
                WHERE restaurant_id = ? AND capacity >= ? AND status != 'Unavailable'
                ORDER BY capacity ASC
                """, (rest_id, guests))
                eligible_tables = [dict(t) for t in cursor.fetchall()]

                # Find tables already reserved for that date and time
                cursor.execute("""
                SELECT table_id FROM reservations
                WHERE restaurant_id = ? AND reservation_date = ? AND reservation_time = ?
                  AND booking_status NOT IN ('Cancelled', 'No-show')
                """, (rest_id, date_val, time_val))
                booked_table_ids = set(r["table_id"] for r in cursor.fetchall())

                available_tables = [t for t in eligible_tables if t["id"] not in booked_table_ids]

                return self._send_json(200, {
                    "success": True,
                    "available": len(available_tables) > 0,
                    "available_tables": available_tables,
                    "booked_count": len(booked_table_ids)
                })

            # 6. GET /api/stats
            elif path == "/api/stats":
                rest_id = query.get("restaurant_id", [None])[0]
                today_str = date.today().strftime("%Y-%m-%d")

                sql_base = "FROM reservations WHERE 1=1"
                params = []
                if rest_id:
                    sql_base += " AND restaurant_id = ?"
                    params.append(rest_id)

                # Today's reservations
                cursor.execute(f"SELECT COUNT(*) as count {sql_base} AND reservation_date = ?", params + [today_str])
                today_res = cursor.fetchone()["count"]

                # Confirmed bookings
                cursor.execute(f"SELECT COUNT(*) as count {sql_base} AND booking_status = 'Confirmed'", params)
                confirmed = cursor.fetchone()["count"]

                # Pending payments
                cursor.execute(f"SELECT COUNT(*) as count {sql_base} AND booking_status = 'Pending Payment'", params)
                pending = cursor.fetchone()["count"]

                # Revenue (Confirmed & Completed)
                cursor.execute(f"SELECT COALESCE(SUM(booking_fee), 0) as eth_revenue {sql_base} AND booking_status IN ('Confirmed', 'Completed')", params)
                eth_revenue = cursor.fetchone()["eth_revenue"]

                # Available Tables
                table_sql = "SELECT COUNT(*) as count FROM tables WHERE status = 'Available'"
                table_params = []
                if rest_id:
                    table_sql += " AND restaurant_id = ?"
                    table_params.append(rest_id)
                cursor.execute(table_sql, table_params)
                available_tables = cursor.fetchone()["count"]

                return self._send_json(200, {
                    "success": True,
                    "stats": {
                        "today_reservations": today_res,
                        "confirmed_bookings": confirmed,
                        "pending_payments": pending,
                        "total_revenue_eth": round(eth_revenue, 4),
                        "total_revenue_thb": round(eth_revenue * 125000, 2), # approx ETH/THB rate
                        "available_tables": available_tables
                    }
                })

            else:
                return self._send_json(404, {"error": "API route not found"})

        finally:
            conn.close()

    def handle_api_post(self, path):
        body = self._read_json_body()
        conn = get_connection()
        cursor = conn.cursor()

        try:
            # 1. POST /api/reservations
            if path == "/api/reservations":
                restaurant_id = body.get("restaurant_id")
                guest_count = int(body.get("guest_count", 2))
                reservation_date = body.get("reservation_date")
                reservation_time = body.get("reservation_time")
                wallet_address = body.get("wallet_address", "0x0000000000000000000000000000000000000000")
                customer_name = body.get("customer_name", "Anonymous Guest")
                customer_email = body.get("customer_email", "")
                customer_phone = body.get("customer_phone", "")
                special_requests = body.get("special_requests", "")
                table_id = body.get("table_id")

                if not (restaurant_id and reservation_date and reservation_time):
                    return self._send_json(400, {"error": "Missing required booking details (restaurant, date, time)"})

                # Fetch restaurant fee
                cursor.execute("SELECT booking_fee, name, wallet_address FROM restaurants WHERE id = ?", (restaurant_id,))
                rest_row = cursor.fetchone()
                if not rest_row:
                    return self._send_json(404, {"error": "Restaurant not found"})
                booking_fee = rest_row["booking_fee"]

                # If no specific table_id provided, assign the best available matching table
                if not table_id:
                    cursor.execute("""
                    SELECT id, table_number, capacity FROM tables
                    WHERE restaurant_id = ? AND capacity >= ? AND status != 'Unavailable'
                      AND id NOT IN (
                          SELECT table_id FROM reservations
                          WHERE restaurant_id = ? AND reservation_date = ? AND reservation_time = ?
                            AND booking_status NOT IN ('Cancelled', 'No-show')
                      )
                    ORDER BY capacity ASC
                    LIMIT 1
                    """, (restaurant_id, guest_count, restaurant_id, reservation_date, reservation_time))
                    assigned_table = cursor.fetchone()
                    if not assigned_table:
                        return self._send_json(409, {
                            "error": "No available tables found for the selected date, time, and party size.",
                            "code": "TABLE_UNAVAILABLE"
                        })
                    table_id = assigned_table["id"]
                else:
                    # Double booking prevention check for specified table
                    cursor.execute("""
                    SELECT id FROM reservations 
                    WHERE table_id = ? AND reservation_date = ? AND reservation_time = ?
                      AND booking_status NOT IN ('Cancelled', 'No-show')
                    """, (table_id, reservation_date, reservation_time))
                    existing = cursor.fetchone()
                    if existing:
                        return self._send_json(409, {
                            "error": "Conflict: This specific table has already been reserved for this time slot.",
                            "code": "TABLE_ALREADY_RESERVED"
                        })

                # Generate clean unique booking ID (e.g. TC-20261010-00481)
                date_compact = reservation_date.replace("-", "")
                rand_suffix = "".join(random.choices(string.digits, k=5))
                booking_id = f"TC-{date_compact}-{rand_suffix}"

                created_at = datetime.now().isoformat()
                init_payment_status = body.get("payment_status", "Pending Payment")
                init_booking_status = body.get("booking_status", "Pending Payment")
                tx_hash = body.get("transaction_hash", None)

                cursor.execute("""
                INSERT INTO reservations (
                    booking_id, restaurant_id, customer_name, customer_email, customer_phone,
                    table_id, reservation_date, reservation_time, guest_count, booking_fee,
                    wallet_address, transaction_hash, payment_status, booking_status, special_requests, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    booking_id, restaurant_id, customer_name, customer_email, customer_phone,
                    table_id, reservation_date, reservation_time, guest_count, booking_fee,
                    wallet_address, tx_hash, init_payment_status, init_booking_status, special_requests, created_at
                ))
                conn.commit()

                # Fetch full created record
                cursor.execute("""
                SELECT r.*, res.name as restaurant_name, res.location as restaurant_location,
                       res.cuisine as restaurant_cuisine, res.wallet_address as restaurant_wallet,
                       t.table_number, t.capacity as table_capacity
                FROM reservations r
                JOIN restaurants res ON r.restaurant_id = res.id
                JOIN tables t ON r.table_id = t.id
                WHERE r.booking_id = ?
                """, (booking_id,))
                new_booking = dict(cursor.fetchone())

                return self._send_json(201, {
                    "success": True,
                    "booking": new_booking,
                    "message": "Reservation created. Awaiting blockchain payment confirmation."
                })

            # 2. POST /api/tables
            elif path == "/api/tables":
                restaurant_id = body.get("restaurant_id")
                table_number = body.get("table_number")
                capacity = int(body.get("capacity", 2))
                status = body.get("status", "Available")

                if not (restaurant_id and table_number):
                    return self._send_json(400, {"error": "Missing restaurant_id or table_number"})

                try:
                    cursor.execute("""
                    INSERT INTO tables (restaurant_id, table_number, capacity, status)
                    VALUES (?, ?, ?, ?)
                    """, (restaurant_id, table_number, capacity, status))
                    conn.commit()
                    table_id = cursor.lastrowid
                    return self._send_json(201, {"success": True, "table_id": table_id, "table_number": table_number})
                except sqlite3.IntegrityError:
                    return self._send_json(409, {"error": f"Table {table_number} already exists in this restaurant"})

            # 3. POST /api/reset-demo
            elif path == "/api/reset-demo":
                conn.close()
                if os.path.exists("tablechain.db"):
                    os.remove("tablechain.db")
                init_db()
                seed_db()
                return self._send_json(200, {"success": True, "message": "Demo database successfully reset!"})

            else:
                return self._send_json(404, {"error": "Endpoint not found"})

        finally:
            conn.close()

    def handle_api_patch(self, path):
        body = self._read_json_body()
        conn = get_connection()
        cursor = conn.cursor()

        try:
            # 1. PATCH /api/reservations/<booking_id>
            if path.startswith("/api/reservations/"):
                booking_id = path.split("/")[-1]
                cursor.execute("SELECT * FROM reservations WHERE booking_id = ?", (booking_id,))
                existing = cursor.fetchone()
                if not existing:
                    return self._send_json(404, {"error": "Reservation not found"})

                fields_to_update = []
                values = []
                for field in ["payment_status", "booking_status", "transaction_hash", "wallet_address", "special_requests"]:
                    if field in body:
                        fields_to_update.append(f"{field} = ?")
                        values.append(body[field])

                if not fields_to_update:
                    return self._send_json(400, {"error": "No valid fields provided to update"})

                values.append(booking_id)
                query = f"UPDATE reservations SET {', '.join(fields_to_update)} WHERE booking_id = ?"
                cursor.execute(query, values)
                conn.commit()

                # If status updated to Confirmed, update table status if needed
                if body.get("booking_status") == "Confirmed":
                    cursor.execute("UPDATE tables SET status = 'Reserved' WHERE id = ?", (existing["table_id"],))
                    conn.commit()
                elif body.get("booking_status") in ["Completed", "Cancelled", "No-show"]:
                    cursor.execute("UPDATE tables SET status = 'Available' WHERE id = ?", (existing["table_id"],))
                    conn.commit()

                cursor.execute("""
                SELECT r.*, res.name as restaurant_name, res.location as restaurant_location,
                       res.cuisine as restaurant_cuisine, t.table_number
                FROM reservations r
                JOIN restaurants res ON r.restaurant_id = res.id
                JOIN tables t ON r.table_id = t.id
                WHERE r.booking_id = ?
                """, (booking_id,))
                updated_booking = dict(cursor.fetchone())

                return self._send_json(200, {
                    "success": True,
                    "booking": updated_booking,
                    "message": f"Reservation {booking_id} status updated to {updated_booking['booking_status']}"
                })

            # 2. PATCH /api/tables/<id>
            elif path.startswith("/api/tables/"):
                table_id = path.split("/")[-1]
                status = body.get("status")
                if not status:
                    return self._send_json(400, {"error": "Missing new table status"})

                cursor.execute("UPDATE tables SET status = ? WHERE id = ?", (status, table_id))
                conn.commit()
                return self._send_json(200, {"success": True, "table_id": table_id, "status": status})

            else:
                return self._send_json(404, {"error": "API route not found"})

        finally:
            conn.close()

def run_server():
    init_db()
    seed_db()
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    server_address = ("0.0.0.0", PORT)
    httpd = ThreadingHTTPServer(server_address, TableChainRequestHandler)
    print(f"TableChain server running at http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
