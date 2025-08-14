from flask import Flask, render_template, request, redirect, url_for, send_file, Response, make_response, send_from_directory, flash
import subprocess
import os
import re
import uuid
app = Flask(__name__)
FILES_FOLDER = os.path.dirname(__file__)
from flask import Flask, render_template, request, redirect, url_for, Response, send_file, render_template_string
from flask_caching import Cache
import subprocess
import threading
import queue
import re
import calls2
process = None
output_queue = queue.Queue()
process_lock = threading.Lock()
app.secret_key = ''
STUDENTS_FILE = "students.txt"
TEACHERS_FILE = "teachers.txt"
OUTPUT_FILE = "output.txt"
OUTPUTSCH_FILE = "outputsch.txt"
TEACHER_CLASS_LISTS_FILE = "teacher_class_lists.txt"
function_name = 'start'
loops = 10
#testing


# -------------------- File Helpers --------------------
from functools import wraps
from flask import session, redirect, url_for

@app.before_request
def ensure_user_id():
    user_id = request.cookies.get("user_id")
    if not user_id:
        new_id = str(uuid.uuid4())
        resp = make_response(redirect(request.url))
        resp.set_cookie("user_id", new_id)
        return resp

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def remove_blank_lines_from_file(file_path: str):
    """
    Reads a file, removes empty or whitespace-only lines,
    and writes the cleaned content back to the same file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Keep only lines that are not empty/whitespace-only
    cleaned_lines = [line for line in lines if line.strip()]

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)

def get_student_file():
    user_id = request.cookies.get("user_id")
    return os.path.join(fr"data\students_{user_id}.txt")

def get_teacher_file():
    user_id = request.cookies.get("user_id")
    return os.path.join(fr"data\teachers_{user_id}.txt")

def get_output_file():
    user_id = request.cookies.get("user_id")
    return os.path.join(fr"data\output_{user_id}.txt")

def get_outputsch_file():
    user_id = request.cookies.get("user_id")
    return os.path.join(fr"data\outputsch_{user_id}.txt")

def get_teacher_class_lists_file():
    user_id = request.cookies.get("user_id")
    return os.path.join(fr"data\teacher_class_lists_{user_id}.txt")

def read_students():
    students = []
    STUDENTS_FILE = get_student_file()
    if os.path.exists(STUDENTS_FILE):
        with open(STUDENTS_FILE) as f:
            for line in f:
                parts = line.strip().split(',')
                students.append(parts)
    return students

def write_students(students):
    STUDENTS_FILE = get_student_file()
    with open(STUDENTS_FILE, 'w') as f:
        for s in students:
            f.write(','.join(s) + '\n')

def read_teachers():
    TEACHERS_FILE = get_teacher_file()
    teachers = []
    if os.path.exists(TEACHERS_FILE):
        with open(TEACHERS_FILE) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # Split once on the first comma to separate teacher id
                tid, rest = line.split(',', 1)
                pairs = []
                # Now split rest by '),(' but first strip starting and ending parentheses
                # e.g. (math1,20),(math2,21) => math1,20  math2,21
                rest = rest.strip()
                if rest.startswith('(') and rest.endswith(')'):
                    rest = rest[1:-1]

                # split pairs safely:
                raw_pairs = rest.split('),(')
                for p in raw_pairs:
                    # now p should be like "math1,20"
                    if ',' not in p:
                        continue
                    subject, size = p.split(',', 1)
                    pairs.append([subject.strip(), size.strip()])

                teachers.append([tid.strip(), pairs])
    return teachers
def write_teachers(teachers):
    TEACHERS_FILE = get_teacher_file()
    with open(TEACHERS_FILE, 'w') as f:
        for t in teachers:
            tid = t[0]
            pairs = [f"({sub},{size})" for sub, size in t[1]]
            f.write(','.join([tid] + pairs) + '\n')

def run_script(script_filename='calls2.py'):
    global process
    with process_lock:
        process = subprocess.Popen(
            ['python', '-u', script_filename, function_name, loops],   # <- unbuffered output flag here
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    for line in process.stdout:
        output_queue.put(line)
    process.stdout.close()
    process.wait()
    output_queue.put(None)  # Signal done
# -------------------- Students Page --------------------
PASSWORD = ""  # change to your password

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            return "Wrong password", 401
    return '''
        <form method="post">
            <input type="password" name="password" placeholder="Password" required>
            <input type="submit" value="Login">
        </form>
    '''
@app.route('/download')
def download_page():
    user_id = request.cookies.get("user_id")
    files = [
        fr"data/output_{user_id}.txt",
        fr"data/outputsch_{user_id}.txt",
        fr"data/teacher_class_lists_{user_id}.txt",
        fr"data/students_{user_id}.txt",
        fr"data/teachers_{user_id}.txt"
    ]
    
    return render_template_string('''
        <h1>Your Download Links</h1>
        <p></p>
        <ul>
        {% for file in files %}
            <li><a href="/download/{{ file }}">{{ file }}</a></li>
        {% endfor %}
        </ul>
    ''', files=files)

@app.route('/download/<path:filename>')
def download_file(filename):
    user_id = request.cookies.get("user_id")
    allowed_files = {
        fr"data/output_{user_id}.txt",
        fr"data/outputsch_{user_id}.txt",
        fr"data/teacher_class_lists_{user_id}.txt",
        fr"data/students_{user_id}.txt",
        fr"data/teachers_{user_id}.txt"
    }
    if filename in allowed_files:
        return send_from_directory(FILES_FOLDER, filename, as_attachment=True)
    return "File not allowed", 403
    

@app.route('/students', methods=['GET', 'POST'])

def students():
    students = read_students()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'save':
            student_ids = request.form.getlist('student_id')
            num_subjects = len(students[0]) - 1 if students else 7
            new_students = []
            for sid in student_ids:
                subjects = []
                for i in range(num_subjects):
                    val = request.form.get(f'student_{sid}_subject_{i}', '')
                    subjects.append(val.strip())
                new_students.append([sid] + subjects)
            write_students(new_students)

        elif action == 'delete':
            del_id = request.form.get('delete_id')
            students = [s for s in students if s[0] != del_id]
            write_students(students)

        elif action == 'add':
            new_id = request.form.get('new_id').strip()
            new_subjects = [request.form.get(f'new_subject_{i}', '').strip() for i in range(7)]
            if new_id and all(new_subjects) and not any(s[0] == new_id for s in students):
                students.append([new_id] + new_subjects)
                # sort by numeric ID
                students.sort(key=lambda x: int(x[0]))
                write_students(students)

        return redirect(url_for('students'))

    return render_template('students.html', students=students)

# -------------------- Teachers Page --------------------
@app.route('/teachers', methods=['GET', 'POST'])

def teachers():
    teachers = read_teachers()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'save':
            teacher_ids = request.form.getlist('teacher_id')
            new_teachers = []
            for tid in teacher_ids:
                pairs = []
                i = 0
                while True:
                    subject = request.form.get(f'teacher_{tid}_subject_{i}')
                    size = request.form.get(f'teacher_{tid}_size_{i}')
                    if subject is None or size is None:
                        break
                    subject = subject.strip()
                    size = size.strip()
                    if subject and size:
                        pairs.append([subject, size])
                    i += 1
                new_teachers.append([tid, pairs])
            write_teachers(new_teachers)

        elif action == 'delete':
            del_id = request.form.get('delete_id')
            teachers = [t for t in teachers if t[0] != del_id]
            write_teachers(teachers)

        elif action == 'add':
            new_id = request.form.get('new_id').strip()
            pairs = []
            for i in range(10):
                subject = request.form.get(f'new_subject_{i}', '').strip()
                size = request.form.get(f'new_size_{i}', '').strip()
                if subject and size:
                    pairs.append([subject, size])
            if new_id and pairs and not any(t[0] == new_id for t in teachers):
                teachers.append([new_id, pairs])
                teachers.sort(key=lambda x: int(x[0]))
                write_teachers(teachers)

        return redirect(url_for('teachers'))

    return render_template('teachers.html', teachers=teachers)


# -------------------- Run Page --------------------
# @app.route('/run')
#make a button that when pressed will do call2.main(loops)
@app.route('/run', methods=['GET', 'POST'])
def run():
    if request.method == 'POST':
        loops = int(request.form.get('loops', 1))  # get loops from form, default 1
        result = calls2.start(loops, get_teacher_file(), get_student_file(),get_output_file(),get_outputsch_file(),get_teacher_class_lists_file())  # run your function
        # You can render result or just confirm success
        return render_template_string('''
            <h2>Function run with loops={{loops}}</h2>
            <p>Result: {{result}}</p>
            <a href="{{ url_for('run') }}">Go back</a>
        ''', loops=loops, result=result)
    # GET method: show the button and input for loops
    return render_template_string('''
        <form method="POST">
            <label for="loops">Number of loops:</label>
            <input type="number" id="loops" name="loops" value="1" min="1" max="100000" required oninput="updateETA()">
            <span id="eta">ETA: 0.5 seconds</span>
            <br><br>
            <button type="submit">Run</button>
            <br>
            <a href="{{ url_for('index') }}">Back to Main Page</a>
        </form>

        <script>
            function updateETA() {
                const loops = document.getElementById('loops').value;
                const eta = loops * 0.5; // seconds
                document.getElementById('eta').innerText = `ETA: ${eta} seconds. Note: The Webpage will load for about the ETA feel free to switch tabs just leave this tab open`;
            }
            updateETA(); // set initial value
        </script>
    ''')



@app.route('/run/start', methods=['POST'])
def run_start():
    global process
    with process_lock:
        if process is not None and process.poll() is None:
            # Already running, just redirect to running output
            return redirect(url_for('run', running=1))

    while not output_queue.empty():
        output_queue.get()

    threading.Thread(target=run_script, args=('calls2.py',), daemon=True).start()
    return redirect(url_for('run', running=1))


@app.route('/output_stream')

def output_stream():
    def generate():
        while True:
            line = output_queue.get()
            if line is None:
                break
            yield line
    return Response(generate(), mimetype='text/plain')

@app.route('/import', methods=['GET', 'POST'])
def import_page():
    if request.method == 'POST':
        file_type = request.form.get('file_type')  # 'students' or 'teachers'
        text_content = request.form.get('file_content')
        if file_type == 'students':
            with open(get_student_file(), 'w', encoding='utf-8') as f:
                f.write(text_content)
            remove_blank_lines_from_file(get_student_file())
        if file_type == 'teachers':
            with open(get_teacher_file(), 'w', encoding='utf-8') as f:
                f.write(text_content)
            remove_blank_lines_from_file(get_teacher_file())
            
        return redirect(url_for('import_page'))

    return render_template('import.html')

# -------------------- Downloads --------------------
@app.route('/download')

def download():
    return send_file(OUTPUT_FILE, as_attachment=True)

@app.route('/download_outputsch')

def download_outputsch():
    return send_file(OUTPUTSCH_FILE, as_attachment=True)

@app.route('/download_teacher_class_lists')

def download_teacher_class_lists():
    return send_file(TEACHER_CLASS_LISTS_FILE, as_attachment=True)

# -------------------- Home --------------------
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
