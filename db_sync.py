import os
import sys
import csv
import sqlite3
import pyodbc
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACCESS_DB = os.path.join(BASE_DIR, "University_System (1).accdb")
SQLITE_DB = os.path.join(BASE_DIR, "University_System.db")
CSV_DIR = os.path.join(BASE_DIR, "db_csv")

PRIMARY_KEYS = {
    'Class_Sections': 'SectionID',
    'Courses': 'CourseID',
    'Departments': 'DepartmentID',
    'Enrollments': 'EnrollmentID',
    'Instructors': 'InstructorID',
    'Rooms': 'RoomID',
    'Schedules': 'ScheduleID',
    'Students': 'StudentID'
}

def get_access_connection():
    if not os.path.exists(ACCESS_DB):
        print(f"Error: Access database not found at {ACCESS_DB}")
        sys.exit(1)
    conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        f'DBQ={ACCESS_DB};'
    )
    return pyodbc.connect(conn_str)

def get_access_schema(cursor, table_name):
    schema = {}
    for col in cursor.columns(table=table_name):
        schema[col.column_name] = {
            'type_name': col.type_name,
            'nullable': col.nullable
        }
    return schema

def map_access_to_sqlite_type(access_type):
    access_type = access_type.upper()
    if 'INT' in access_type or 'COUNTER' in access_type or 'BIT' in access_type:
        return 'INTEGER'
    elif any(x in access_type for x in ('DOUBLE', 'DECIMAL', 'REAL', 'FLOAT', 'NUMERIC')):
        return 'REAL'
    elif 'DATE' in access_type or 'TIME' in access_type:
        return 'TEXT'
    else:
        return 'TEXT'

def parse_csv_value(val, schema_info):
    val = val.strip()
    if val == "":
        return None
    type_name = schema_info['type_name'].upper()
    if 'INT' in type_name or 'COUNTER' in type_name:
        return int(val)
    elif any(x in type_name for x in ('DOUBLE', 'DECIMAL', 'REAL', 'FLOAT', 'NUMERIC')):
        return float(val)
    elif 'DATE' in type_name or 'TIME' in type_name:
        # Try parsing various datetime formats
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%H:%M:%S'):
            try:
                return datetime.strptime(val, fmt)
            except ValueError:
                continue
        return val # Fallback to raw string
    else:
        return val

def export_db():
    print("Starting export from MS Access to SQLite & CSV...")
    
    # 1. Connect to Access
    access_conn = get_access_connection()
    access_cursor = access_conn.cursor()
    
    # 2. Get list of tables
    tables = [t.table_name for t in access_cursor.tables(tableType='TABLE')]
    print(f"Found tables: {tables}")
    
    # 3. Create CSV directory if not exists
    os.makedirs(CSV_DIR, exist_ok=True)
    
    # 4. Connect to SQLite
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_cursor = sqlite_conn.cursor()
    
    try:
        for table in tables:
            print(f"\nProcessing table: {table}")
            
            # Fetch table schema
            schema = get_access_schema(access_cursor, table)
            columns = list(schema.keys())
            
            # Fetch data
            access_cursor.execute(f"SELECT * FROM [{table}]")
            rows = access_cursor.fetchall()
            
            # --- Write to CSV ---
            csv_path = os.path.join(CSV_DIR, f"{table}.csv")
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                for row in rows:
                    row_data = []
                    for val in row:
                        if isinstance(val, datetime):
                            row_data.append(val.strftime('%Y-%m-%d %H:%M:%S'))
                        elif val is None:
                            row_data.append("")
                        else:
                            row_data.append(str(val))
                    writer.writerow(row_data)
            print(f"  Saved {len(rows)} rows to CSV: {os.path.basename(csv_path)}")
            
            # --- Write to SQLite ---
            # Drop table if exists to overwrite
            sqlite_cursor.execute(f"DROP TABLE IF EXISTS [{table}]")
            
            # Create SQLite table schema
            create_fields = []
            pk_col = PRIMARY_KEYS.get(table)
            for col_name, info in schema.items():
                sq_type = map_access_to_sqlite_type(info['type_name'])
                field_def = f"[{col_name}] {sq_type}"
                if col_name == pk_col:
                    field_def += " PRIMARY KEY"
                create_fields.append(field_def)
            
            create_sql = f"CREATE TABLE [{table}] ({', '.join(create_fields)})"
            sqlite_cursor.execute(create_sql)
            
            # Insert data into SQLite
            if rows:
                placeholders = ", ".join(["?"] * len(columns))
                insert_sql = f"INSERT INTO [{table}] ({', '.join(columns)}) VALUES ({placeholders})"
                
                sqlite_rows = []
                for row in rows:
                    row_data = []
                    for val in row:
                        if isinstance(val, datetime):
                            row_data.append(val.strftime('%Y-%m-%d %H:%M:%S'))
                        else:
                            row_data.append(val)
                    sqlite_rows.append(row_data)
                    
                sqlite_cursor.executemany(insert_sql, sqlite_rows)
            print(f"  Created SQLite table [{table}] with {len(rows)} rows.")
            
        sqlite_conn.commit()
        print("\nExport completed successfully!")
        
    finally:
        sqlite_conn.close()
        access_conn.close()

def import_sqlite():
    print("Starting import from SQLite back to MS Access...")
    if not os.path.exists(SQLITE_DB):
        print(f"Error: SQLite database not found at {SQLITE_DB}")
        return
        
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_cursor = sqlite_conn.cursor()
    
    access_conn = get_access_connection()
    access_cursor = access_conn.cursor()
    
    try:
        # Get list of tables from SQLite
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in sqlite_cursor.fetchall()]
        
        for table in tables:
            pk_col = PRIMARY_KEYS.get(table)
            if not pk_col:
                print(f"Warning: Primary key for table {table} not defined. Skipping.")
                continue
                
            print(f"\nSyncing table: {table}")
            
            # Fetch SQLite columns and rows
            sqlite_cursor.execute(f"SELECT * FROM [{table}]")
            rows = sqlite_cursor.fetchall()
            columns = [description[0] for description in sqlite_cursor.description]
            
            # Get Access schema to parse types correctly
            schema = get_access_schema(access_cursor, table)
            
            updates = 0
            inserts = 0
            
            for row in rows:
                row_dict = dict(zip(columns, row))
                pk_val = row_dict[pk_col]
                
                # Check if row exists in Access
                access_cursor.execute(f"SELECT COUNT(*) FROM [{table}] WHERE {pk_col}=?", (pk_val,))
                exists = access_cursor.fetchone()[0] > 0
                
                # Prepare data and parse types
                parsed_vals = []
                other_cols = []
                for col in columns:
                    if col == pk_col:
                        continue
                    other_cols.append(col)
                    parsed_vals.append(parse_csv_value(str(row_dict[col]) if row_dict[col] is not None else "", schema[col]))
                
                if exists:
                    # Update
                    set_clause = ", ".join([f"[{col}]=?" for col in other_cols])
                    update_sql = f"UPDATE [{table}] SET {set_clause} WHERE {pk_col}=?"
                    access_cursor.execute(update_sql, parsed_vals + [pk_val])
                    updates += 1
                else:
                    # Insert (include pk)
                    insert_cols = [pk_col] + other_cols
                    placeholders = ", ".join(["?"] * len(insert_cols))
                    insert_sql = f"INSERT INTO [{table}] ({', '.join(insert_cols)}) VALUES ({placeholders})"
                    
                    parsed_pk = parse_csv_value(str(pk_val), schema[pk_col])
                    access_cursor.execute(insert_sql, [parsed_pk] + parsed_vals)
                    inserts += 1
                    
            print(f"  Table [{table}]: Updated {updates} rows, Inserted {inserts} rows.")
            
        access_conn.commit()
        print("\nImport from SQLite completed successfully!")
        
    finally:
        sqlite_conn.close()
        access_conn.close()

def import_csv():
    print("Starting import from CSV back to MS Access...")
    if not os.path.exists(CSV_DIR):
        print(f"Error: CSV directory not found at {CSV_DIR}")
        return
        
    access_conn = get_access_connection()
    access_cursor = access_conn.cursor()
    
    try:
        csv_files = [f for f in os.listdir(CSV_DIR) if f.endswith('.csv')]
        
        for csv_file in csv_files:
            table = os.path.splitext(csv_file)[0]
            pk_col = PRIMARY_KEYS.get(table)
            if not pk_col:
                print(f"Warning: Primary key for table {table} not defined. Skipping.")
                continue
                
            csv_path = os.path.join(CSV_DIR, csv_file)
            print(f"\nSyncing table from CSV: {table}")
            
            schema = get_access_schema(access_cursor, table)
            
            updates = 0
            inserts = 0
            
            with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                columns = reader.fieldnames
                
                for row_dict in reader:
                    pk_val = row_dict[pk_col]
                    
                    # Check if row exists in Access
                    access_cursor.execute(f"SELECT COUNT(*) FROM [{table}] WHERE {pk_col}=?", (pk_val,))
                    exists = access_cursor.fetchone()[0] > 0
                    
                    # Prepare data and parse types
                    parsed_vals = []
                    other_cols = []
                    for col in columns:
                        if col == pk_col:
                            continue
                        other_cols.append(col)
                        parsed_vals.append(parse_csv_value(row_dict[col], schema[col]))
                    
                    if exists:
                        # Update
                        set_clause = ", ".join([f"[{col}]=?" for col in other_cols])
                        update_sql = f"UPDATE [{table}] SET {set_clause} WHERE {pk_col}=?"
                        access_cursor.execute(update_sql, parsed_vals + [pk_val])
                        updates += 1
                    else:
                        # Insert
                        insert_cols = [pk_col] + other_cols
                        placeholders = ", ".join(["?"] * len(insert_cols))
                        insert_sql = f"INSERT INTO [{table}] ({', '.join(insert_cols)}) VALUES ({placeholders})"
                        
                        parsed_pk = parse_csv_value(pk_val, schema[pk_col])
                        access_cursor.execute(insert_sql, [parsed_pk] + parsed_vals)
                        inserts += 1
                        
            print(f"  CSV [{csv_file}]: Updated {updates} rows, Inserted {inserts} rows.")
            
        access_conn.commit()
        print("\nImport from CSV completed successfully!")
        
    finally:
        access_conn.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python db_sync.py [export | import-sqlite | import-csv]")
        sys.exit(1)
        
    cmd = sys.argv[1].lower()
    if cmd == 'export':
        export_db()
    elif cmd == 'import-sqlite':
        import_sqlite()
    elif cmd == 'import-csv':
        import_csv()
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python db_sync.py [export | import-sqlite | import-csv]")
        sys.exit(1)
