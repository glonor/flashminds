import requests
from faker import Faker
from test_flashcards import create_test_flashcard
from test_decks import create_test_deck

fake = Faker()

# Replace with the actual DL_API_URL
DL_API_URL = 'http://localhost:5000'
base_url = 'http://localhost:5001'

def test_review_flashcard():
    # Create a user
    flashcard_id, deck_id, user_id = create_test_flashcard()

    # Start a study session
    start_session_url = f'{DL_API_URL}/users/{user_id}/decks/{deck_id}/study_sessions'
    start_session_response = requests.post(start_session_url)
    assert start_session_response.status_code == 201
    session_id = start_session_response.json()['session_id']

    # Review the flashcard
    review_flashcard_url = f'{base_url}/review_flashcard'
    review_payload = {
        "user_id": user_id,
        "deck_id": deck_id,
        "card_id": flashcard_id,
        "confidence": 5,
        "session_id": session_id
    }
    review_flashcard_response = requests.post(review_flashcard_url, json=review_payload)

    # Check the response from the server
    assert review_flashcard_response.status_code == 200
    assert review_flashcard_response.json()['message'] == 'Flashcard reviewed successfully'

    # Clean up: Delete the user and associated data
    delete_user_url = f'{DL_API_URL}/users/{user_id}'
    delete_user_response = requests.delete(delete_user_url)
    assert delete_user_response.status_code == 200

def test_review_again_flashcard():
    # Create a user
    flashcard_id, deck_id, user_id = create_test_flashcard()

    # Start a study session
    start_session_url = f'{DL_API_URL}/users/{user_id}/decks/{deck_id}/study_sessions'
    start_session_response = requests.post(start_session_url)
    assert start_session_response.status_code == 201
    session_id = start_session_response.json()['session_id']

    # Review the flashcard
    review_flashcard_url = f'{base_url}/review_flashcard'
    review_payload = {
        "user_id": user_id,
        "deck_id": deck_id,
        "card_id": flashcard_id,
        "confidence": 3,
        "session_id": session_id
    }
    review_flashcard_response = requests.post(review_flashcard_url, json=review_payload)

    # Check the response from the server
    assert review_flashcard_response.status_code == 200
    assert review_flashcard_response.json()['message'] == 'Flashcard reviewed successfully'

    # Review the flashcard again
    new_review_payload = {
        "user_id": user_id,
        "deck_id": deck_id,
        "card_id": flashcard_id,
        "confidence": 5,
        "session_id": session_id
    }
    review_again_flashcard_response = requests.post(review_flashcard_url, json=new_review_payload)

    # Check the response from the server
    assert review_again_flashcard_response.status_code == 200
    assert review_again_flashcard_response.json()['message'] == 'Flashcard reviewed successfully'

    # Clean up: Delete the user and associated data
    delete_user_url = f'{DL_API_URL}/users/{user_id}'
    delete_user_response = requests.delete(delete_user_url)
    assert delete_user_response.status_code == 200

def test_review_flashcard_with_expired_session():
    # Create a user
    flashcard_id, deck_id, user_id = create_test_flashcard()

    # Start a study session
    start_session_url = f'{DL_API_URL}/users/{user_id}/decks/{deck_id}/study_sessions'
    start_session_response = requests.post(start_session_url)
    assert start_session_response.status_code == 201
    session_id = start_session_response.json()['session_id']

    # End the study session
    end_session_url = f'{DL_API_URL}/users/{user_id}/decks/{deck_id}/study_sessions/{session_id}'
    payload = {"confidence": 5, "end_time": "2021-04-01 00:00:00.000000"}
    end_session_response = requests.put(end_session_url, json=payload)
    assert end_session_response.status_code == 200

    # Review the flashcard
    review_flashcard_url = f'{base_url}/review_flashcard'
    review_payload = {
        "user_id": user_id,
        "deck_id": deck_id,
        "card_id": flashcard_id,
        "confidence": 5,
        "session_id": session_id
    }
    review_flashcard_response = requests.post(review_flashcard_url, json=review_payload)

    # Check the response from the server
    assert review_flashcard_response.status_code == 400
    assert review_flashcard_response.json()['message'] == 'Session is already over'

    # Clean up: Delete the user and associated data
    delete_user_url = f'{DL_API_URL}/users/{user_id}'
    delete_user_response = requests.delete(delete_user_url)
    assert delete_user_response.status_code == 200


def test_get_next_flashcard():
    # Create a user
    flashcard_id, deck_id, user_id = create_test_flashcard()

    # Start a study session
    start_session_url = f'{DL_API_URL}/users/{user_id}/decks/{deck_id}/study_sessions'
    start_session_response = requests.post(start_session_url)
    assert start_session_response.status_code == 201
    session_id = start_session_response.json()['session_id']

    # Get the next flashcard
    get_next_flashcard_url = f'{base_url}/get_next_flashcard'
    get_next_flashcard_payload = {
        "user_id": user_id,
        "deck_id": deck_id,
        "session_id": session_id
    }
    get_next_flashcard_response = requests.get(get_next_flashcard_url, json=get_next_flashcard_payload)

    # Check the response from the server
    assert get_next_flashcard_response.status_code == 200
    assert 'question' in get_next_flashcard_response.json()
    assert 'answer' in get_next_flashcard_response.json()
    assert 'card_id' in get_next_flashcard_response.json()

    # Clean up: Delete the user and associated data
    delete_user_url = f'{DL_API_URL}/users/{user_id}'
    delete_user_response = requests.delete(delete_user_url)
    assert delete_user_response.status_code == 200


def test_get_next_flashcard_with_expired_session():
    # Create a user
    flashcard_id, deck_id, user_id = create_test_flashcard()

    # Start a study session
    start_session_url = f'{DL_API_URL}/users/{user_id}/decks/{deck_id}/study_sessions'
    start_session_response = requests.post(start_session_url)
    assert start_session_response.status_code == 201
    session_id = start_session_response.json()['session_id']

    # End the study session
    end_session_url = f'{DL_API_URL}/users/{user_id}/decks/{deck_id}/study_sessions/{session_id}'
    payload = {"confidence": 5, "end_time": "2021-04-01 00:00:00.000000"}
    end_session_response = requests.put(end_session_url, json=payload)
    assert end_session_response.status_code == 200

    # Get the next flashcard
    get_next_flashcard_url = f'{base_url}/get_next_flashcard'
    get_next_flashcard_payload = {
        "user_id": user_id,
        "deck_id": deck_id,
        "session_id": session_id
    }
    get_next_flashcard_response = requests.get(get_next_flashcard_url, json=get_next_flashcard_payload)

    # Check the response from the server
    assert get_next_flashcard_response.status_code == 400
    assert get_next_flashcard_response.json()['message'] == 'Session is already over'

    # Clean up: Delete the user and associated data
    delete_user_url = f'{DL_API_URL}/users/{user_id}'
    delete_user_response = requests.delete(delete_user_url)
    assert delete_user_response.status_code == 200

def test_start_study_session():
    # Create a user and a deck
    _, deck_id, user_id = create_test_flashcard()

    # Start a study session
    start_session_url = f'{base_url}/start_study_session'
    start_session_payload = {
        "user_id": user_id,
        "deck_id": deck_id
    }
    start_session_response = requests.post(start_session_url, json=start_session_payload)

    # Check the response from the server
    assert start_session_response.status_code == 201
    assert 'message' in start_session_response.json()
    assert 'session_id' in start_session_response.json()

    # Clean up: Delete the user and associated data
    delete_user_url = f'{DL_API_URL}/users/{user_id}'
    delete_user_response = requests.delete(delete_user_url)
    assert delete_user_response.status_code == 200

def test_end_study_session():
    # Create a user, a deck, and start a study session
    flashcard_id, deck_id, user_id = create_test_flashcard()
    start_session_url = f'{base_url}/start_study_session'
    start_session_payload = {
        "user_id": user_id,
        "deck_id": deck_id
    }
    start_session_response = requests.post(start_session_url, json=start_session_payload)
    assert start_session_response.status_code == 201
    session_id = start_session_response.json()['session_id']

    # Review the flashcard
    review_flashcard_url = f'{base_url}/review_flashcard'
    review_payload = {
        "user_id": user_id,
        "deck_id": deck_id,
        "card_id": flashcard_id,
        "confidence": 5,
        "session_id": session_id
    }
    review_flashcard_response = requests.post(review_flashcard_url, json=review_payload)
    assert review_flashcard_response.status_code == 200

    # End the study session
    end_session_url = f'{base_url}/end_study_session'
    end_session_payload = {
        "user_id": user_id,
        "deck_id": deck_id,
        "session_id": session_id
    }
    end_session_response = requests.post(end_session_url, json=end_session_payload)

    # Check the response from the server
    assert end_session_response.status_code == 200
    assert 'message' in end_session_response.json()
    assert 'average_confidence' in end_session_response.json()

    # Clean up: Delete the user and associated data
    delete_user_url = f'{DL_API_URL}/users/{user_id}'
    delete_user_response = requests.delete(delete_user_url)
    assert delete_user_response.status_code == 200

def test_start_study_session_after_session_over():
    # Create a user, a deck, and start a study session
    _, deck_id, user_id = create_test_flashcard()
    start_session_url = f'{base_url}/start_study_session'
    start_session_payload = {
        "user_id": user_id,
        "deck_id": deck_id
    }
    start_session_response = requests.post(start_session_url, json=start_session_payload)
    print(start_session_response.json())
    assert start_session_response.status_code == 201
    session_id = start_session_response.json()['session_id']

    # End the study session
    end_session_url = f'{base_url}/end_study_session'
    end_session_payload = {
        "user_id": user_id,
        "deck_id": deck_id,
        "session_id": session_id
    }
    end_session_response = requests.post(end_session_url, json=end_session_payload)
    assert end_session_response.status_code == 200

    # Attempt to end the study session again
    end_session_response = requests.post(end_session_url, json=end_session_payload)
    assert end_session_response.status_code == 400

    # Clean up: Delete the user and associated data
    delete_user_url = f'{DL_API_URL}/users/{user_id}'
    delete_user_response = requests.delete(delete_user_url)
    assert delete_user_response.status_code == 200


def test_get_next_flashcard_with_paraphrasing():
    # Create a user
    flashcard_id, deck_id, user_id = create_test_flashcard()

    # Start a study session
    start_session_url = f'{DL_API_URL}/users/{user_id}/decks/{deck_id}/study_sessions'
    start_session_response = requests.post(start_session_url)
    assert start_session_response.status_code == 201
    session_id = start_session_response.json()['session_id']

    # Get the next flashcard
    get_next_flashcard_url = f'{base_url}/get_next_flashcard'
    get_next_flashcard_payload = {
        "user_id": user_id,
        "deck_id": deck_id,
        "session_id": session_id,
        "chatgpt": True
    }
    get_next_flashcard_response = requests.get(get_next_flashcard_url, json=get_next_flashcard_payload)

    # Check the response from the server
    assert get_next_flashcard_response.status_code == 200
    assert 'question' in get_next_flashcard_response.json()
    assert 'answer' in get_next_flashcard_response.json()
    assert 'card_id' in get_next_flashcard_response.json()

    # Clean up: Delete the user and associated data
    delete_user_url = f'{DL_API_URL}/users/{user_id}'
    delete_user_response = requests.delete(delete_user_url)
    assert delete_user_response.status_code == 200