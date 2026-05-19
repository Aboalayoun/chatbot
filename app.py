from flask import Flask, request, jsonify
import pyodbc
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

def get_db_connection():
    # 1. Search for chat2.accdb first, then fallback to chat.accdb
    db_path = os.path.join(BASE_DIR, "University_System (1).accdb")
    if not os.path.exists(db_path):
        db_path = os.path.join(BASE_DIR, "University_System (1).accdb")
    
    if not os.path.exists(db_path):
        return None
    
    conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        f'DBQ={db_path};'
    )
    return pyodbc.connect(conn_str)

@app.route('/webhook', methods=['POST'])
def webhook():
    # 1. Validate payload structure
    req = request.get_json(silent=True)
    if not req or 'queryResult' not in req:
        return jsonify({"fulfillmentText": "طلب غير صالح"}), 400
        
    query_result = req.get('queryResult', {})
    intent_obj = query_result.get('intent', {})
    intent_name = intent_obj.get('displayName')
    parameters = query_result.get('parameters', {})
    
    if not intent_name:
        return jsonify({"fulfillmentText": "طلب غير صالح"}), 400

    conn = None
    try:
        # 2. Establish connection per request
        conn = get_db_connection()
        if conn is None:
            return jsonify({
                "fulfillmentText": "عذراً، لم نتمكن من الوصول إلى قاعدة البيانات حالياً."
            })
        
        cursor = conn.cursor()
        
        # 3. Handle Intents
        if intent_name == "get_gpa":
            name = parameters.get('name', '').strip()
            if not name:
                return jsonify({
                    "fulfillmentText": "يرجى تحديد اسم الطالب لمعرفة المعدل."
                })
            
            query = "SELECT GPA FROM Students WHERE StudentName=?"
            cursor.execute(query, (name,))
            row = cursor.fetchone()
            
            if row:
                gpa = row[0]
                response = f"GPA الخاص بـ {name} هو {gpa}"
            else:
                response = f"عذراً، الطالب {name} غير مسجل في النظام."
                
        elif intent_name == "get_address":
            name = (parameters.get('person') or parameters.get('name') or '').strip()
            if not name:
                return jsonify({
                    "fulfillmentText": "يرجى تحديد اسم الطالب لمعرفة العنوان."
                })
            
            query = "SELECT City FROM Students WHERE StudentName=?"
            cursor.execute(query, (name,))
            row = cursor.fetchone()
            
            if row:
                city = row[0]
                response = f"العنوان الخاص بـ {name} هو {city}"
            else:
                response = f"عذراً، الطالب {name} غير مسجل في النظام."
        else:
            response = "عذراً، لم أفهم هذا السؤال."
            
        return jsonify({"fulfillmentText": response})
        
    except Exception as e:
        print(f"Error handling database query: {e}")
        return jsonify({
            "fulfillmentText": "حدث خطأ أثناء الاستعلام من قاعدة البيانات."
        })
        
    finally:
        # 3. Always close connection to avoid file lock
        if conn:
            try:
                conn.close()
            except Exception:
                pass

if __name__ == '__main__':
    app.run(port=5000)

