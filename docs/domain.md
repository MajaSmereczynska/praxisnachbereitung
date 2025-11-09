```mermaid
erDiagram
    PERSON {
        int personnel_no PK
        string name
        string department
    }

    DEVICETYPE {
        int devicetype_id PK
        string code UK
        string description
    }

    LOCATION {
        int location_id PK
        string code UK
        string name
    }

    DEVICE {
        int device_id PK
        string inventory_no UK
        int devicetype_id FK
        int location_id FK
        string model
    }

    ASSIGNMENT {
        int assignment_id PK
        int device_id FK
        int personnel_no FK
        datetime assigned_from
        datetime assigned_to
    }

    DEVICETYPE ||--o{ DEVICE : "classified_as"
    LOCATION ||--o{ DEVICE : "located_at"
    PERSON ||--o{ ASSIGNMENT : "receives"
    DEVICE ||--o{ ASSIGNMENT : "assigned_to"
