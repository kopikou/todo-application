from flask import Flask, render_template, request, redirect, jsonify

app = Flask(__name__)
todos = []

@app.route('/')
def index():
    # Получаем параметры фильтрации из URL
    search_query = request.args.get('search', '')
    filter_status = request.args.get('filter', 'all')  # all, active, completed
    
    filtered_todos = todos.copy()
    
    if search_query:
        filtered_todos = [todo for todo in filtered_todos 
                         if search_query.lower() in todo['text'].lower()]
    
    # Фильтрация по статусу
    if filter_status == 'active':
        filtered_todos = [todo for todo in filtered_todos if not todo['done']]
    elif filter_status == 'completed':
        filtered_todos = [todo for todo in filtered_todos if todo['done']]
    
    return render_template('index.html', 
                         todos=filtered_todos,
                         all_todos=todos,  # Все задачи для статистики
                         search_query=search_query,
                         filter_status=filter_status)

@app.route('/add', methods=['POST'])
def add_todo():
    todo_text = request.form.get('todo')
    if todo_text:
        todos.append({
            'id': len(todos) + 1, 
            'text': todo_text, 
            'done': False
        })
    return redirect('/')

@app.route('/complete/<int:todo_id>')
def complete_todo(todo_id):
    for todo in todos:
        if todo['id'] == todo_id:
            todo['done'] = not todo['done']
            break
    
    search_query = request.args.get('search', '')
    filter_status = request.args.get('filter', 'all')
    return redirect(f'/?search={search_query}&filter={filter_status}')

@app.route('/delete/<int:todo_id>')
def delete_todo(todo_id):
    global todos 
    todos = [todo for todo in todos if todo['id'] != todo_id]
    
    search_query = request.args.get('search', '')
    filter_status = request.args.get('filter', 'all')
    return redirect(f'/?search={search_query}&filter={filter_status}')

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
        
        search_query = request.args.get('search', '')
        filter_status = request.args.get('filter', 'all')
        return redirect(f'/?search={search_query}&filter={filter_status}')
    
    return render_template('edit.html', todo=todo)

@app.route('/clear_search')
def clear_search():
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)