# praxisnachbereitung

## Tag 1

A1
- Repository erstellt 
- Lokal geklont
- CSV Dateien kopiert
- Commit und push ausgefuehrt

A2
- CSV Dateien importiert
- Leere Datensaetze in Query Editor entfernt

A3
- Geraete mit Ausleihen gemerged ueber key 'Geraetenummer'
- Tabelle erweitert mit Mitarbeiterdaten ueber Mitarbeiter-ID

A4
- Pivottable erstellt mit Filter nach 'Rueckgabe am'
- Tabelle von A3 nach Laptops ueber query gefiltert
- Pivottable erstellt mit Geraetetyp in Zeile und Geraetenummer zur Errechnung der Summe
- Diagramme erstellt (Kreisdiagramm)
- Standort als spalte hinzugefuegt und Saeulendiagramm erstellt

A5
- Tabelle manuell als CSV exportiert
- Python skript fuer export der Tabelle erstellt
- Dokumentierung der Dokummentierung
- Commit und push ausgefuehrt 

## Tag 2

Prüfliste
- [X] docker compose up -d erfolgreich; /health = ok
- [X] docs/domain.md mit ERD & Regeln angelegt
- [X] Branch, PR, Merge durchgeführt

## Tag 3

### A

"Which building blocks play together?" 
The Publisher (Terminal 2) sends a message to the Broker (Eclipse Mosquitto container). The Broker looks up who is interested in that topic and forwards the message to the Subscriber (Terminal 1).

### B

Structure of g_starter:
- db.py: It uses row_factory=dict_row. This is important! It means when we write Python later, the database will give us data back like {"name": "Anna"} instead of just ("Anna",).
- 001_schema.sql: The keywords ON DELETE CASCADE mean that if you delete the "Student" (the parent), the database automatically deletes all "Grades" (the children) linked to that ID. Without this, the database would throw an error if you tried to delete a student who still had grades.
- Templates: They use Jinja2 (loops like {% for %}) and htmx for the grades list (look at hx-target="#grade-list" in grades/index.html). It generates the HTML on the server before sending it to the browser.

### C

Minimal structure:
.
├── backend/
│   └── app/
│       ├── templates/
│       ├── main.py
│       └── db.py
├── db/
│   └── init/
├── mqtt/
│   └── mosquitto.conf
└── docker-compose.yml

### D

Cretaed the new sql file

### E

Implementation of a RESTful API using **FastAPI** and **Pydantic** to manage the inventory lifecycle, enforcing strict domain consistency rules.

#### 🛡️ Domain Rules Implemented
* **IR-01: Unique Inventory Number**
    * Ensures no two devices share the same `inventory_no`.
    * **Result:** Returns `409 Conflict` on duplicates.
* **IR-02: Single Active Assignment**
    * A device cannot be issued if it is currently assigned (where `assigned_to` is NULL).
    * **Result:** Returns `409 Conflict` if the device is busy.
* **IR-03: Chronological Consistency**
    * A device cannot be returned before it was issued.
    * **Result:** Enforced via Database Constraints and API checks (`422 Unprocessable Entity`).

#### 🔌 Key Endpoints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/devices` | [cite_start]List all devices with calculated status (`Free` / `Assigned`). |
| `POST` | `/devices` | [cite_start]Register a new device (validates IR-01). |
| `GET` | `/assignments/active` | [cite_start]List currently ongoing loans. |
| `POST` | `/assignments` | [cite_start]Issue a device to a person (validates IR-02). |
| `POST` | `/assignments/{id}/return` | [cite_start]Mark an assignment as finished (validates IR-03). |

**1. Rule IR-01: Unique Inventory Number Constraint**
No two devices can share the same `inventory_no`.

* ✅ **Success (Happy Path)**
  * **Action:** Create a new device with a unique ID.
  * **Method:** `POST /devices`
  * **Payload:**
    ```json
    {
      "inventory_no": "TEST-DEVICE-01",
      "devicetype_id": 1,
      "location_id": 1,
      "model": "Test Model X"
    }
    ```
  * **Result:** `200 OK` / `201 Created`

* ❌ **Error Case**
  * **Action:** Try to create the same device again.
  * **Payload:** (Same as above)
  * **Result:** `409 Conflict`
  * **Response:** `{"detail": "Inventory number already exists"}`

---

**2. Rule IR-02: One Active Assignment Constraint**
A device cannot be assigned if it is currently issued to someone else (i.e., not yet returned).

* ✅ **Success (Happy Path)**
  * **Action:** Issue a device that is currently "Free".
  * **Method:** `POST /assignments`
  * **Payload:**
    ```json
    {
      "device_id": 1,
      "personnel_no": 1
    }
    ```
  * **Result:** `200 OK` / `201 Created` (Returns `assignment_id`, e.g., 5)

* ❌ **Error Case**
  * **Action:** Try to assign Device 1 again while the previous assignment is still active.
  * **Payload:**
    ```json
    {
      "device_id": 1,
      "personnel_no": 2
    }
    ```
  * **Result:** `409 Conflict`
  * **Response:** `{"detail": "Device is already assigned"}`

---

**3. Rule IR-03: Lifecycle Consistency Constraint**
A device must be active to be returned, and cannot be returned twice. (Date logic `assigned_to` >= `assigned_from` is enforced by DB constraints).

* ✅ **Success (Happy Path)**
  * **Action:** Return the assignment created in the previous step.
  * **Method:** `POST /assignments/{assignment_id}/return`
  * **Path Parameter:** `assignment_id = 1`
  * **Result:** `200 OK`
  * **Response:** `{"msg": "Device returned"}`

* ❌ **Error Case**
  * **Action:** Try to return the same assignment (ID 1) a second time.
  * **Method:** `POST /assignments/1/return`
  * **Result:** `422 Unprocessable Entity` (or `404 Not Found`)
  * **Response:** `{"detail": "Assignment not found or already returned"}`

### F

Implemented a server-side rendered user interface using Jinja2 templates to provide a visual frontend for the inventory system.
Inventory Dashboard (/devices): Displays a complete list of devices including technical details (Inventory No, Model) and a dynamically calculated status (Free or Assigned) based on active assignments .
Device Registration: Integrated an HTML form to register new devices.
Includes dynamic dropdowns fetching real-time data for Locations and Device Types.
Implements Post-Redirect-Get pattern to handle form submissions.
Provides visual error feedback for duplicate inventory numbers (Rule IR-01) via URL parameters.
Navigation: Added a central index.html landing page to navigate between the UI and API documentation.

### G

Events in Terminal when a device is issued or returned (udner different topics)

### Prüfliste (Ende der Übung)
- [X] Tag-2-Branch (tag2-mqtt-demo o. ä.) existiert und läuft mit MQTT-Chat.
- [X] Inventar-Branch (feat/inventar-app o. ä.) existiert.
- [X] Init-SQL für Inventar ist angelegt und erzeugt alle Tabellen.
- [X] REST-Endpunkte für Devices & Assignments funktionieren inkl. Domänenregeln.
- [X] Mindestens eine einfache UI-Seite für Inventar ist vorhanden.
- [X] Ihr könnt Branch-Wechsel, Schema, API und einen UI-Flow mündlich erklären. 

## Tag 4

### A

📝 Schema Change: Damage Notes
Business Requirement: We need to capture information about potential damages when a device is returned.
Implementation: Added a new column damage_notes to the assignment table.
Design Decisions:
Type: Text was chosen to allow free-form descriptions of the damage.
Optionality: The column is nullable (optional) because most devices are returned without damage, so it should not be a mandatory field.
Tooling: Migration created and applied using Alembic.

### B

1. CSV Export (/assignments.csv)
Format: Plain text, semicolon-separated values.
Use Case: Ideal for automated data processing and stable imports.
Advantage: Lightweight and universally readable by almost any tool (Power Query, Python scripts, legacy systems). It creates a stable "data pipeline" connection in Excel that refreshes easily without formatting issues.

2. Excel Export (/assignments.xlsx)
Format: Binary OpenXML format (generated via Pandas/OpenPyXL).
Use Case: Ideal for business users and ad-hoc reporting.
Advantage: Ready-to-use for humans. It opens directly in Excel with correct column types (dates recognized automatically) and headers, requiring no import wizard configuration.

Recommendation: Use CSV for building permanent dashboards (Power BI/Excel Power Query) and XLSX for quick email snapshots or management reports.

### C
Comparison: URL vs. File Import

Variant 1 (CSV via URL):art 
Best for: Live Dashboards and "Always Up-to-Date" reporting.
Why: The user just clicks "Refresh" to get the latest state from the database without leaving Excel.

Variant 2 (XLSX File):
Best for: Monthly Reports, Archiving, or Offline Analysis.
Why: It creates a "Snapshot" in time. Use this when you need to freeze the data (e.g., "Q3 Inventory Report") and ensure it doesn't change even if the database updates.