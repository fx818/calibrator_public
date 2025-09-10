# 📜 Certificate Approval Dashboard

This project is an **end-to-end workflow automation system** that:

1. Fetches **vendor emails with PDF attachments** from Gmail.
2. Extracts **certificate information** from those PDFs.
3. Pushes the extracted data into a **database**.
4. Waits for **user approval** via dashboard.
5. On approval, pushes approved data to a **calendar**.

The system is built with:

* **FastAPI** (backend API).
* **LangGraph** (state machine for workflow).
* **Frontend Dashboard** (HTML + JS).
* **Gmail API integration** for fetching attachments.

---

## 🚀 Features

### 1. **Frontend Dashboard**

A clean and modern UI for managing the certificate extraction workflow.

* **API Health Check**

  * Shows whether the backend API is running (online/offline).

* **Vendor Email Input**

  * User enters the vendor email address (mandatory).
  * Ensures extraction is only run for specific vendors.

* **Extract Certificates Button**

  * Starts the workflow by calling `/extract_certificates`.
  * Displays extracted certificates in a grid format.

* **Approval Panel**

  * Appears if workflow pauses for approval.
  * User can approve ✅ or reject ❌ extraction results.

* **Finalize Button**

  * Each certificate has a **Finalize Approval** option.
  * Calls `/after_approval` to mark it as processed.

* **Toast Notifications**

  * Success, error, and status messages appear at the top-right corner.

* **Loading Overlay**

  * Blocks the screen with a spinner while processing requests.

---

### 2. **Backend Workflow (LangGraph)**

The workflow is modeled as a **state graph** using `langgraph`.
Each node represents a step in the pipeline.

#### Workflow Steps:

1. **Gmail File Node**

   * Fetches emails with attachments from the specified `vendor_email`.
   * Extracts PDF file paths.

2. **Certificate Data Extraction**

   * Reads PDF files → extracts text → parses certificate information.
   * Normalizes into structured JSON:

     ```json
     {
       "certificate_number": "12345",
       "status": "pending"
     }
     ```

3. **Push Data to Database**

   * Stores extracted certificates into DB.

4. **User Approval (Pause)**

   * Workflow pauses and waits for user approval via frontend.
   * Uses `interrupt()` from LangGraph.

5. **Push to Calendar**

   * If approved, updates the system (e.g., pushes to calendar).
   * Marks certificates as finalized.

---

### 3. **API Endpoints**

#### `POST /extract_certificates`

Starts the workflow.

**Request (JSON Body):**

```json
{
  "vendor_email": "vendor@example.com"
}
```

**Response Example:**

```json
{
  "status": "Waiting",
  "message": "Waiting for user approval...",
  "certificates": [
    { "certificate_number": "12345", "status": "pending" }
  ]
}
```

---

#### `POST /approval?user_input=yes|no`

Handles user approval from frontend.

**Example:**

```
POST http://127.0.0.1:8000/approval?user_input=yes
```

**Response:**

```json
{
  "status": "Approved",
  "message": "Certificates approved by user"
}
```

---

#### `POST /after_approval?certificate_number=12345`

Finalizes approval for a specific certificate.

**Example:**

```
POST http://127.0.0.1:8000/after_approval?certificate_number=12345
```

**Response:**

```json
{
  "status": "Finalized",
  "message": "Certificate 12345 pushed to calendar"
}
```

---

### 4. **State Graph Diagram**

```
START → gmail_file_node → certificate_data → push_data_to_db → user_approval → push_to_calendar → END
```

* `user_approval` pauses the graph until the user provides input.

---

### 5. **How to Run**

#### Backend

1. Clone repo and install dependencies:

   ```bash
   pip install fastapi uvicorn langgraph python-dotenv
   ```
2. Run FastAPI server:

   ```bash
   uvicorn main:app --reload
   ```
3. Backend runs at `http://127.0.0.1:8000`.

#### Frontend

* Open the provided `index.html` in browser.
* Enter vendor email → Click **Extract Certificates**.

#### Postman Testing

* Start extraction:

  ```http
  POST http://127.0.0.1:8000/extract_certificates
  Body: { "vendor_email": "vendor@example.com" }
  ```
* Approve certificates:

  ```http
  POST http://127.0.0.1:8000/approval?user_input=yes
  ```
* Finalize certificate:

  ```http
  POST http://127.0.0.1:8000/after_approval?certificate_number=12345
  ```

---

### 6. **Future Improvements**

* Add user authentication.
* Support multiple vendors at once.
* Automate calendar push with Google Calendar API.
* Advanced error handling and retry mechanisms.
