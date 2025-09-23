from flask import Flask, render_template, request, redirect, jsonify

app = Flask(__name__)
todos = []

@app.route('/')
def index():
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add_todo():
    todo = request.form.get('todo')
    if todo:
        todos.append({'id': len(todos) + 1, 'text': todo, 'done': False})
    return redirect('/')

@app.route('/complete/<int:todo_id>')
def complete_todo(todo_id):
    for todo in todos:
        if todo['id'] == todo_id:
            todo['done'] = not todo['done']
            break
    return redirect('/')

@app.route('/delete/<int:todo_id>')
def delete_todo(todo_id):
    global todos 
    todos = [todo for todo in todos if todo['id'] != todo_id]
    return redirect('/')

@app.route('/api/todos', methods=['GET'])
def get_todos():
    return jsonify(todos)

@app.route('/edit/<int:todo_id>', methods=['GET', 'POST'])
def edit_todo(todo_id):
    todo = next((t for t in todos if t['id'] == todo_id), None)
    if request.method == 'POST':
        new_text = request.form.get('text')
        if todo and new_text:
            todo['text'] = new_text
        return redirect('/')
    return render_template('edit.html', todo=todo)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)