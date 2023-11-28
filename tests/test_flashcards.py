import requests
from faker import Faker

from test_users import create_test_user, delete_test_user
from test_decks import create_test_deck

fake = Faker()
base_url = 'http://localhost:5000'

def create_test_flashcard():
    user_id, deck_id = create_test_deck()

    create_flashcard_url = f'{base_url}/users/{user_id}/decks/{deck_id}/flashcards'
    flashcard_data = {"question": "What is the capital of France?", "answer": "Paris"}
    create_flashcard_response = requests.post(create_flashcard_url, json=flashcard_data)

    assert create_flashcard_response.status_code == 201
    flashcard_id = create_flashcard_response.json()["card_id"]
    return flashcard_id, deck_id, user_id


def test_create_flashcard_success():
    _, _, user_id = create_test_flashcard()
    delete_test_user(user_id)

def test_create_flashcard_missing_fields():
    user_id, deck_id = create_test_deck()

    create_flashcard_url = f'{base_url}/users/{user_id}/decks/{deck_id}/flashcards'
    flashcard_data = {"question": "What is the capital of France?"}  # Missing 'answer' field
    create_flashcard_response = requests.post(create_flashcard_url, json=flashcard_data)

    assert create_flashcard_response.status_code == 400
    assert 'message' in create_flashcard_response.json()
    assert create_flashcard_response.json()['message'] == 'Missing required fields'

    delete_test_user(user_id)

def test_create_flashcard_user_not_found():    
    user_id, deck_id = create_test_deck()

    non_existent_user_id = fake.random_int(min=100001, max=200000)
    create_flashcard_url = f'{base_url}/users/{non_existent_user_id}/decks/{deck_id}/flashcards'
    flashcard_data = {"question": "What is the capital of Germany?", "answer": "Berlin"}
    create_flashcard_response = requests.post(create_flashcard_url, json=flashcard_data)

    assert create_flashcard_response.status_code == 404
    assert 'message' in create_flashcard_response.json()
    assert create_flashcard_response.json()['message'] == 'User not found'

    delete_test_user(user_id)

def test_create_flashcard_deck_not_found():    
    user_id, _ = create_test_deck()

    non_existent_deck_id = fake.random_int(min=100001, max=200000)
    create_flashcard_url = f'{base_url}/users/{user_id}/decks/{non_existent_deck_id}/flashcards'
    flashcard_data = {"question": "What is the capital of Spain?", "answer": "Madrid"}
    create_flashcard_response = requests.post(create_flashcard_url, json=flashcard_data)

    assert create_flashcard_response.status_code == 404
    assert 'message' in create_flashcard_response.json()
    assert create_flashcard_response.json()['message'] == 'Deck not found'

    delete_test_user(user_id)


def test_update_flashcard_success():
    flashcard_id, deck_id, user_id = create_test_flashcard()
    update_flashcard_url = f'{base_url}/users/{user_id}/decks/{deck_id}/flashcards/{flashcard_id}'
    update_flashcard_data = {"ebisu_model": "new_model", "last_reviewed": "2023-01-01"}
    update_flashcard_response = requests.put(update_flashcard_url, json=update_flashcard_data)

    assert update_flashcard_response.status_code == 200
    assert update_flashcard_response.json()['message'] == 'Flashcard updated successfully'

    delete_test_user(user_id)

def test_update_flashcard_missing_fields():
    flashcard_id, deck_id, user_id = create_test_flashcard()
    update_flashcard_url = f'{base_url}/users/{user_id}/decks/{deck_id}/flashcards/{flashcard_id}'
    update_flashcard_data = {"ebisu_model": "new_model"}  # Missing 'last_reviewed' field
    update_flashcard_response = requests.put(update_flashcard_url, json=update_flashcard_data)

    assert update_flashcard_response.status_code == 400
    assert 'message' in update_flashcard_response.json()
    assert update_flashcard_response.json()['message'] == 'Missing required fields'

    delete_test_user(user_id)

def test_update_flashcard_user_not_found():
    flashcard_id, deck_id, user_id = create_test_flashcard()
    non_existent_user_id = fake.random_int(min=100001, max=200000)
    update_flashcard_url = f'{base_url}/users/{non_existent_user_id}/decks/{deck_id}/flashcards/{flashcard_id}'
    update_flashcard_data = {"ebisu_model": "new_model", "last_reviewed": "2023-01-01"}
    update_flashcard_response = requests.put(update_flashcard_url, json=update_flashcard_data)

    assert update_flashcard_response.status_code == 404
    assert 'message' in update_flashcard_response.json()
    assert update_flashcard_response.json()['message'] == 'User not found'

    delete_test_user(user_id)

def test_update_flashcard_deck_not_found():
    flashcard_id, deck_id, user_id = create_test_flashcard()
    non_existent_deck_id = fake.random_int(min=100001, max=200000)
    update_flashcard_url = f'{base_url}/users/{user_id}/decks/{non_existent_deck_id}/flashcards/{flashcard_id}'
    update_flashcard_data = {"ebisu_model": "new_model", "last_reviewed": "2023-01-01"}
    update_flashcard_response = requests.put(update_flashcard_url, json=update_flashcard_data)

    assert update_flashcard_response.status_code == 404
    assert 'message' in update_flashcard_response.json()
    assert update_flashcard_response.json()['message'] == 'Deck not found'

    delete_test_user(user_id)

def test_update_flashcard_not_found():
    flashcard_id, deck_id, user_id = create_test_flashcard()
    non_existent_card_id = fake.random_int(min=3001, max=4000)
    update_flashcard_url = f'{base_url}/users/{user_id}/decks/{deck_id}/flashcards/{non_existent_card_id}'
    update_flashcard_data = {"ebisu_model": "new_model", "last_reviewed": "2023-01-01"}
    update_flashcard_response = requests.put(update_flashcard_url, json=update_flashcard_data)

    assert update_flashcard_response.status_code == 404
    assert 'message' in update_flashcard_response.json()
    assert update_flashcard_response.json()['message'] == 'Flashcard not found'

    delete_test_user(user_id)

def test_get_flashcards_success():
    flashcard_id, deck_id, user_id = create_test_flashcard()
    get_flashcards_url = f'{base_url}/users/{user_id}/decks/{deck_id}/flashcards'
    get_flashcards_response = requests.get(get_flashcards_url)

    assert get_flashcards_response.status_code == 200
    assert 'flashcards' in get_flashcards_response.json()
    assert len(get_flashcards_response.json()['flashcards']) >= 1

    delete_test_user(user_id)

def test_get_flashcards_deck_not_found():
    user_id, _ = create_test_deck()
    non_existent_deck_id = fake.random_int(min=100001, max=200000)
    get_flashcards_url = f'{base_url}/users/{user_id}/decks/{non_existent_deck_id}/flashcards'
    get_flashcards_response = requests.get(get_flashcards_url)

    assert get_flashcards_response.status_code == 404
    assert 'message' in get_flashcards_response.json()
    assert get_flashcards_response.json()['message'] == 'Deck not found'

    delete_test_user(user_id)

def test_get_flashcards_user_not_found():
    user_id, deck_id = create_test_deck()
    non_existent_user_id = fake.random_int(min=200001, max=300000)
    get_flashcards_url = f'{base_url}/users/{non_existent_user_id}/decks/{deck_id}/flashcards'
    get_flashcards_response = requests.get(get_flashcards_url)

    assert get_flashcards_response.status_code == 404
    assert 'message' in get_flashcards_response.json()
    assert get_flashcards_response.json()['message'] == 'User not found'

    delete_test_user(user_id)

def test_get_flashcards_no_flashcards():
    user_id, deck_id = create_test_deck()

    get_flashcards_url = f'{base_url}/users/{user_id}/decks/{deck_id}/flashcards'
    get_flashcards_response = requests.get(get_flashcards_url)

    assert get_flashcards_response.status_code == 404
    assert 'message' in get_flashcards_response.json()
    assert get_flashcards_response.json()['message'] == 'No flashcards found for the specified deck'

    delete_test_user(user_id)

def test_get_flashcard_success():
    flashcard_id, deck_id, user_id = create_test_flashcard()
    get_flashcard_url = f'{base_url}/users/{user_id}/decks/{deck_id}/flashcards/{flashcard_id}'
    get_flashcard_response = requests.get(get_flashcard_url)

    assert get_flashcard_response.status_code == 200
    assert 'flashcard' in get_flashcard_response.json()

    delete_test_user(user_id)

def test_get_flashcard_deck_not_found():
    flashcard_id, deck_id, user_id = create_test_flashcard()
    non_existent_deck_id = fake.random_int(min=100001, max=200000)
    get_flashcard_url = f'{base_url}/users/{user_id}/decks/{non_existent_deck_id}/flashcards/{flashcard_id}'
    get_flashcard_response = requests.get(get_flashcard_url)

    assert get_flashcard_response.status_code == 404
    assert 'message' in get_flashcard_response.json()
    assert get_flashcard_response.json()['message'] == 'Deck not found'

    delete_test_user(user_id)

def test_get_flashcard_user_not_found():
    flashcard_id, deck_id, user_id = create_test_flashcard()
    non_existent_user_id = fake.random_int(min=200001, max=300000)
    get_flashcard_url = f'{base_url}/users/{non_existent_user_id}/decks/{deck_id}/flashcards/{flashcard_id}'
    get_flashcard_response = requests.get(get_flashcard_url)

    assert get_flashcard_response.status_code == 404
    assert 'message' in get_flashcard_response.json()
    assert get_flashcard_response.json()['message'] == 'User not found'

    delete_test_user(user_id)

def test_get_flashcard_not_found():
    flashcard_id, deck_id, user_id = create_test_flashcard()
    non_existent_card_id = fake.random_int(min=200001, max=300000)
    get_flashcard_url = f'{base_url}/users/{user_id}/decks/{deck_id}/flashcards/{non_existent_card_id}'
    get_flashcard_response = requests.get(get_flashcard_url)

    assert get_flashcard_response.status_code == 404
    assert 'message' in get_flashcard_response.json()
    assert get_flashcard_response.json()['message'] == 'Flashcard not found'

    delete_test_user(user_id)

def test_delete_flashcard_success():
    flashcard_id, deck_id, user_id = create_test_flashcard()
    delete_flashcard_url = f'{base_url}/users/{user_id}/decks/{deck_id}/flashcards/{flashcard_id}'
    delete_flashcard_response = requests.delete(delete_flashcard_url)

    assert delete_flashcard_response.status_code == 200
    assert 'message' in delete_flashcard_response.json()
    assert delete_flashcard_response.json()['message'] == 'Flashcard deleted successfully'

    delete_test_user(user_id)

def test_delete_flashcard_deck_not_found():
    flashcard_id, deck_id, user_id = create_test_flashcard()
    non_existent_deck_id = fake.random_int(min=100001, max=200000)
    delete_flashcard_url = f'{base_url}/users/{user_id}/decks/{non_existent_deck_id}/flashcards/{flashcard_id}'
    delete_flashcard_response = requests.delete(delete_flashcard_url)

    assert delete_flashcard_response.status_code == 404
    assert 'message' in delete_flashcard_response.json()
    assert delete_flashcard_response.json()['message'] == 'Deck not found'

    delete_test_user(user_id)

def test_delete_flashcard_user_not_found():
    flashcard_id, deck_id, user_id = create_test_flashcard()
    non_existent_user_id = fake.random_int(min=200001, max=300000)
    delete_flashcard_url = f'{base_url}/users/{non_existent_user_id}/decks/{deck_id}/flashcards/{flashcard_id}'
    delete_flashcard_response = requests.delete(delete_flashcard_url)

    assert delete_flashcard_response.status_code == 404
    assert 'message' in delete_flashcard_response.json()
    assert delete_flashcard_response.json()['message'] == 'User not found'

    delete_test_user(user_id)

def test_delete_flashcard_not_found():
    flashcard_id, deck_id, user_id = create_test_flashcard()
    non_existent_card_id = fake.random_int(min=200001, max=300000)
    delete_flashcard_url = f'{base_url}/users/{user_id}/decks/{deck_id}/flashcards/{non_existent_card_id}'
    delete_flashcard_response = requests.delete(delete_flashcard_url)

    assert delete_flashcard_response.status_code == 404
    assert 'message' in delete_flashcard_response.json()
    assert delete_flashcard_response.json()['message'] == 'Flashcard not found'

    delete_test_user(user_id)