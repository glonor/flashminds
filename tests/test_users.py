import requests
from faker import Faker

fake = Faker()
base_url = 'http://localhost:5000'
user_id = fake.random_int(min=1, max=100000)
username = "test_user"

def test_create_user():
    create_user_url = f'{base_url}/users'

    # Create a user with the random user_id
    payload = {"user_id": user_id, "username": username}
    response = requests.post(create_user_url, json=payload)

    assert response.status_code == 201
    assert response.json()['message'] == 'User created successfully'

    # Try to create another user with the same user_id, expecting a conflict
    conflicting_payload = {"user_id": user_id, "username": "existing_user"}
    conflicting_response = requests.post(create_user_url, json=conflicting_payload)

    assert conflicting_response.status_code == 409
    assert conflicting_response.json()['message'] == 'User with the same user_id already exists'


def test_get_user():
    # Retrieve the created user
    get_user_url = f'{base_url}/users/{user_id}'
    get_response = requests.get(get_user_url)

    assert get_response.status_code == 200
    assert 'user' in get_response.json()

    retrieved_user = get_response.json()['user']
    assert retrieved_user['user_id'] == user_id
    assert retrieved_user['username'] == username

def test_get_user_not_found():
    # Attempt to retrieve a non-existent user
    non_existent_user_id = fake.random_int(min=1001, max=2000)
    get_user_url = f'{base_url}/users/{non_existent_user_id}'
    get_response = requests.get(get_user_url)

    assert get_response.status_code == 404
    assert 'message' in get_response.json()
    assert get_response.json()['message'] == 'User not found'

def test_update_user_success():
    # Update the created user
    update_user_url = f'{base_url}/users/{user_id}'
    updated_payload = {"username": "updated_username"}
    update_response = requests.put(update_user_url, json=updated_payload)

    assert update_response.status_code == 200
    assert update_response.json()['message'] == 'User updated successfully'

    # Retrieve the updated user and check if the username has changed
    get_user_url = f'{base_url}/users/{user_id}'
    get_response = requests.get(get_user_url)
    assert get_response.status_code == 200

    retrieved_user = get_response.json()['user']
    assert retrieved_user['username'] == "updated_username"

def test_update_user_missing_fields():
    update_user_url = f'{base_url}/users/{user_id}'
    updated_payload = {}  # Missing 'username' field
    update_response = requests.put(update_user_url, json=updated_payload)

    assert update_response.status_code == 400
    assert 'message' in update_response.json()
    assert update_response.json()['message'] == 'Missing required fields'

def test_update_user_not_found():
    non_existent_user_id = fake.random_int(min=2001, max=3000)
    update_user_url = f'{base_url}/users/{non_existent_user_id}'
    updated_payload = {"username": "updated_username"}
    update_response = requests.put(update_user_url, json=updated_payload)

    assert update_response.status_code == 404
    assert 'message' in update_response.json()
    assert update_response.json()['message'] == 'User not found'

def test_delete_user_success():
    # Delete the created user
    delete_user_url = f'{base_url}/users/{user_id}'
    delete_response = requests.delete(delete_user_url)

    assert delete_response.status_code == 200
    assert delete_response.json()['message'] == 'User deleted successfully'

    # Attempt to retrieve the deleted user and check for a not found response
    get_user_url = f'{base_url}/users/{user_id}'
    get_response = requests.get(get_user_url)
    assert get_response.status_code == 404
    assert 'message' in get_response.json()
    assert get_response.json()['message'] == 'User not found'

def test_delete_user_not_found():
    non_existent_user_id = fake.random_int(min=2001, max=3000)
    delete_user_url = f'{base_url}/users/{non_existent_user_id}'
    delete_response = requests.delete(delete_user_url)

    assert delete_response.status_code == 404
    assert 'message' in delete_response.json()
    assert delete_response.json()['message'] == 'User not found'

