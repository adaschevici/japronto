import os.path
import sqlite3
from functools import partial
import sys
import json

sys.path.append(os.path.dirname(__file__) + '/../..')

from app import Application

DB_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'todo.sqlite'))
db_connect = partial(sqlite3.connect, DB_FILE)


def maybe_create_schema():
    db = db_connect()
    db.execute("""
        CREATE TABLE IF NOT EXISTS todos
        (id INTEGER PRIMARY KEY, todo TEXT)""")
    db.close()


def add_todo(request):
    db = db_connect()
    cur = db.cursor()
    todo = "mytodo"
    cur.execute("""INSERT INTO todos (todo) VALUES (?)""", (todo,))
    last_id = cur.lastrowid
    db.commit()
    db.close()

    return request.Response(
        text=json.dumps({"id": last_id, "todo": todo}),
        mime_type='application/json')


def list_todos(request):
    db = db_connect()
    cur = db.cursor()
    cur.execute("""SELECT id, todo FROM todos""")
    todos = [{"id": id, "todo": todo} for id, todo in cur]
    db.close()

    return request.Response(
        text=json.dumps({"results": todos}),
        mime_type='application/json'
    )


def show_todo(request):
    db = db_connect()
    cur = db.cursor()
    id = int(request.match_dict['id'])
    cur.execute("""SELECT id, todo FROM todos WHERE id = ?""", (id,))
    todo = cur.fetchone()
    if not todo:
        return request.Response(404, text="{}", mime_type='application/json')
    todo = {"id": todo[0], "todo": todo[1]}
    db.close()

    return request.Response(
        text=json.dumps(todo),
        mime_type='application/json'
    )


if __name__ == '__main__':
    maybe_create_schema()
    app = Application()
    router = app.get_router()
    router.add_route('/todos', list_todos, method='GET')
    router.add_route('/todos/{id}', show_todo, method='GET')
    router.add_route('/todos', add_todo, method='POST')
    app.serve()
