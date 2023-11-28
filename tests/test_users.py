import requests
from faker import Faker

fake = Faker()
base_url = 'http://localhost:5000'

def create_test_user():
    user_id = fake.random_int(min=1, max=100000)
    username = "test_user"
    create_user_url = f'{base_url}/users'
    user_payload = {"user_id": user_id, "username": username}
    create_user_response = requests.post(create_user_url, json=user_payload)
    assert create_user_response.status_code == 201

    return user_id

def delete_test_user(user_id):
    delete_user_url = f'{base_url}/users/{user_id}'
    delete_user_response = requests.delete(delete_user_url)
    assert delete_user_response.status_code == 200

def test_create_user_success():
    # Create a user for testing
    user_id = create_test_user()

    # Delete the created user to make the test idempotent
    delete_test_user(user_id)

def test_create_user_conflict():
    # Create a user for testing
    user_id = create_test_user()

    # Try to create another user with the same user_id, expecting a conflict
    create_user_url = f'{base_url}/users'
    conflicting_payload = {"user_id": user_id, "username": "existing_user"}
    conflicting_response = requests.post(create_user_url, json=conflicting_payload)

    # Check if the expected conflict response is received
    assert conflicting_response.status_code == 409
    assert conflicting_response.json()['message'] == 'User with the same user_id already exists'

    # Delete the created user to make the test idempotent
    delete_user_url = f'{base_url}/users/{user_id}'
    delete_user_response = requests.delete(delete_user_url)
    assert delete_user_response.status_code == 200


def test_get_user():
    # Create a user for testing
    user_id = create_test_user()

    # Retrieve the created use
    get_user_url = f'{base_url}/users/{user_id}'
    get_response = requests.get(get_user_url)

    assert get_response.status_code == 200
    assert 'user' in get_response.json()

    retrieved_user = get_response.json()['user']
    assert retrieved_user['user_id'] == user_id

    # Delete the created user to make the test idempotent
    delete_test_user(user_id)

def test_get_user_not_found():
    # Attempt to retrieve a non-existent user
    non_existent_user_id = fake.random_int(min=1001, max=2000)
    get_user_url = f'{base_url}/users/{non_existent_user_id}'
    get_response = requests.get(get_user_url)

    assert get_response.status_code == 404
    assert 'message' in get_response.json()
    assert get_response.json()['message'] == 'User not found'

def test_update_user_success():
    # Create a user for testing
    user_id = create_test_user()

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

    # Delete the created user to make the test idempotent
    delete_test_user(user_id)

def test_update_user_missing_fields():
    # Create a user for testing
    user_id = create_test_user()

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
    # Create a user for testing
    user_id = create_test_user()

    # Delete the created user
    delete_user_url = f'{base_url}/users/{user_id}'
    delete_response = requests.delete(delete_user_url)

    assert delete_response.status_code == 200
    assert delete_response.json()['message'] == 'User deleted successfully'

def test_delete_user_not_found():
    non_existent_user_id = fake.random_int(min=2001, max=3000)
    delete_user_url = f'{base_url}/users/{non_existent_user_id}'
    delete_response = requests.delete(delete_user_url)

    assert delete_response.status_code == 404
    assert 'message' in delete_response.json()
    assert delete_response.json()['message'] == 'User not found'

