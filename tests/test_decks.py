import requests
from faker import Faker

from test_users import create_test_user, delete_test_user

fake = Faker()
base_url = 'http://localhost:5000'

def create_test_deck():
    user_id = create_test_user()

    create_deck_url = f'{base_url}/users/{user_id}/decks'
    deck_name = fake.word()
    payload = {"deck_name": deck_name}
    create_deck_response = requests.post(create_deck_url, json=payload)
    assert create_deck_response.status_code == 201
    deck_id = create_deck_response.json()["deck_id"]

    return user_id, deck_id

# Endpoint to create a deck tests

def test_create_deck_success():
    # Create a user for testing
    user_id = create_test_user()

    # Create a deck for the user
    create_deck_url = f'{base_url}/users/{user_id}/decks'
    deck_name = fake.word()
    deck_payload = {"deck_name": deck_name}
    create_deck_response = requests.post(create_deck_url, json=deck_payload)

    assert create_deck_response.status_code == 201
    assert create_deck_response.json()['message'] == 'Deck created successfully'

    # Delete the deck created for testing
    delete_deck_url = f'{base_url}/users/{user_id}/decks/{create_deck_response.json()["deck_id"]}'
    delete_deck_response = requests.delete(delete_deck_url)
    assert delete_deck_response.status_code == 200

    # Delete the user created for testing
    delete_test_user(user_id)

def test_create_deck_missing_fields():
    # Create a user for testing
    user_id = create_test_user()

    # Attempt to create a deck with missing fields
    create_deck_url = f'{base_url}/users/{user_id}/decks'
    payload = {}  # Missing 'deck_name' field
    create_deck_response = requests.post(create_deck_url, json=payload)

    assert create_deck_response.status_code == 400
    assert 'message' in create_deck_response.json()
    assert create_deck_response.json()['message'] == 'Missing required fields'

    # Delete the user created for testing
    delete_test_user(user_id)

def test_create_deck_user_not_found():
    non_existent_user_id = fake.random_int(min=2001, max=3000)
    create_deck_url = f'{base_url}/users/{non_existent_user_id}/decks'
    payload = {"deck_name": "test_deck"}
    create_deck_response = requests.post(create_deck_url, json=payload)

    assert create_deck_response.status_code == 404
    assert 'message' in create_deck_response.json()
    assert create_deck_response.json()['message'] == 'User not found'

def test_create_deck_conflict():
    # Create a user for testing
    user_id = create_test_user()

    # Attempt to create the first deck
    create_deck_url = f'{base_url}/users/{user_id}/decks'
    deck_name = fake.word()
    payload = {"deck_name": deck_name}
    create_first_deck_response = requests.post(create_deck_url, json=payload)

    # Check if the first deck was created successfully
    assert create_first_deck_response.status_code == 201

    # Attempt to create the second deck with the same name for the same user
    create_second_deck_response = requests.post(create_deck_url, json=payload)

    # Check if the second deck creation failed due to conflict
    if create_second_deck_response.status_code == 409:
        assert 'message' in create_second_deck_response.json()
        assert create_second_deck_response.json()['message'] == 'Deck with the same name already exists'

    # Delete the user created for testing
    delete_test_user(user_id)

# Endpoint to update a deck tests

def test_update_deck_success():
    user_id, deck_id = create_test_deck()

    # Update the deck
    update_deck_url = f'{base_url}/users/{user_id}/decks/{deck_id}'
    updated_deck_name = fake.word()
    update_deck_payload = {"deck_name": updated_deck_name}
    update_deck_response = requests.put(update_deck_url, json=update_deck_payload)

    assert update_deck_response.status_code == 200
    assert update_deck_response.json()['message'] == 'Deck updated successfully'

    # Retrieve the updated deck and check if the deck name has changed
    get_deck_url = f'{base_url}/users/{user_id}/decks/{deck_id}'
    get_deck_response = requests.get(get_deck_url)
    assert get_deck_response.status_code == 200

    retrieved_deck = get_deck_response.json()['deck']
    assert retrieved_deck['deck_name'] == updated_deck_name

    # Delete the user created for testing
    delete_test_user(user_id)

def test_update_deck_conflict():
    user_id, deck_id = create_test_deck()

    # Create the second deck
    create_deck_url = f'{base_url}/users/{user_id}/decks'
    deck_name = fake.word()
    create_deck_payload = {"deck_name": deck_name}
    create_second_deck_response = requests.post(create_deck_url, json=create_deck_payload)
    assert create_second_deck_response.status_code == 201

    # Attempt to update the first deck with the same name as the second deck
    update_deck_url = f'{base_url}/users/{user_id}/decks/{deck_id}'
    update_deck_payload = {"deck_name": deck_name}
    update_deck_response = requests.put(update_deck_url, json=update_deck_payload)

    # Check if the deck update failed due to conflict
    assert update_deck_response.status_code == 409
    assert 'message' in update_deck_response.json()
    assert update_deck_response.json()['message'] == 'Deck with the same name already exists'

    # Delete the user created for testing
    delete_test_user(user_id)

def test_update_deck_missing_fields():
    user_id, deck_id = create_test_deck()

    # Attempt to update the deck with missing fields
    update_deck_url = f'{base_url}/users/{user_id}/decks/{deck_id}'
    update_deck_payload = {}  # Missing 'deck_name' field
    update_deck_response = requests.put(update_deck_url, json=update_deck_payload)

    # Check if the update failed due to missing fields
    assert update_deck_response.status_code == 400
    assert 'message' in update_deck_response.json()
    assert update_deck_response.json()['message'] == 'Missing required fields'

    # Delete the user created for testing
    delete_test_user(user_id)

def test_update_deck_user_not_found():
    # Attempt to update a deck for a non-existent user
    non_existent_user_id = fake.random_int(min=3001, max=4000)
    deck_id = fake.random_int(min=4001, max=5000)
    update_deck_url = f'{base_url}/users/{non_existent_user_id}/decks/{deck_id}'
    update_deck_payload = {"deck_name": "updated_deck"}
    update_deck_response = requests.put(update_deck_url, json=update_deck_payload)

    assert update_deck_response.status_code == 404
    assert 'message' in update_deck_response.json()
    assert update_deck_response.json()['message'] == 'User not found'

def test_update_deck_deck_not_found():
    # Create a user for testing
    user_id = create_test_user()

    # Attempt to update a non-existent deck
    non_existent_deck_id = fake.random_int(min=6001, max=7000)
    update_deck_url = f'{base_url}/users/{user_id}/decks/{non_existent_deck_id}'
    update_deck_payload = {"deck_name": "updated_deck"}
    update_deck_response = requests.put(update_deck_url, json=update_deck_payload)

    assert update_deck_response.status_code == 404
    assert 'message' in update_deck_response.json()
    assert update_deck_response.json()['message'] == 'Deck not found'

    # Delete the user created for testing
    delete_test_user(user_id)

# Endpoint to get a deck tests

def test_get_deck_success():
    user_id, deck_id = create_test_deck()

    # Retrieve the created deck
    get_deck_url = f'{base_url}/users/{user_id}/decks/{deck_id}'
    get_deck_response = requests.get(get_deck_url)

    # Check if the deck was retrieved successfully
    assert get_deck_response.status_code == 200
    assert 'deck' in get_deck_response.json()
    assert get_deck_response.json()['deck']['deck_id'] == deck_id
    assert get_deck_response.json()['deck']['user_id'] == user_id

    # Delete the user created for testing
    delete_test_user(user_id)

def test_get_deck_not_found():
    # Create a user for testing
    user_id = create_test_user()

    # Attempt to retrieve a non-existent deck
    non_existent_deck_id = fake.random_int(min=100001, max=200000)
    get_deck_url = f'{base_url}/users/{user_id}/decks/{non_existent_deck_id}'
    get_deck_response = requests.get(get_deck_url)

    # Check if the expected 404 response is received
    assert get_deck_response.status_code == 404
    assert 'message' in get_deck_response.json()
    assert get_deck_response.json()['message'] == 'Deck not found'

    # Delete the user created for testing
    delete_test_user(user_id)

def test_get_deck_user_not_found():
    # Attempt to retrieve a deck for a non-existent user
    non_existent_user_id = fake.random_int(min=200001, max=300000)
    get_deck_url = f'{base_url}/users/{non_existent_user_id}/decks/{fake.random_int(min=1, max=100000)}'
    get_deck_response = requests.get(get_deck_url)

    # Check if the expected 404 response is received
    assert get_deck_response.status_code == 404
    assert 'message' in get_deck_response.json()
    assert get_deck_response.json()['message'] == 'User not found'

# Endpoint to get all decks for a user tests

def test_get_decks_success():
    # Create a user for testing
    user_id, deck_id = create_test_deck()

    # Retrieve the created decks
    get_decks_url = f'{base_url}/users/{user_id}/decks'
    get_decks_response = requests.get(get_decks_url)

    # Check if the decks were retrieved successfully
    assert get_decks_response.status_code == 200
    assert 'decks' in get_decks_response.json()
    assert len(get_decks_response.json()['decks']) >= 1

    # Delete the user created for testing
    delete_test_user(user_id)

def test_get_decks_no_decks():
    # Create a user for testing
    user_id = create_test_user()

    # Attempt to retrieve decks for the created user
    get_decks_url = f'{base_url}/users/{user_id}/decks'
    get_decks_response = requests.get(get_decks_url)

    # Check if the expected 404 response is received
    assert get_decks_response.status_code == 404
    assert 'message' in get_decks_response.json()
    assert get_decks_response.json()['message'] == 'No decks found for the specified user'

    # Delete the user created for testing
    delete_test_user(user_id)

def test_get_decks_user_not_found():
    # Attempt to retrieve decks for a non-existent user
    non_existent_user_id = fake.random_int(min=200001, max=300000)
    get_decks_url = f'{base_url}/users/{non_existent_user_id}/decks'
    get_decks_response = requests.get(get_decks_url)

    # Check if the expected 404 response is received
    assert get_decks_response.status_code == 404
    assert 'message' in get_decks_response.json()
    assert get_decks_response.json()['message'] == 'User not found'

# Endpoint to delete a deck tests

def test_delete_deck_success():
    user_id, deck_id = create_test_deck()

    # Attempt to delete the created deck
    delete_deck_url = f'{base_url}/users/{user_id}/decks/{deck_id}'
    delete_deck_response = requests.delete(delete_deck_url)

    # Check if the deck was deleted successfully
    assert delete_deck_response.status_code == 200
    assert 'message' in delete_deck_response.json()
    assert delete_deck_response.json()['message'] == 'Deck deleted successfully'

    # Delete the user created for testing
    delete_test_user(user_id)

def test_delete_deck_not_found():
    # Create a user for testing
    user_id = create_test_user()

    # Attempt to delete a non-existent deck
    non_existent_deck_id = fake.random_int(min=100001, max=200000)
    delete_deck_url = f'{base_url}/users/{user_id}/decks/{non_existent_deck_id}'
    delete_deck_response = requests.delete(delete_deck_url)

    # Check if the expected 404 response is received
    assert delete_deck_response.status_code == 404
    assert 'message' in delete_deck_response.json()
    assert delete_deck_response.json()['message'] == 'Deck not found'

    # Delete the user created for testing
    delete_test_user(user_id)


def test_delete_deck_user_not_found():
    # Attempt to delete a deck for a non-existent user
    non_existent_user_id = fake.random_int(min=200001, max=300000)
    delete_deck_url = f'{base_url}/users/{non_existent_user_id}/decks/{fake.random_int(min=1, max=100000)}'
    delete_deck_response = requests.delete(delete_deck_url)

    # Check if the expected 404 response is received
    assert delete_deck_response.status_code == 404
    assert 'message' in delete_deck_response.json()
    assert delete_deck_response.json()['message'] == 'User not found'