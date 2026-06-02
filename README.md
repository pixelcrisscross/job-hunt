***

# Intelligent Candidate Skill Matching and Recruitment Analytics System
### Visvesvaraya Technological University (VTU) — Mini Project Report [1]
**Department of Computer Science and Engineering**  
**B.Tech in Artificial Intelligence and Data Science (2025 – 2026)** [1]

---

## 📌 Project Overview
Traditional recruitment systems rely heavily on manual resume screening, which is time-consuming, inconsistent, and error-prone [1, 9]. This project implements a high-performance, **3NF-normalized Multi-Page Application (MPA)** that automates candidate screening and ranking using database-driven techniques [1, 15, 17]. 

The system leverages **MySQL** [12, 13] for secure data storage and executes an intelligent skill-matching ranking query in **under 0.05 seconds** [15, 20, 24]. The application is powered by a **Python Flask** backend and features a modern, responsive user interface utilizing **HTML5, CSS3, Vanilla JS**, and **Chart.js** [14, 21].

---

## 🛠️ Tech Stack
*   **Backend Framework:** Python 3.x with Flask [14]
*   **Database Management System:** MySQL (with Foreign Key constraints, Indexes, and Triggers) [12, 13, 15, 17, 18, 20]
*   **Frontend Technologies:** HTML5, CSS3 (Modern Glassmorphism UI), Vanilla JavaScript [14]
*   **Data Visualization:** Chart.js (Real-time analytics integration) [21]
*   **Database Adapter:** `mysql-connector-python`

---

## 🚀 Key Features & Architecture

### 1. Role-Based Access Control (RBAC) [25]
The platform utilizes distinct portals depending on the authenticated user session [25]:
*   **System Administrator:** Gatekeeper dashboard. Approves or rejects incoming Recruiter registration requests, and monitors the real-time system database changes through audit logs [21, 25].
*   **Corporate Recruiter:** Command center to post job openings, select targeted tech stacks, evaluate matches, and analyze candidate skill inventory graphs [21, 25].
*   **Candidate:** Portfolio manager where candidates can update their details, qualification, experience, and select their current skills.

### 2. Database Normalization (Third Normal Form - 3NF) [1, 17]
*   **1NF:** All attributes represent atomic values [17]. Many-to-many relationships (e.g., Candidates and Skills) are resolved using junction bridge tables (`CandidateSkills` and `RequirementSkills`) instead of flat comma-separated fields [15, 16, 17].
*   **2NF:** No partial dependencies on composite primary keys [17].
*   **3NF:** Non-key attributes are fully dependent only on the primary key, eliminating transitive dependencies [17].

### 3. Database Triggers & Audit Logging [17, 18, 20]
An active `AFTER UPDATE` database trigger is bound to the `Candidates` table. Whenever a candidate's profile is updated, the trigger automatically captures the delta changes and writes an entry to the `CandidateAuditLog` table for data compliance [17, 18, 20].

### 4. High-Performance SQL Ranking Query [19, 20]
The core matching engine relies on a clean, optimized SQL query utilizing `INNER JOIN` and aggregate count operations to calculate candidate-to-job matching scores instantly:
```sql
SELECT c.candidate_id, c.name, c.email, c.qualification, c.experience,
       COUNT(cs.skill_id) AS rank_score
FROM Candidates c
INNER JOIN CandidateSkills cs ON c.candidate_id = cs.candidate_id
INNER JOIN RequirementSkills rs ON cs.skill_id = rs.skill_id
WHERE rs.requirement_id = %s
GROUP BY c.candidate_id, c.name, c.email, c.qualification, c.experience
ORDER BY rank_score DESC, c.experience DESC;
```

---

## 💻 Step-by-Step Installation & Setup

### 1. Prerequisites
Ensure you have the following installed on your local machine:
*   [Python 3.8+](https://www.python.org/downloads/)
*   [MySQL Server](https://dev.mysql.com/downloads/installer/)

### 2. Setup the Codebase
Clone or download the project files and arrange them in the following directory tree:
```text
recruitment-system/
│
├── schema.sql           # Database structures & seed data
├── app.py               # Flask application server
└── templates/           # Frontend pages
    ├── login.html
    ├── register.html
    ├── admin_dashboard.html
    ├── recruiter_dashboard.html
    └── candidate_dashboard.html
```

### 3. Create the Database
Open your MySQL Command Line Client, Terminal, or Workbench and run the following command to load the schema [12, 13]:
```sql
CREATE DATABASE recruitment_db;
USE recruitment_db;
```
Now, import and source your `schema.sql` file [12, 13]:
```sql
SOURCE /path/to/your/schema.sql;
```

### 4. Install Dependencies
Run the command below to install Python packages:
```bash
pip install flask mysql-connector-python
```

### 5. Configure Database Credentials
Open `app.py` in your editor and update the MySQL connection credentials to match your local setup:
```python
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_LOCAL_MYSQL_PASSWORD', -- Replace with your actual password
    'database': 'recruitment_db'
}
```

### 6. Run the Application [14]
Launch the development server [14]:
```bash
python app.py
```
Open your browser and navigate to **`http://127.0.0.1:5000`** [14].

---

## 🔄 User Workflow Guide (For Presentation & Demos)

Follow these steps to demonstrate the full capabilities of the system during an evaluation:

```text
 [ Admin Logs In ] 
        │
        ▼
 [ Candidate Registers ] ──► Auto-Approved ──► Update Portfolio & Select Skills
        │
        ▼
 [ Recruiter Registers ] ──► Blocked (Pending)
        │
        ▼
 [ Admin Dashboard ] ─────► Approve Recruiter ──► Recruiter Allowed to Log In
        │
        ▼
 [ Recruiter Dashboard ] ──► Post Job & Skills ──► Query Skill Matcher Rankings
```

1.  **Administrative Checkpoint (Admin Login):**
    *   Go to `/login` and sign in with the system administrator credentials:
        *   **Username:** `admin`
        *   **Password:** `admin123`
    *   This logs you into the **Admin Panel** where you can monitor audit history and manage authorization requests [21, 25].

2.  **Candidate Journey (Register & Sync Profile):**
    *   Go to `/register`, create an account with the role set to **Candidate**. Candidates are auto-approved.
    *   Log in as the Candidate to access the **Talent Portal**. Fill out phone details, highest qualification, years of work experience, and check off skills [21, 25].
    *   Click **Update Portfolio**.

3.  **Recruiter Onboarding (Pending Approval Gate):**
    *   Go to `/register` and sign up as a **Recruiter**.
    *   Attempt to log in immediately. The system will prevent access with a warning: *"Your account is pending Admin approval."*

4.  **Admin Verification:**
    *   Log back in as `admin`.
    *   Locate the newly registered recruiter under **Pending Registrations Approval Requests** and click **Approve** [25].

5.  **Recruitment Operations (Analytics & Matching Engine):**
    *   Log in as the newly approved Recruiter.
    *   **Post Job Requirement:** Go to the *Post Job* tab. Create a new job requirement (e.g., "Python Developer") and check off required skills (e.g., Python, SQL, Flask) [20, 21].
    *   **Evaluate Skill Rankings:** Navigate to the *Intel-Skill Matcher* tab [20, 21]. Select your posted job opening from the dropdown. The system will instantly calculate match ratios and rank candidates based on matching skills [19, 20].

---

## 👥 Project Team & Guidance [1]
*   **Under the Guidance of:** Prof. Laxmi Desai (Assistant Professor, Department of CSE, VTU, Belagavi) [1]
*   **Submitted By:** [1]
    1.  PIYUSH S ANNIGERI (USN: 2VX24AD065) [1]
    2.  KULVENDAR SINGH RAJPUT (USN: 2VX24AD043) [1]
    3.  MANOJ (USN: 2VX24AD051) [1]
    4.  AKASH (USN: 2VX24AD010) [1]
