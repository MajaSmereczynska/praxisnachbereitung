-- db/init/010_inventory_schema.sql
-- Cleanup
DROP TABLE IF EXISTS assignment;
DROP TABLE IF EXISTS device;
DROP TABLE IF EXISTS location;
DROP TABLE IF EXISTS devicetype;
DROP TABLE IF EXISTS person;

CREATE TABLE devicetype (
    devicetype_id SERIAL PRIMARY KEY,
    code          TEXT NOT NULL UNIQUE,
    description   TEXT
);

CREATE TABLE location (
    location_id   SERIAL PRIMARY KEY,
    code          TEXT NOT NULL UNIQUE,
    name          TEXT
);

CREATE TABLE person (
    personnel_no SERIAL PRIMARY KEY,
    name         TEXT NOT NULL,
    department   TEXT
);

CREATE TABLE device (
    device_id     SERIAL PRIMARY KEY,
    inventory_no  TEXT NOT NULL UNIQUE,
    devicetype_id INT NOT NULL REFERENCES devicetype(devicetype_id),
    location_id   INT REFERENCES location(location_id),
    model         TEXT
);

CREATE TABLE assignment (
    assignment_id SERIAL PRIMARY KEY,
    device_id     INT NOT NULL REFERENCES device(device_id) ON DELETE CASCADE,
    personnel_no  INT NOT NULL REFERENCES person(personnel_no) ON DELETE CASCADE,
    assigned_from TIMESTAMP NOT NULL DEFAULT NOW(),
    assigned_to   TIMESTAMP, -- NULL means "currently active"
    
    -- Time Logic
    CONSTRAINT check_dates CHECK (assigned_to IS NULL OR assigned_to >= assigned_from)
);

-- Max one active assignment per device
CREATE UNIQUE INDEX one_active_assignment_per_device 
ON assignment (device_id) 
WHERE assigned_to IS NULL;

INSERT INTO devicetype (code, description) VALUES 
    ('NB', 'Notebook'), 
    ('MON', 'Monitor'), 
    ('TAB', 'Tablet');

INSERT INTO location (code, name) VALUES 
    ('R-101', 'Server Room'), 
    ('R-202', 'Warehouse'), 
    ('HO', 'Home Office');

INSERT INTO person (name, department) VALUES 
    ('Alice Admin', 'IT'),
    ('Bob Builder', 'Production'),
    ('Charlie Sales', 'Sales');

INSERT INTO device (inventory_no, devicetype_id, location_id, model) VALUES 
    ('INV-001', 1, 1, 'Lenovo ThinkPad'),
    ('INV-002', 2, 2, 'Dell 24 Inch'),
    ('INV-003', 3, 3, 'iPad Pro');