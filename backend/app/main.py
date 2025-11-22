from fastapi import FastAPI, HTTPException
from .db import get_conn
from .models import DeviceCreate, AssignmentCreate

app = FastAPI(title="Inventar API (Section E)", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "ok"}

# SECTION E.2: DEVICES
@app.get("/devices")
def list_devices():
    """
    List all devices including their status (Free vs Assigned).
    """
    with get_conn() as conn, conn.cursor() as cur:
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
        return cur.fetchall()

@app.post("/devices", status_code=201)
def create_device(device: DeviceCreate):
    """
    Create a new device.
    Rule IR-01: Unique Inventory Number.
    """
    with get_conn() as conn, conn.cursor() as cur:
        # Check if inventory_no exists
        cur.execute("SELECT 1 FROM device WHERE inventory_no = %s", (device.inventory_no,))
        if cur.fetchone():
            # Rule IR-01 violation -> HTTP 409 
            raise HTTPException(status_code=409, detail="Inventory number already exists")

        cur.execute(
            """
            INSERT INTO device (inventory_no, devicetype_id, location_id, model)
            VALUES (%s, %s, %s, %s)
            RETURNING device_id
            """,
            (device.inventory_no, device.devicetype_id, device.location_id, device.model)
        )
        new_id = cur.fetchone()['device_id']
        return {"msg": "Device created", "device_id": new_id}

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