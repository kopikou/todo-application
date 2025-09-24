import pytest
from app import app

@pytest.fixture
def client():
    # Очищаем задачи перед каждым тестом
    from app import todos
    todos.clear()
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Тест главной страницы"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'To-Do List' in response.data

def test_add_todo(client):
    """Тест добавления задачи"""
    # Добавляем задачу
    response = client.post('/add', data={'todo': 'Test task'})
    assert response.status_code == 302  # Redirect
    
    # Проверяем, что задача добавилась
    response = client.get('/api/todos')
    todos = response.get_json()
    assert len(todos) == 1
    assert todos[0]['text'] == 'Test task'
    assert todos[0]['done'] == False

def test_add_empty_todo(client):
    """Тест добавления пустой задачи"""
    response = client.get('/api/todos')
    todos = response.get_json()
    initial_count = len(todos)
    response = client.post('/add', data={'todo': ''})
    assert response.status_code == 302
    response = client.get('/api/todos')
    todos = response.get_json()
    assert len(todos) == initial_count

def test_complete_todo(client):
    """Тест отметки задачи как выполненной"""
    # Добавляем задачу
    client.post('/add', data={'todo': 'Test task'})
    response = client.get('/api/todos')
    todos = response.get_json()
    todo_id = todos[0]['id']
    
    # Отмечаем как выполненную
    response = client.get(f'/complete/{todo_id}')
    assert response.status_code == 302
    response = client.get('/api/todos')
    todos = response.get_json()
    assert todos[0]['done'] == True
    
    # Снова отмечаем - должно снять отметку
    response = client.get(f'/complete/{todo_id}')
    assert response.status_code == 302
    response = client.get('/api/todos')
    todos = response.get_json()
    assert todos[0]['done'] == False

def test_delete_todo(client):
    """Тест удаления задачи"""
    # Добавляем несколько задач
    client.post('/add', data={'todo': 'Task 1'})
    client.post('/add', data={'todo': 'Task 2'})
    
    response = client.get('/api/todos')
    todos = response.get_json()
    initial_count = len(todos)
    todo_id = todos[0]['id']
    
    # Удаляем первую задачу
    response = client.get(f'/delete/{todo_id}')
    assert response.status_code == 302
    response = client.get('/api/todos')
    todos = response.get_json()
    assert len(todos) == initial_count - 1
    
    # Проверяем, что правильная задача удалена
    remaining_tasks = [todo['text'] for todo in todos]
    assert 'Task 1' not in remaining_tasks
    assert 'Task 2' in remaining_tasks

def test_get_todos_api(client):
    """Тест API получения todos"""
    # Добавляем задачи
    client.post('/add', data={'todo': 'API Task 1'})
    client.post('/add', data={'todo': 'API Task 2'})
    
    response = client.get('/api/todos')
    assert response.status_code == 200
    
    data = response.get_json()
    assert len(data) == 2
    assert data[0]['text'] == 'API Task 1'
    assert data[1]['text'] == 'API Task 2'

def test_edit_todo_get(client):
    client.post('/add', data={'todo': 'Test task to edit'})
    response = client.get('/edit/1')
    
    assert response.status_code == 200
    assert b'Edit Task' in response.data
    assert b'Test task to edit' in response.data
    assert b'Save' in response.data

def test_edit_todo_post(client):
    client.post('/add', data={'todo': 'Original task'})

    response = client.post('/edit/1', data={'text': 'Updated task'})

    assert response.status_code == 302
    
    response = client.get('/api/todos')
    tasks = response.get_json()
    assert tasks[0]['text'] == 'Updated task'

def test_search_functionality(client):
    """Тестирование поиска задач"""
    test_tasks = ['Buy groceries', 'Write report', 'Call mom']
    for task in test_tasks:
        client.post('/add', data={'todo': task})
    
    # Тест поиска существующей задачи
    response = client.get('/?search=groceries')
    assert b'Buy groceries' in response.data
    assert b'Write report' not in response.data
    
    # Тест поиска несуществующей задачи
    response = client.get('/?search=nonexistent')
    assert b'No tasks found' in response.data

def test_filter_functionality(client):
    """Тестирование фильтрации по статусу"""
    client.post('/add', data={'todo': 'FilterTestTask1'})
    client.post('/add', data={'todo': 'FilterTestTask2'}) 
    client.post('/add', data={'todo': 'FilterTestTask3'})
    
    response = client.get('/api/todos')
    tasks = response.get_json()
    assert len(tasks) == 3
    
    response = client.get('/complete/1')
    assert response.status_code == 302

    response = client.get('/api/todos')
    tasks = response.get_json()

    task1 = next((task for task in tasks if task['id'] == 1), None)
    task2 = next((task for task in tasks if task['id'] == 2), None)
    task3 = next((task for task in tasks if task['id'] == 3), None)
    
    assert task1 is not None and task1['done'] == True
    assert task2 is not None and task2['done'] == False
    assert task3 is not None and task3['done'] == False

    # Тест 1: Фильтр "Все" - должны видеть все 3 задачи
    response = client.get('/?filter=all')
    content = response.data.decode('utf-8')
    assert 'FilterTestTask1' in content
    assert 'FilterTestTask2' in content  
    assert 'FilterTestTask3' in content

    # Тест 2: Фильтр "Активные" - должны видеть только невыполненные задачи
    response = client.get('/?filter=active')
    content = response.data.decode('utf-8')
    
    assert 'FilterTestTask1' not in content
    assert 'FilterTestTask2' in content
    assert 'FilterTestTask3' in content

    # Тест 3: Фильтр "Выполненные" - должны видеть только выполненные задачи
    response = client.get('/?filter=completed')
    content = response.data.decode('utf-8')
    assert 'FilterTestTask1' in content
    assert 'FilterTestTask2' not in content
    assert 'FilterTestTask3' not in content