<div align="center">
  <h2>🎓 University System Chatbot Webhook & Database Migration</h2>
  <p><b>اختر اللغة / Choose Language:</b></p>
  <a href="#arabic-version"><b>العربية 🇪🇬</b></a> | <a href="#english-version"><b>English 🇺🇸</b></a>
</div>

---

<!-- القسم العربي (مفتوح افتراضياً) -->
<details open id="arabic-version">
  <summary><b>🔽 اضغط هنا لإخفاء/إظهار الشرح باللغة العربية (Toggle Arabic Version)</b></summary>
  <br>

  # 🎓 شات بوت نظام الجامعة وهجرة قاعدة البيانات (Access ↔ SQLite & CSV)

  حل برمجى متكامل لربط قاعدة بيانات مايكروسوفت أكسس (MS Access) مع شات بوت Dialogflow باستخدام Flask و Ngrok، بالإضافة إلى نظام كامل لهجرة البيانات والمزامنة ثنائية الاتجاه مع قاعدة SQLite وملفات CSV النصية.

  تم تصميم هذا النظام خصيصاً لتمكين وكلاء البرمجة الذكية (مثل Cursor و Windsurf وغيرها) من قراءة الجداول، الاستعلام عنها، وتعديلها بسهولة كملفات نصية عادية، ومن ثم إعادة مزامنتها مع قاعدة بيانات أكسس الأصلية بضغطة زر.

  ---

  ## 🛠️ مكونات المشروع الهيكلية

  ```
  ├── app.py                      # خادم ويب Flask Webhook لـ Dialogflow
  ├── db_sync.py                  # أداة المزامنة ثنائية الاتجاه (Access ↔ SQLite & CSV)
  ├── University_System (1).accdb # قاعدة بيانات MS Access الأصلية (ثنائية مغلقة)
  ├── University_System.db        # قاعدة بيانات SQLite المحمولة (صديقة للـ AI)
  ├── University_System_Schema.md # الدليل التفصيلي لهيكل الجداول والعلاقات
  ├── db_csv/                     # المجلد النصي لملفات CSV المصدّرة للجداول
  │   ├── Students.csv
  │   ├── Courses.csv
  │   ├── Departments.csv
  │   └── ... (إجمالي 8 جداول)
  ```

  1. **الويبهوك خادم الويب (`app.py`)**: يستقبل طلبات Intent الخاصة بـ Dialogflow (مثل الاستعلام عن المعدل التراكمي GPA أو عنوان الطالب)، ويقوم بالاستعلام الفوري من قاعدة البيانات والرد باللغة العربية.
  2. **قاعدة بيانات SQLite (`University_System.db`)**: نسخة محمولة من قاعدة البيانات. يستطيع الـ Agent قراءتها وتعديلها باستخدام مكتبة بايثون الافتراضية `sqlite3` بدون الحاجة لمشغلات أكسس على ويندوز.
  3. **مجلد ملفات الـ CSV (`db_csv/`)**: يحتوي على جداول قاعدة البيانات كملفات نصية منفصلة لسهولة إظهار الفروق (Git Diffs) وتعديلها يدوياً.
  4. **سكريبت المزامنة (`db_sync.py`)**: الأداة الذكية المسؤولة عن تبادل وتحديث البيانات بين الجداول المختلفة لمنع تعارض المفاتيح وضمان التوافق.

  ---

  ## 🚀 التثبيت والتشغيل المحلي

  ### 1. المتطلبات الأساسية
  تأكد من تنصيب لغة بايثون وتثبيت برامج تشغيل MS Access على نظام التشغيل ويندوز، ثم قم بتثبيت المكاتب المطلوبة:
  ```bash
  pip install flask pyodbc
  ```

  ### 2. إعداد نفق Ngrok
  قم بتحميل Ngrok وتوثيق حسابك، ثم افتح نفقاً للمنفذ 5000:
  ```bash
  ngrok config add-authtoken "<YOUR_AUTHTOKEN>"
  ngrok http 5000
  ```
  قم بنسخ رابط الـ HTTPS العام المولد (مثال: `https://xxxx.ngrok-free.dev`).

  ### 3. تشغيل سيرفر Flask
  شغّل تطبيق الويب المحلي:
  ```bash
  python app.py
  ```

  ### 4. ربط الـ Webhook في Dialogflow
  1. افتح لوحة تحكم Dialogflow الخاصة بالبوت.
  2. اختر **Fulfillment** من القائمة اليسرى.
  3. قم بتفعيل خيار **Webhook** وضع رابط Ngrok مضافاً إليه `/webhook` (مثال: `https://xxxx.ngrok-free.dev/webhook`).
  4. اضغط على **Save** في أسفل الصفحة.

  ---

  ## 🔄 دليل تشغيل أداة المزامنة (`db_sync.py`)

  يمكنك إبقاء قواعد البيانات الثلاث متطابقة تماماً باستخدام الأوامر التالية من سطر الأوامر:

  ### أ) التصدير: من Access إلى SQLite و CSV
  إذا قمت بتعديل البيانات داخل برنامج MS Access وتريد تصديرها للـ CSV والـ SQLite:
  ```bash
  python db_sync.py export
  ```

  ### ب) الاستيراد: مزامنة SQLite إلى Access
  إذا قام الـ Agent بتعديل البيانات داخل قاعدة `University_System.db` وتريد حفظ التعديلات في ملف Access الأصلية:
  ```bash
  python db_sync.py import-sqlite
  ```

  ### ج) الاستيراد: مزامنة CSV إلى Access
  إذا قمت بتعديل محتويات أي ملف CSV داخل مجلد `db_csv/` وتريد حفظ التحديثات في ملف Access الأصلي:
  ```bash
  python db_sync.py import-csv
  ```

  ---

  ## 📊 بنية العلاقات وقواعد البيانات

  للاطلاع على شرح العلاقات الأكاديمية (مثل علاقة الأقسام مع الطلاب، وجدول المواعيد، وجدول التسجيل الوسيط) ومخطط العلاقات الكامل (ER Diagram)، يرجى زيارة مستند الدليل باللغة العربية [University_System_Schema.md](./University_System_Schema.md).

</details>

<br>

<!-- القسم الإنجليزي (مغلق افتراضياً لتقليل حجم الصفحة، ويمكن للمستخدم فتحه بضغطة زر) -->
<details id="english-version">
  <summary><b>🔽 Click here to show/hide English Guide (اضغط لإظهار/إخفاء الشرح بالإنجليزية)</b></summary>
  <br>

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

</details>
