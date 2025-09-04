from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('task', __name__, url_prefix='/task')

@bp.route('/')
@login_required
def index():
    db = get_db()
    tasks = db.execute(
        'SELECT * FROM task WHERE author_id = ?', (g.user['id'],)
    ).fetchall()

    return render_template('task/index.html', tasks=tasks)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Titulo e obrigatorio'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO task (title, body, author_id, finished)'
                ' VALUES (?, ?, ?, FALSE)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('task.index'))
        
    return render_template('task/create.html')

def get_task(id, check_author = True):
    task = get_db().execute(
        'SELECT t.id, title, body, created, author_id, username'
        ' FROM task t JOIN user u ON t.author_id = u.id'
        ' WHERE t.id = ?',
        (id,)
    ).fetchone()

    if task is None:
        abort(404, f"Tarefa do id {id} não existe.")
    
    if check_author and task['author_id'] != g.user['id']:
        abort(403)
    
    return task

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    task = get_task(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Titulo e obrigatorio.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE task SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('task.index'))
    
    return render_template('task/update.html', task=task)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_task(id)
    db = get_db()
    db.execute('DELETE FROM task WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('task.index'))