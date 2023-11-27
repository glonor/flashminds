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

def test_create_study_session_success():
    create_study_session_url = f'{base_url}/users/{user_id}/decks/{deck_id}/study_sessions'
    create_study_session_response = requests.post(create_study_session_url)

    assert create_study_session_response.status_code == 201
    assert 'message' in create_study_session_response.json()
    assert 'session_id' in create_study_session_response.json()
    assert create_study_session_response.json()['message'] == 'Study session created successfully'

def test_create_study_session_deck_not_found():
    non_existent_deck_id = fake.random_int(min=100001, max=200000)
    create_study_session_url = f'{base_url}/users/{user_id}/decks/{non_existent_deck_id}/study_sessions'
    create_study_session_response = requests.post(create_study_session_url)

    assert create_study_session_response.status_code == 404
    assert 'message' in create_study_session_response.json()
    assert create_study_session_response.json()['message'] == 'Deck not found'

def test_create_study_session_user_not_found():
    non_existent_user_id = fake.random_int(min=200001, max=300000)
    create_study_session_url = f'{base_url}/users/{non_existent_user_id}/decks/{deck_id}/study_sessions'
    create_study_session_response = requests.post(create_study_session_url)

    assert create_study_session_response.status_code == 404
    assert 'message' in create_study_session_response.json()
    assert create_study_session_response.json()['message'] == 'User not found'

def test_get_study_sessions_success():
    create_study_session_url = f'{base_url}/users/{user_id}/decks/{deck_id}/study_sessions'
    create_study_session_response = requests.post(create_study_session_url)
    assert create_study_session_response.status_code == 201

    get_study_sessions_url = f'{base_url}/users/{user_id}/decks/{deck_id}/study_sessions'
    get_study_sessions_response = requests.get(get_study_sessions_url)

    assert get_study_sessions_response.status_code == 200
    assert 'study_sessions' in get_study_sessions_response.json()
    assert len(get_study_sessions_response.json()['study_sessions']) > 0

def test_get_study_sessions_no_study_sessions():
    create_deck_url = f'{base_url}/users/{user_id}/decks'
    deck_name = fake.word()
    payload = {"deck_name": deck_name}
    create_deck_response = requests.post(create_deck_url, json=payload)
    assert create_deck_response.status_code == 201
    deck_id = create_deck_response.json()["deck_id"]

    get_study_sessions_url = f'{base_url}/users/{user_id}/decks/{deck_id}/study_sessions'
    get_study_sessions_response = requests.get(get_study_sessions_url)

    assert get_study_sessions_response.status_code == 404
    assert 'message' in get_study_sessions_response.json()
    assert get_study_sessions_response.json()['message'] == 'No study sessions found for the specified deck'

def test_get_study_sessions_deck_not_found():
    non_existent_deck_id = fake.random_int(min=100001, max=200000)
    get_study_sessions_url = f'{base_url}/users/{user_id}/decks/{non_existent_deck_id}/study_sessions'
    get_study_sessions_response = requests.get(get_study_sessions_url)

    assert get_study_sessions_response.status_code == 404
    assert 'message' in get_study_sessions_response.json()
    assert get_study_sessions_response.json()['message'] == 'Deck not found'

def test_get_study_sessions_user_not_found():
    non_existent_user_id = fake.random_int(min=200001, max=300000)
    get_study_sessions_url = f'{base_url}/users/{non_existent_user_id}/decks/{deck_id}/study_sessions'
    get_study_sessions_response = requests.get(get_study_sessions_url)

    assert get_study_sessions_response.status_code == 404
    assert 'message' in get_study_sessions_response.json()
    assert get_study_sessions_response.json()['message'] == 'User not found'

create_study_session_url = f'{base_url}/users/{user_id}/decks/{deck_id}/study_sessions'
create_study_session_response = requests.post(create_study_session_url)
assert create_study_session_response.status_code == 201

def test_get_study_session_success():
    session_id = create_study_session_response.json()["session_id"]
    get_study_session_url = f'{base_url}/users/{user_id}/decks/{deck_id}/study_sessions/{session_id}'
    get_study_session_response = requests.get(get_study_session_url)

    assert get_study_session_response.status_code == 200
    assert 'study_session' in get_study_session_response.json()
    assert get_study_session_response.json()['study_session']['session_id'] == session_id

def test_get_study_session_session_not_found():
    non_existent_session_id = fake.random_int(min=100001, max=200000)
    get_study_session_url = f'{base_url}/users/{user_id}/decks/{deck_id}/study_sessions/{non_existent_session_id}'
    get_study_session_response = requests.get(get_study_session_url)

    assert get_study_session_response.status_code == 404
    assert 'message' in get_study_session_response.json()
    assert get_study_session_response.json()['message'] == 'Study session not found'

def test_get_study_session_deck_not_found():
    non_existent_deck_id = fake.random_int(min=200001, max=300000)
    get_study_session_url = f'{base_url}/users/{user_id}/decks/{non_existent_deck_id}/study_sessions/{create_study_session_response.json()["session_id"]}'
    get_study_session_response = requests.get(get_study_session_url)

    assert get_study_session_response.status_code == 404
    assert 'message' in get_study_session_response.json()
    assert get_study_session_response.json()['message'] == 'Deck not found'

def test_get_study_session_user_not_found():
    non_existent_user_id = fake.random_int(min=300001, max=400000)
    get_study_session_url = f'{base_url}/users/{non_existent_user_id}/decks/{deck_id}/study_sessions/{create_study_session_response.json()["session_id"]}'
    get_study_session_response = requests.get(get_study_session_url)

    assert get_study_session_response.status_code == 404
    assert 'message' in get_study_session_response.json()
    assert get_study_session_response.json()['message'] == 'User not found'

def test_update_study_session_success():
    session_id = create_study_session_response.json()["session_id"]
    update_study_session_url = f'{base_url}/users/{user_id}/decks/{deck_id}/study_sessions/{session_id}'
    update_study_session_payload = {"average_confidence": 0.8, "end_time": "2023-01-01T12:00:00"}
    update_study_session_response = requests.put(update_study_session_url, json=update_study_session_payload)

    assert update_study_session_response.status_code == 200
    assert 'message' in update_study_session_response.json()
    assert update_study_session_response.json()['message'] == 'Study session updated successfully'

def test_update_study_session_missing_fields():
    session_id = create_study_session_response.json()["session_id"]
    update_study_session_url = f'{base_url}/users/{user_id}/decks/{deck_id}/study_sessions/{session_id}'
    update_study_session_payload = {}  # Missing 'average_confidence' and 'end_time' fields
    update_study_session_response = requests.put(update_study_session_url, json=update_study_session_payload)

    assert update_study_session_response.status_code == 400
    assert 'message' in update_study_session_response.json()
    assert update_study_session_response.json()['message'] == 'Missing required fields'

def test_update_study_session_session_not_found():
    non_existent_session_id = fake.random_int(min=100001, max=200000)
    update_study_session_url = f'{base_url}/users/{user_id}/decks/{deck_id}/study_sessions/{non_existent_session_id}'
    update_study_session_payload = {"average_confidence": 0.8, "end_time": "2023-01-01T12:00:00"}
    update_study_session_response = requests.put(update_study_session_url, json=update_study_session_payload)

    assert update_study_session_response.status_code == 404
    assert 'message' in update_study_session_response.json()
    assert update_study_session_response.json()['message'] == 'Study session not found'

def test_update_study_session_deck_not_found():
    non_existent_deck_id = fake.random_int(min=200001, max=300000)
    session_id = create_study_session_response.json()["session_id"]
    update_study_session_url = f'{base_url}/users/{user_id}/decks/{non_existent_deck_id}/study_sessions/{session_id}'
    update_study_session_payload = {"average_confidence": 0.8, "end_time": "2023-01-01T12:00:00"}
    update_study_session_response = requests.put(update_study_session_url, json=update_study_session_payload)

    assert update_study_session_response.status_code == 404
    assert 'message' in update_study_session_response.json()
    assert update_study_session_response.json()['message'] == 'Deck not found'

def test_update_study_session_user_not_found():
    non_existent_user_id = fake.random_int(min=300001, max=400000)
    session_id = create_study_session_response.json()["session_id"]
    update_study_session_url = f'{base_url}/users/{non_existent_user_id}/decks/{deck_id}/study_sessions/{session_id}'
    update_study_session_payload = {"average_confidence": 0.8, "end_time": "2023-01-01T12:00:00"}
    update_study_session_response = requests.put(update_study_session_url, json=update_study_session_payload)

    assert update_study_session_response.status_code == 404
    assert 'message' in update_study_session_response.json()
    assert update_study_session_response.json()['message'] == 'User not found'