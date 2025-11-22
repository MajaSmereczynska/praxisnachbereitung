from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os, json
import paho.mqtt.client as mqtt
from datetime import datetime

# Import DB connection and Pydantic models
from .db import get_conn
from .models import DeviceCreate, AssignmentCreate

app = FastAPI(title="Inventar App", version="1.0.0")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# --- MQTT Helper ---
MQTT_HOST = os.getenv("MQTT_HOST", "mqtt")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

def mqtt_client() -> mqtt.Client:
    c = mqtt.Client()
    c.connect(MQTT_HOST, MQTT_PORT, keepalive=30)
    return c

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Inventar App"}
    )

@app.get("/health")
def health():
    return {"status": "ok"}

# SECTION F.1 & F.2: DEVICES UI

@app.get("/devices", response_class=HTMLResponse)
def devices_page(request: Request, error: str = None):
    # Added 'error' parameter here to catch messages from the URL
    with get_conn() as conn, conn.cursor() as cur:
        # F.1: List all devices
        cur.execute("""
            SELECT d.device_id, d.inventory_no, d.model, 
                   dt.description as type_name, l.name as location_name,
                   CASE 
                       WHEN a.assignment_id IS NOT NULL THEN 'Assigned' 
                       ELSE 'Free' 
                   END as status
            FROM device d
            JOIN devicetype dt ON d.devicetype_id = dt.devicetype_id
            LEFT JOIN location l ON d.location_id = l.location_id
            LEFT JOIN assignment a ON d.device_id = a.device_id AND a.assigned_to IS NULL
            ORDER BY d.inventory_no
        """)
        devices = list(cur.fetchall())

        cur.execute("SELECT * FROM devicetype ORDER BY description")
        types = list(cur.fetchall())
        
        cur.execute("SELECT * FROM location ORDER BY name")
        locations = list(cur.fetchall())

    return templates.TemplateResponse(
        "inventory.html",
        {
            "request": request, 
            "title": "Geräteverwaltung", 
            "devices": devices,
            "types": types,
            "locations": locations,
            "error": error # Pass error message to template HTML
        },
    )

@app.post("/devices", response_class=HTMLResponse)
def create_device(
    request: Request,
    inventory_no: str = Form(...),
    devicetype_id: int = Form(...),
    location_id: int = Form(...),
    model: str = Form(...)
):
    # F.2: POST Endpoint for new devices
    with get_conn() as conn, conn.cursor() as cur:
        # Added RETURNING device_id to check if it worked
        cur.execute(
            """
            INSERT INTO device (inventory_no, devicetype_id, location_id, model)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (inventory_no) DO NOTHING
            RETURNING device_id
            """,
            (inventory_no, devicetype_id, location_id, model)
        )
        row = cur.fetchone()
        
    if not row:
        # If 'row' is None, the insert failed (duplicate)
        # Redirect with an error message in the URL
        return RedirectResponse("/devices?error=Doppelte Inventarnummer!", status_code=303)
    
    # Success
    return RedirectResponse("/devices", status_code=303)

# SECTION E.3: ASSIGNMENTS
@app.get("/assignments/active")
def list_active_assignments():
    """
    List only currently active assignments (assigned_to IS NULL).
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT a.assignment_id, a.assigned_from, 
                   d.inventory_no, d.model,
                   p.name as person_name
            FROM assignment a
            JOIN device d ON a.device_id = d.device_id
            JOIN person p ON a.personnel_no = p.personnel_no
            WHERE a.assigned_to IS NULL
        """)
        return cur.fetchall()

@app.post("/assignments", status_code=201)
def create_assignment(assign: AssignmentCreate):
    """
    Issue a device.
    Rule IR-02: Max one active assignment per device.
    """
    with get_conn() as conn, conn.cursor() as cur:
        # Check if device is already assigned (IR-02)
        cur.execute(
            "SELECT 1 FROM assignment WHERE device_id = %s AND assigned_to IS NULL",
            (assign.device_id,)
        )
        if cur.fetchone():
            # Rule IR-02 violation -> HTTP 409
            raise HTTPException(status_code=409, detail="Device is already assigned")

        # Create assignment (If date not provided, DB defaults to NOW via COALESCE or SQL default)
        cur.execute(
            """
            INSERT INTO assignment (device_id, personnel_no, assigned_from)
            VALUES (%s, %s, COALESCE(%s, NOW()))
            RETURNING assignment_id
            """,
            (assign.device_id, assign.personnel_no, assign.assigned_from)
        )
        new_id = cur.fetchone()['assignment_id']
        return {"msg": "Assignment created", "assignment_id": new_id}

@app.post("/assignments/{assignment_id}/return")
def return_assignment(assignment_id: int):
    """
    Return a device.
    Rule IR-03: Return date >= Issue date (Handled by DB Constraint).
    """
    with get_conn() as conn, conn.cursor() as cur:
        try:
            cur.execute(
                """
                UPDATE assignment
                SET assigned_to = NOW()
                WHERE assignment_id = %s AND assigned_to IS NULL
                RETURNING assignment_id
                """,
                (assignment_id,)
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Assignment not found or already returned")
            
            return {"msg": "Device returned"}
            
        except Exception as e:
            # If DB constraint "check_dates" fails (IR-03), it raises an error here
            raise HTTPException(status_code=422, detail=f"Domain Rule Error: {e}")