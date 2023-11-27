import requests
from faker import Faker

fake = Faker()
base_url = 'http://localhost:5000'
user_id = fake.random_int(min=1, max=100000)
username = "test_user"
create_user_url = f'{base_url}/users'
payload = {"user_id": user_id, "username": username}
create_user_response = requests.post(create_user_url, json=payload)
assert create_user_response.status_code == 201

def test_create_deck_success():
    # Create a deck for the user
    create_deck_url = f'{base_url}/users/{user_id}/decks'
    deck_name = fake.word()
    payload = {"deck_name": deck_name}
    create_deck_response = requests.post(create_deck_url, json=payload)

    assert create_deck_response.status_code == 201
    assert create_deck_response.json()['message'] == 'Deck created successfully'

def test_create_deck_missing_fields():
    create_deck_url = f'{base_url}/users/{user_id}/decks'
    payload = {}  # Missing 'deck_name' field
    create_deck_response = requests.post(create_deck_url, json=payload)

    assert create_deck_response.status_code == 400
    assert 'message' in create_deck_response.json()
    assert create_deck_response.json()['message'] == 'Missing required fields'

def test_create_deck_user_not_found():
    non_existent_user_id = fake.random_int(min=2001, max=3000)
    create_deck_url = f'{base_url}/users/{non_existent_user_id}/decks'
    payload = {"deck_name": "test_deck"}
    create_deck_response = requests.post(create_deck_url, json=payload)

    assert create_deck_response.status_code == 404
    assert 'message' in create_deck_response.json()
    assert create_deck_response.json()['message'] == 'User not found'

def test_create_deck_conflict():
    create_deck_url = f'{base_url}/users/{user_id}/decks'
    deck_name = fake.word()
    payload = {"deck_name": deck_name}
    create_first_deck_response = requests.post(create_deck_url, json=payload)
    assert create_first_deck_response.status_code == 201

    # Attempt to create a second deck with the same name for the same user
    create_second_deck_response = requests.post(create_deck_url, json=payload)

    assert create_second_deck_response.status_code == 409
    assert 'message' in create_second_deck_response.json()
    assert create_second_deck_response.json()['message'] == 'Deck with the same name already exists'

def test_update_deck_success():
    create_deck_url = f'{base_url}/users/{user_id}/decks'
    deck_name = fake.word()
    create_deck_payload = {"deck_name": deck_name}
    create_deck_response = requests.post(create_deck_url, json=create_deck_payload)
    assert create_deck_response.status_code == 201

    # Update the deck
    update_deck_url = f'{base_url}/users/{user_id}/decks/{create_deck_response.json()["deck_id"]}'
    updated_deck_name = fake.word()
    update_deck_payload = {"deck_name": updated_deck_name}
    update_deck_response = requests.put(update_deck_url, json=update_deck_payload)

    assert update_deck_response.status_code == 200
    assert update_deck_response.json()['message'] == 'Deck updated successfully'

    # Retrieve the updated deck and check if the deck name has changed
    get_deck_url = f'{base_url}/users/{user_id}/decks/{create_deck_response.json()["deck_id"]}'
    get_deck_response = requests.get(get_deck_url)
    assert get_deck_response.status_code == 200

    retrieved_deck = get_deck_response.json()['deck']
    assert retrieved_deck['deck_name'] == updated_deck_name

def test_update_deck_missing_fields():
    deck_id = fake.random_int(min=2001, max=3000)
    update_deck_url = f'{base_url}/users/{user_id}/decks/{deck_id}'
    update_deck_payload = {}  # Missing 'deck_name' field
    update_deck_response = requests.put(update_deck_url, json=update_deck_payload)

    assert update_deck_response.status_code == 400
    assert 'message' in update_deck_response.json()
    assert update_deck_response.json()['message'] == 'Missing required fields'

def test_update_deck_user_not_found():
    non_existent_user_id = fake.random_int(min=3001, max=4000)
    deck_id = fake.random_int(min=4001, max=5000)
    update_deck_url = f'{base_url}/users/{non_existent_user_id}/decks/{deck_id}'
    update_deck_payload = {"deck_name": "updated_deck"}
    update_deck_response = requests.put(update_deck_url, json=update_deck_payload)

    assert update_deck_response.status_code == 404
    assert 'message' in update_deck_response.json()
    assert update_deck_response.json()['message'] == 'User not found'

def test_update_deck_deck_not_found():
    non_existent_deck_id = fake.random_int(min=6001, max=7000)
    update_deck_url = f'{base_url}/users/{user_id}/decks/{non_existent_deck_id}'
    update_deck_payload = {"deck_name": "updated_deck"}
    update_deck_response = requests.put(update_deck_url, json=update_deck_payload)

    assert update_deck_response.status_code == 404
    assert 'message' in update_deck_response.json()
    assert update_deck_response.json()['message'] == 'Deck not found'

def test_get_deck_success():
    create_deck_url = f'{base_url}/users/{user_id}/decks'
    deck_name = fake.word()
    create_deck_payload = {"deck_name": deck_name}
    create_deck_response = requests.post(create_deck_url, json=create_deck_payload)
    assert create_deck_response.status_code == 201

    get_deck_url = f'{base_url}/users/{user_id}/decks/{create_deck_response.json()["deck_id"]}'
    get_deck_response = requests.get(get_deck_url)

    assert get_deck_response.status_code == 200
    assert 'deck' in get_deck_response.json()
    assert get_deck_response.json()['deck']['deck_id'] == create_deck_response.json()["deck_id"]
    assert get_deck_response.json()['deck']['user_id'] == user_id
    assert get_deck_response.json()['deck']['deck_name'] == deck_name

def test_get_deck_not_found():
    non_existent_deck_id = fake.random_int(min=100001, max=200000)
    get_deck_url = f'{base_url}/users/{user_id}/decks/{non_existent_deck_id}'
    get_deck_response = requests.get(get_deck_url)

    assert get_deck_response.status_code == 404
    assert 'message' in get_deck_response.json()
    assert get_deck_response.json()['message'] == 'Deck not found'

def test_get_decks_no_decks():
    create_user_url = f'{base_url}/users'
    
    # Create a user with the random user_id
    user_id = fake.random_int(min=1, max=100000)
    payload = {"user_id": user_id, "username": "random_username"}
    response = requests.post(create_user_url, json=payload)

    assert response.status_code == 201

    get_decks_url = f'{base_url}/users/{user_id}/decks'
    get_decks_response = requests.get(get_decks_url)

    assert get_decks_response.status_code == 404
    assert 'message' in get_decks_response.json()
    assert get_decks_response.json()['message'] == 'No decks found for the specified user'

def test_delete_deck_success():
    create_deck_url = f'{base_url}/users/{user_id}/decks'
    deck_name = fake.word()
    create_deck_payload = {"deck_name": deck_name}
    create_deck_response = requests.post(create_deck_url, json=create_deck_payload)
    assert create_deck_response.status_code == 201

    delete_deck_url = f'{base_url}/users/{user_id}/decks/{create_deck_response.json()["deck_id"]}'
    delete_deck_response = requests.delete(delete_deck_url)

    assert delete_deck_response.status_code == 200
    assert 'message' in delete_deck_response.json()
    assert delete_deck_response.json()['message'] == 'Deck deleted successfully'

def test_delete_deck_not_found():
    non_existent_deck_id = fake.random_int(min=100001, max=200000)
    delete_deck_url = f'{base_url}/users/{user_id}/decks/{non_existent_deck_id}'
    delete_deck_response = requests.delete(delete_deck_url)

    assert delete_deck_response.status_code == 404
    assert 'message' in delete_deck_response.json()
    assert delete_deck_response.json()['message'] == 'Deck not found'