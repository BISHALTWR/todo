from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('tasks', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    tasks = db.execute(
        'SELECT t.id, t.created, t.title, t.body, t.category, t.completed FROM tasks t '
        'JOIN user u ON t.user_id = u.id '
        'WHERE t.user_id = ? '
        'ORDER BY t.created ASC',
        (g.user['id'],)
    ).fetchall()
    return render_template('task/index.html', tasks=tasks)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        category = request.form['category']
        error = None

        if not title:
            error = 'Title is required.'
        if not category:
            error = 'Category is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO tasks (title, body, category, user_id)'
                ' VALUES (?, ?, ?, ?)',
                (title, body, category, g.user['id'])
            )
            db.commit()
            return redirect(url_for('tasks.index'))

    return render_template('task/create.html')

def get_task(id, check_user=True):
    task = get_db().execute(
        'SELECT t.id, title, body, t.category, created, user_id, username'
        ' FROM tasks t JOIN user u ON t.user_id = u.id'
        ' WHERE t.id = ?',
        (id,)
    ).fetchone()

    if task is None:
        abort(404, f"Task id {id} doesn't exist.")

    if check_user and task['user_id'] != g.user['id']:
        abort(403)

    return task

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    task = get_task(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        category = request.form['category']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE tasks SET title = ?, body = ?, category = ?'
                ' WHERE id = ?',
                (title, body,category, id)
            )
            db.commit()
            return redirect(url_for('tasks.index'))

    return render_template('task/update.html', task=task)

@bp.route('/<int:id>/update_completed', methods=['POST'])
@login_required
def update_completed(id):
    completed = request.get_json()['completed']
    db = get_db()
    db.execute(
        'UPDATE tasks SET completed = ? WHERE id = ?',
        (completed, id)
    )
    db.commit()
    return '', 204

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_task(id)
    db = get_db()
    db.execute('DELETE FROM tasks WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('tasks.index'))

