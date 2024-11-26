from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database initialization
DATABASE = 'crud_app.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    # Search and pagination
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 5
    offset = (page - 1) * per_page

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    if search_query:
        c.execute('SELECT COUNT(*) FROM tasks WHERE title LIKE ?', (f'%{search_query}%',))
        total = c.fetchone()[0]
        c.execute('SELECT * FROM tasks WHERE title LIKE ? LIMIT ? OFFSET ?', 
                  (f'%{search_query}%', per_page, offset))
    else:
        c.execute('SELECT COUNT(*) FROM tasks')
        total = c.fetchone()[0]
        c.execute('SELECT * FROM tasks LIMIT ? OFFSET ?', (per_page, offset))
    tasks = c.fetchall()
    conn.close()

    return render_template('index.html', tasks=tasks, search_query=search_query, 
                           page=page, total_pages=(total // per_page) + 1)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form['title']
    description = request.form['description']
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('INSERT INTO tasks (title, description) VALUES (?, ?)', (title, description))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>')
def edit_task(id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM tasks WHERE id = ?', (id,))
    task = c.fetchone()
    conn.close()
    return render_template('edit.html', task=task)

@app.route('/update/<int:id>', methods=['POST'])
def update_task(id):
    title = request.form['title']
    description = request.form['description']
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('UPDATE tasks SET title = ?, description = ? WHERE id = ?', (title, description, id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_task(id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)