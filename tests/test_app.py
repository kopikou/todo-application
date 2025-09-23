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