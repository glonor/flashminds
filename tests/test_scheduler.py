import requests
from datetime import datetime, timedelta
import json
from test_flashcards import create_test_flashcard
from test_decks import create_test_deck

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
        "confidence": 5,  # Assume the user is very confident
        "session_id": session_id
    }
    review_flashcard_response = requests.post(review_flashcard_url, json=review_payload)

    # Check the response from the server
    assert review_flashcard_response.status_code == 200
    assert review_flashcard_response.json()['message'] == 'Flashcard reviewed successfully'

    # Clean up: Delete the user and associated data
    delete_user_url = f'{DL_API_URL}/users/123'
    delete_user_response = requests.delete(delete_user_url)
    assert delete_user_response.status_code == 200
