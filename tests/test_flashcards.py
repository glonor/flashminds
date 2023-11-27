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

create_deck_url = f'{base_url}/users/{user_id}/decks'
deck_name = fake.word()
payload = {"deck_name": deck_name}
create_deck_response = requests.post(create_deck_url, json=payload)
assert create_deck_response.status_code == 201
deck_id = create_deck_response.json()["deck_id"]

def test_create_flashcard_success():
    create_flashcard_url = f'{base_url}/users/{user_id}/decks/{deck_id}/flashcards'
    flashcard_data = {"question": "What is the capital of France?", "answer": "Paris"}
    create_flashcard_response = requests.post(create_flashcard_url, json=flashcard_data)
    flashcard_id = create_flashcard_response.json()["card_id"]
    
    assert create_flashcard_response.status_code == 201
    assert create_flashcard_response.json()['message'] == 'Flashcard created successfully'

def test_create_flashcard_missing_fields():
    create_flashcard_url = f'{base_url}/users/{user_id}/decks/{deck_id}/flashcards'
    flashcard_data = {"question": "What is the capital of France?"}  # Missing 'answer' field
    create_flashcard_response = requests.post(create_flashcard_url, json=flashcard_data)

    assert create_flashcard_response.status_code == 400
    assert 'message' in create_flashcard_response.json()
    assert create_flashcard_response.json()['message'] == 'Missing required fields'

def test_create_flashcard_user_not_found():
    non_existent_user_id = fake.random_int(min=100001, max=200000)
    create_flashcard_url = f'{base_url}/users/{non_existent_user_id}/decks/{deck_id}/flashcards'
    flashcard_data = {"question": "What is the capital of Germany?", "answer": "Berlin"}
    create_flashcard_response = requests.post(create_flashcard_url, json=flashcard_data)

    assert create_flashcard_response.status_code == 404
    assert 'message' in create_flashcard_response.json()
    assert create_flashcard_response.json()['message'] == 'User not found'

def test_create_flashcard_deck_not_found():
    non_existent_deck_id = fake.random_int(min=100001, max=200000)
    create_flashcard_url = f'{base_url}/users/{user_id}/decks/{non_existent_deck_id}/flashcards'
    flashcard_data = {"question": "What is the capital of Spain?", "answer": "Madrid"}
    create_flashcard_response = requests.post(create_flashcard_url, json=flashcard_data)

    assert create_flashcard_response.status_code == 404
    assert 'message' in create_flashcard_response.json()
    assert create_flashcard_response.json()['message'] == 'Deck not found'

# Create a flashcard to update later
create_flashcard_url = f'{base_url}/users/{user_id}/decks/{deck_id}/flashcards'
flashcard_data = {"question": "What is the capital of France?", "answer": "Paris"}
create_flashcard_response = requests.post(create_flashcard_url, json=flashcard_data)

assert create_flashcard_response.status_code == 201
flashcard_id = create_flashcard_response.json()["card_id"]

def test_update_flashcard_success():
    update_flashcard_url = f'{base_url}/users/{user_id}/decks/{deck_id}/flashcards/{flashcard_id}'
    update_flashcard_data = {"ebisu_model": "new_model", "last_reviewed": "2023-01-01"}
    update_flashcard_response = requests.put(update_flashcard_url, json=update_flashcard_data)

    assert update_flashcard_response.status_code == 200
    assert update_flashcard_response.json()['message'] == 'Flashcard updated successfully'

def test_update_flashcard_missing_fields():
    update_flashcard_url = f'{base_url}/users/{user_id}/decks/{deck_id}/flashcards/{flashcard_id}'
    update_flashcard_data = {"ebisu_model": "new_model"}  # Missing 'last_reviewed' field
    update_flashcard_response = requests.put(update_flashcard_url, json=update_flashcard_data)

    assert update_flashcard_response.status_code == 400
    assert 'message' in update_flashcard_response.json()
    assert update_flashcard_response.json()['message'] == 'Missing required fields'

def test_update_flashcard_user_not_found():
    non_existent_user_id = fake.random_int(min=100001, max=200000)
    update_flashcard_url = f'{base_url}/users/{non_existent_user_id}/decks/{deck_id}/flashcards/{flashcard_id}'
    update_flashcard_data = {"ebisu_model": "new_model", "last_reviewed": "2023-01-01"}
    update_flashcard_response = requests.put(update_flashcard_url, json=update_flashcard_data)

    assert update_flashcard_response.status_code == 404
    assert 'message' in update_flashcard_response.json()
    assert update_flashcard_response.json()['message'] == 'User not found'

def test_update_flashcard_deck_not_found():
    non_existent_deck_id = fake.random_int(min=100001, max=200000)
    update_flashcard_url = f'{base_url}/users/{user_id}/decks/{non_existent_deck_id}/flashcards/{flashcard_id}'
    update_flashcard_data = {"ebisu_model": "new_model", "last_reviewed": "2023-01-01"}
    update_flashcard_response = requests.put(update_flashcard_url, json=update_flashcard_data)

    assert update_flashcard_response.status_code == 404
    assert 'message' in update_flashcard_response.json()
    assert update_flashcard_response.json()['message'] == 'Deck not found'

def test_update_flashcard_not_found():
    non_existent_card_id = fake.random_int(min=3001, max=4000)
    update_flashcard_url = f'{base_url}/users/{user_id}/decks/{deck_id}/flashcards/{non_existent_card_id}'
    update_flashcard_data = {"ebisu_model": "new_model", "last_reviewed": "2023-01-01"}
    update_flashcard_response = requests.put(update_flashcard_url, json=update_flashcard_data)

    assert update_flashcard_response.status_code == 404
    assert 'message' in update_flashcard_response.json()
    assert update_flashcard_response.json()['message'] == 'Flashcard not found'

def test_get_flashcards_success():
    get_flashcards_url = f'{base_url}/users/{user_id}/decks/{deck_id}/flashcards'
    get_flashcards_response = requests.get(get_flashcards_url)

    assert get_flashcards_response.status_code == 200
    assert 'flashcards' in get_flashcards_response.json()
    assert len(get_flashcards_response.json()['flashcards']) >= 1
    assert get_flashcards_response.json()['flashcards'][0]['question'] == flashcard_data["question"]
    assert get_flashcards_response.json()['flashcards'][0]['answer'] == flashcard_data["answer"]

def test_get_flashcards_deck_not_found():
    non_existent_deck_id = fake.random_int(min=100001, max=200000)
    get_flashcards_url = f'{base_url}/users/{user_id}/decks/{non_existent_deck_id}/flashcards'
    get_flashcards_response = requests.get(get_flashcards_url)

    assert get_flashcards_response.status_code == 404
    assert 'message' in get_flashcards_response.json()
    assert get_flashcards_response.json()['message'] == 'Deck not found'

def test_get_flashcards_user_not_found():
    non_existent_user_id = fake.random_int(min=200001, max=300000)
    get_flashcards_url = f'{base_url}/users/{non_existent_user_id}/decks/{deck_id}/flashcards'
    get_flashcards_response = requests.get(get_flashcards_url)

    assert get_flashcards_response.status_code == 404
    assert 'message' in get_flashcards_response.json()
    assert get_flashcards_response.json()['message'] == 'User not found'

def test_get_flashcards_no_flashcards():
    create_deck_url = f'{base_url}/users/{user_id}/decks'
    deck_name = fake.word()
    payload = {"deck_name": deck_name}
    create_deck_response = requests.post(create_deck_url, json=payload)
    assert create_deck_response.status_code == 201

    get_flashcards_url = f'{base_url}/users/{user_id}/decks/{create_deck_response.json()["deck_id"]}/flashcards'
    get_flashcards_response = requests.get(get_flashcards_url)

    assert get_flashcards_response.status_code == 404
    assert 'message' in get_flashcards_response.json()
    assert get_flashcards_response.json()['message'] == 'No flashcards found for the specified deck'

def test_get_flashcard_success():
    get_flashcard_url = f'{base_url}/users/{user_id}/decks/{deck_id}/flashcards/{flashcard_id}'
    get_flashcard_response = requests.get(get_flashcard_url)

    assert get_flashcard_response.status_code == 200
    assert 'flashcard' in get_flashcard_response.json()
    assert get_flashcard_response.json()['flashcard']['question'] == flashcard_data["question"]
    assert get_flashcard_response.json()['flashcard']['answer'] == flashcard_data["answer"]

def test_get_flashcard_deck_not_found():
    non_existent_deck_id = fake.random_int(min=100001, max=200000)
    get_flashcard_url = f'{base_url}/users/{user_id}/decks/{non_existent_deck_id}/flashcards/{flashcard_id}'
    get_flashcard_response = requests.get(get_flashcard_url)

    assert get_flashcard_response.status_code == 404
    assert 'message' in get_flashcard_response.json()
    assert get_flashcard_response.json()['message'] == 'Deck not found'

def test_get_flashcard_user_not_found():
    non_existent_user_id = fake.random_int(min=200001, max=300000)
    get_flashcard_url = f'{base_url}/users/{non_existent_user_id}/decks/{deck_id}/flashcards/{flashcard_id}'
    get_flashcard_response = requests.get(get_flashcard_url)

    assert get_flashcard_response.status_code == 404
    assert 'message' in get_flashcard_response.json()
    assert get_flashcard_response.json()['message'] == 'User not found'

def test_get_flashcard_not_found():
    non_existent_card_id = fake.random_int(min=200001, max=300000)
    get_flashcard_url = f'{base_url}/users/{user_id}/decks/{deck_id}/flashcards/{non_existent_card_id}'
    get_flashcard_response = requests.get(get_flashcard_url)

    assert get_flashcard_response.status_code == 404
    assert 'message' in get_flashcard_response.json()
    assert get_flashcard_response.json()['message'] == 'Flashcard not found'

def test_delete_flashcard_success():
    delete_flashcard_url = f'{base_url}/users/{user_id}/decks/{create_deck_response.json()["deck_id"]}/flashcards/{flashcard_id}'
    delete_flashcard_response = requests.delete(delete_flashcard_url)

    assert delete_flashcard_response.status_code == 200
    assert 'message' in delete_flashcard_response.json()
    assert delete_flashcard_response.json()['message'] == 'Flashcard deleted successfully'

def test_delete_flashcard_deck_not_found():
    non_existent_deck_id = fake.random_int(min=100001, max=200000)
    delete_flashcard_url = f'{base_url}/users/{user_id}/decks/{non_existent_deck_id}/flashcards/{flashcard_id}'
    delete_flashcard_response = requests.delete(delete_flashcard_url)

    assert delete_flashcard_response.status_code == 404
    assert 'message' in delete_flashcard_response.json()
    assert delete_flashcard_response.json()['message'] == 'Deck not found'

def test_delete_flashcard_user_not_found():
    non_existent_user_id = fake.random_int(min=200001, max=300000)
    delete_flashcard_url = f'{base_url}/users/{non_existent_user_id}/decks/{deck_id}/flashcards/{flashcard_id}'
    delete_flashcard_response = requests.delete(delete_flashcard_url)

    assert delete_flashcard_response.status_code == 404
    assert 'message' in delete_flashcard_response.json()
    assert delete_flashcard_response.json()['message'] == 'User not found'

def test_delete_flashcard_not_found():
    non_existent_card_id = fake.random_int(min=200001, max=300000)
    delete_flashcard_url = f'{base_url}/users/{user_id}/decks/{deck_id}/flashcards/{non_existent_card_id}'
    delete_flashcard_response = requests.delete(delete_flashcard_url)

    assert delete_flashcard_response.status_code == 404
    assert 'message' in delete_flashcard_response.json()
    assert delete_flashcard_response.json()['message'] == 'Flashcard not found'