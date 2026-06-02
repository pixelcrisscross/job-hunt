from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super_secret_session_encryption_key_vtu'

db_config = {
    'host': 'localhost',
    'user': 'root',
    'database': 'recruitment_db'
}

def get_db():
    return mysql.connector.connect(**db_config)

# Auto-seed default Admin on startup if missing
def seed_admin_and_data():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Users WHERE username = 'admin'")
    if not cursor.fetchone():
        hashed_pw = generate_password_hash('admin123')
        cursor.execute(
            "INSERT INTO Users (username, email, password_hash, role, is_approved) VALUES (%s, %s, %s, %s, %s)",
            ('admin', 'admin@vtu.edu', hashed_pw, 'admin', True)
        )
        db.commit()
    cursor.close()
    db.close()

# Authentication Wrappers (Security Decorators)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def roles_allowed(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('role') not in roles:
                flash('Unauthorized Access!', 'error')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- ROUTING LOGIC ---

@app.route('/')
def index():
    if 'user_id' in session:
        role = session['role']
        return redirect(url_for(f'{role}_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user and check_password_hash(user['password_hash'], password):
            if not user['is_approved']:
                flash('Your account is pending Admin approval.', 'error')
                return render_template('login.html')
            
            # Set Session
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            return redirect(url_for(f'{user["role"]}_dashboard'))
        else:
            flash('Invalid Username or Password.', 'error')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        hashed_pw = generate_password_hash(password)
        # Admins and Candidates are auto-approved, recruiters must wait
        is_approved = True if role in ['admin', 'candidate'] else False
        
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO Users (username, email, password_hash, role, is_approved) VALUES (%s, %s, %s, %s, %s)",
                (username, email, hashed_pw, role, is_approved)
            )
            user_id = cursor.lastrowid
            
            # If Candidate, create a profile skeleton
            if role == 'candidate':
                cursor.execute(
                    "INSERT INTO Candidates (user_id, name, email) VALUES (%s, %s, %s)",
                    (user_id, username.replace('_', ' ').title(), email)
                )
            
            db.commit()
            if is_approved:
                flash('Registration Successful! You can now log in.', 'success')
            else:
                flash('Registration Successful! Pending Administrator approval.', 'warning')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f'Error: Account already exists or data invalid.', 'error')
        finally:
            cursor.close()
            db.close()
            
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Successfully logged out.', 'success')
    return redirect(url_for('login'))


# --- 1. ADMIN DASHBOARD ---
@app.route('/admin')
@login_required
@roles_allowed('admin')
def admin_dashboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Fetch Pending Approvals
    cursor.execute("SELECT user_id, username, email, role, created_at FROM Users WHERE is_approved = FALSE")
    pending = cursor.fetchall()
    
    # Fetch Active Users
    cursor.execute("SELECT user_id, username, email, role, is_approved FROM Users WHERE role != 'admin'")
    all_users = cursor.fetchall()

    # Fetch System Audit Log
    cursor.execute("SELECT * FROM CandidateAuditLog ORDER BY changed_at DESC LIMIT 10")
    audit_logs = cursor.fetchall()
    
    cursor.close()
    db.close()
    return render_template('admin_dashboard.html', pending=pending, all_users=all_users, audit_logs=audit_logs)

@app.route('/admin/approve/<int:uid>', methods=['POST'])
@login_required
@roles_allowed('admin')
def approve_user(uid):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE Users SET is_approved = TRUE WHERE user_id = %s", (uid,))
    db.commit()
    cursor.close()
    db.close()
    flash('User profile approved successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject/<int:uid>', methods=['POST'])
@login_required
@roles_allowed('admin')
def reject_user(uid):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Users WHERE user_id = %s", (uid,))
    db.commit()
    cursor.close()
    db.close()
    flash('Registration rejected/deleted.', 'warning')
    return redirect(url_for('admin_dashboard'))


# --- 2. RECRUITER DASHBOARD ---
@app.route('/recruiter')
@login_required
@roles_allowed('recruiter', 'admin')
def recruiter_dashboard():
    return render_template('recruiter_dashboard.html')


# --- 3. CANDIDATE DASHBOARD ---
@app.route('/candidate')
@login_required
@roles_allowed('candidate')
def candidate_dashboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Fetch Candidate Profile Info
    cursor.execute("SELECT * FROM Candidates WHERE user_id = %s", (session['user_id'],))
    candidate = cursor.fetchone()
    
    # Fetch all skills
    cursor.execute("SELECT * FROM Skills ORDER BY skill_name")
    all_skills = cursor.fetchall()
    
    # Fetch mapped candidate skills
    candidate_skills = []
    if candidate:
        cursor.execute("SELECT skill_id FROM CandidateSkills WHERE candidate_id = %s", (candidate['candidate_id'],))
        candidate_skills = [row['skill_id'] for row in cursor.fetchall()]
        
    cursor.close()
    db.close()
    return render_template('candidate_dashboard.html', candidate=candidate, all_skills=all_skills, mapped_skills=candidate_skills)

@app.route('/candidate/update', methods=['POST'])
@login_required
@roles_allowed('candidate')
def update_profile():
    name = request.form['name']
    phone = request.form['phone']
    qualification = request.form['qualification']
    experience = float(request.form['experience'])
    selected_skills = request.form.getlist('skills')

    db = get_db()
    cursor = db.cursor()
    try:
        # Get candidate record id
        cursor.execute("SELECT candidate_id FROM Candidates WHERE user_id = %s", (session['user_id'],))
        candidate_id = cursor.fetchone()[0]
        
        # Update Profile
        cursor.execute(
            "UPDATE Candidates SET name=%s, phone=%s, qualification=%s, experience=%s WHERE candidate_id=%s",
            (name, phone, qualification, experience, candidate_id)
        )
        
        # Sync Skills mappings
        cursor.execute("DELETE FROM CandidateSkills WHERE candidate_id = %s", (candidate_id,))
        for skill_id in selected_skills:
            cursor.execute("INSERT INTO CandidateSkills (candidate_id, skill_id) VALUES (%s, %s)", (candidate_id, int(skill_id)))
            
        db.commit()
        flash('Profile updated successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error: {str(e)}', 'error')
    finally:
        cursor.close()
        db.close()
    return redirect(url_for('candidate_dashboard'))


# --- SHARED API ENDPOINTS ---
@app.route('/api/skills')
def api_skills():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Skills")
    res = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(res)

@app.route('/api/requirements', methods=['GET', 'POST'])
@login_required
@roles_allowed('recruiter', 'admin')
def api_requirements():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        data = request.json
        cursor.execute("INSERT INTO JobRequirements (title, description, created_by) VALUES (%s, %s, %s)",
                       (data['title'], data['description'], session['user_id']))
        req_id = cursor.lastrowid
        for skill_id in data['skills']:
            cursor.execute("INSERT INTO RequirementSkills (requirement_id, skill_id) VALUES (%s, %s)", (req_id, skill_id))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({"message": "Successfully posted"}), 201
    else:
        cursor.execute("SELECT * FROM JobRequirements ORDER BY requirement_id DESC")
        reqs = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(reqs)

@app.route('/api/candidates', methods=['GET', 'POST'])
@login_required
@roles_allowed('recruiter', 'admin')
def api_candidates():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        data = request.json
        try:
            cursor.execute("INSERT INTO Candidates (name, email, phone, qualification, experience) VALUES (%s, %s, %s, %s, %s)",
                           (data['name'], data['email'], data['phone'], data['qualification'], data['experience']))
            cid = cursor.lastrowid
            for skill_id in data['skills']:
                cursor.execute("INSERT INTO CandidateSkills (candidate_id, skill_id) VALUES (%s, %s)", (cid, skill_id))
            db.commit()
            return jsonify({"message": "Added"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        finally:
            cursor.close()
            db.close()
    else:
        cursor.execute("SELECT * FROM Candidates")
        cands = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(cands)

@app.route('/api/rank/<int:req_id>')
@login_required
@roles_allowed('recruiter', 'admin')
def api_rank(req_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    query = """
        SELECT c.candidate_id, c.name, c.email, c.qualification, c.experience,
               COUNT(cs.skill_id) AS rank_score
        FROM Candidates c
        INNER JOIN CandidateSkills cs ON c.candidate_id = cs.candidate_id
        INNER JOIN RequirementSkills rs ON cs.skill_id = rs.skill_id
        WHERE rs.requirement_id = %s
        GROUP BY c.candidate_id, c.name, c.email, c.qualification, c.experience
        ORDER BY rank_score DESC, c.experience DESC;
    """
    
    cursor.execute("SELECT COUNT(*) as total_required FROM RequirementSkills WHERE requirement_id = %s", (req_id,))
    total_required = cursor.fetchone()['total_required']
    cursor.execute(query, (req_id,))
    rankings = cursor.fetchall()
    
    cursor.close()
    db.close()
    return jsonify({"total_required": total_required, "candidates": rankings})

@app.route('/api/analytics')
@login_required
@roles_allowed('recruiter', 'admin')
def api_analytics():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as count FROM Candidates")
    c_count = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM JobRequirements")
    j_count = cursor.fetchone()['count']
    cursor.execute("""
        SELECT s.skill_name, COUNT(cs.candidate_id) as candidate_count
        FROM Skills s
        LEFT JOIN CandidateSkills cs ON s.skill_id = cs.skill_id
        GROUP BY s.skill_id, s.skill_name
        ORDER BY candidate_count DESC
    """)
    chart_data = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify({"total_candidates": c_count, "total_jobs": j_count, "chart_data": chart_data})


if __name__ == '__main__':
    seed_admin_and_data()
    app.run(debug=True, port=5000)