# 🎓 University System Chatbot Webhook & Database Migration

An integrated solution connecting a Microsoft Access database with a Dialogflow chatbot using Flask and Ngrok, alongside a bidirectional database migration and synchronization pipeline to SQLite and CSV.

This project was built to enable AI agents (like Cursor, Windsurf, etc.) to read, search, and edit database records directly in plain-text formats, while retaining full synchronization with the master MS Access `.accdb` file.

---

## 🛠️ Project Components

```
├── app.py                      # Flask webhook server for Dialogflow
├── db_sync.py                  # Bidirectional sync utility (Access ↔ SQLite & CSV)
├── University_System (1).accdb # Original binary MS Access database
├── University_System.db        # Ported SQLite database (agent-friendly)
├── University_System_Schema.md # Detailed schema & relationships guide
├── db_csv/                     # Plain-text CSV exports of all tables
│   ├── Students.csv
│   ├── Courses.csv
│   ├── Departments.csv
│   └── ... (8 tables total)
```

1. **Flask Webhook (`app.py`)**: Receives JSON requests from Dialogflow intents (e.g. queries for GPA or student addresses), runs queries on the database, and returns Arabic localized responses.
2. **SQLite Database (`University_System.db`)**: A portable version of the database. AI agents can query and update this using Python's built-in `sqlite3` driver without platform-dependent MS Access drivers.
3. **CSV Directory (`db_csv/`)**: Contains one plain-text CSV file per database table. Ideal for quick indexing, textual editing, and tracking version changes (git diffs).
4. **Sync Script (`db_sync.py`)**: Handles bidirectional updates to keep MS Access, SQLite, and CSVs in perfect sync.

---

## 🚀 Setup & Installation

### 1. Prerequisites
Ensure you have Python installed and the MS Access Database Engine driver on Windows. Then, install dependencies:
```bash
pip install flask pyodbc
```

### 2. Configure Ngrok
Download and authenticate Ngrok:
```bash
ngrok config add-authtoken "<YOUR_AUTHTOKEN>"
ngrok http 5000
```
Copy the generated public HTTPS URL (e.g., `https://xxxx.ngrok-free.dev`).

### 3. Run the Webhook Server
Start the Flask application:
```bash
python app.py
```

### 4. Link to Dialogflow
1. Open your Dialogflow console.
2. Navigate to **Fulfillment** in the left menu.
3. Enable **Webhook** and paste your Ngrok URL followed by `/webhook` (e.g., `https://xxxx.ngrok-free.dev/webhook`).
4. Click **Save**.

---

## 🔄 Database Sync Guide (`db_sync.py`)

Keep your databases aligned with these commands:

### Export: Access to SQLite & CSV
If you make manual changes inside MS Access and want to update the SQLite/CSVs:
```bash
python db_sync.py export
```

### Import: SQLite to Access
If an AI agent updates the data in the SQLite database (`University_System.db`), push changes back to MS Access:
```bash
python db_sync.py import-sqlite
```

### Import: CSV to Access
If you or an AI agent edit the CSV files in `db_csv/`, sync those changes back to MS Access:
```bash
python db_sync.py import-csv
```

---

## 📊 Database Schema & Relationships

For a detailed review of the 8 tables (`Students`, `Courses`, `Departments`, `Enrollments`, `Instructors`, `Rooms`, `Schedules`, `Class_Sections`) and their Entity-Relationship (ER) mappings, refer to [University_System_Schema.md](./University_System_Schema.md).
