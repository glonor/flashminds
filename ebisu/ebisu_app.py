import ebisu
from datetime import datetime

import requests
from flask import Flask, jsonify, request
import json

BL_API_BASE_URL = "http://business_logic:5000"

app = Flask(__name__)

def get_flashcard_model(card_id):
    try:
        endpoint = '/get_flashcard_model'
        response = requests.get(f'{BL_API_BASE_URL}{endpoint}', json={'card_id': card_id})
        return response
    except requests.RequestException as e:
        return jsonify({'error': f'Error making request to remote server: {e}'}), 500


def update_session_statistics(session_id, confidence):
    try:
        endpoint = '/update_session_statistics'
        response = requests.post(f'{BL_API_BASE_URL}{endpoint}', json={'session_id': session_id, 'confidence': confidence})
        return response
    except requests.RequestException as e:
        return jsonify({'error': f'Error making request to remote server: {e}'}), 500


def update_flashcard(update_data):
    try:
        endpoint = '/update_flashcard'
        response = requests.post(f'{BL_API_BASE_URL}{endpoint}', json=update_data)
        return response
    except requests.RequestException as e:
        return jsonify({'error': f'Error making request to remote server: {e}'}), 500

# Endpoint to review a flashcard
@app.route('/review_flashcard', methods=['POST'])
def review_flashcard():
    try:
        # Retrieve data from the incoming request
        data = request.get_json()
        card_id = data.get('card_id')
        confidence = data.get('confidence')
        session_id = data.get('session_id')

        if card_id is None or session_id is None or confidence is None or not (1 <= confidence <= 5):
            return jsonify({'error': 'card_id, session_id and confidence parameters are required, and confidence must be between 1 and 5'}), 400

        # Get flashcard model
        response = get_flashcard_model(card_id)
        if response.status_code == 204:
            model = ebisu.initModel(firstHalflife=10, lastHalflife=10e3, firstWeight=0.9, numAtoms=5, initialAlphaBeta=2.0)
        elif response.status_code == 200:
            prior_model =  response.json().get('model')
            last_reviewed = response.json().get('last_reviewed')
            elapsed_time = int((datetime.now() - datetime.strptime(last_reviewed, '%a, %d %b %Y %H:%M:%S %Z')).total_seconds())
            confidence_score = (confidence - 1) / 4.0
            decoded_data = json.loads(prior_model)
            prior_model = [ebisu.Atom.from_dict(atom_data) for atom_data in decoded_data]

            model = ebisu.updateRecall(prior_model, confidence_score, 1, elapsed_time)
        else:
            return response.json(), response.status_code

        # Encode the model to JSON
        model_json = json.dumps(ebisu.Atom.to_dict(model))

        # Create a new JSON payload with model and card_id
        update_data = {
            'card_id': card_id,
            'ebisu_model': model_json,
            'last_reviewed': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        }

        # Update session statistics
        response = update_session_statistics(session_id, confidence)
        if response.status_code != 200:
            return response.json(), response.status_code

        # Update flashcard
        response = update_flashcard(update_data)

        # Check the response from the server and return a response to the client
        if response.status_code == 201:
            return jsonify({'message': 'Flashcard reviewed successfully'}), 201
        else:
            return jsonify(response.json()), response.status_code

    except Exception as e:
        return jsonify({'error': f'Unexpected error: {e}'}), 500
    
def get_study_session(deck_id):
    try:
        get_session_endpoint = f'{BL_API_BASE_URL}/check_study_session'
        response = requests.get(get_session_endpoint, json={'session_id': deck_id})
        return response
    except requests.RequestException as e:
        return jsonify({'error': f'Error making request to remote server: {e}'}), 500


def get_flashcards(deck_id):
    try:
        get_deck_endpoint = f'{BL_API_BASE_URL}/get_flashcards'
        response = requests.get(get_deck_endpoint, json={'deck_id': deck_id})
        return response
    except requests.RequestException as e:
        return jsonify({'error': f'Error making request to remote server: {e}'}), 500


def get_recall_probability(flashcard):
    if flashcard['ebisu_model'] is None:
        return 0
    else:
        f_model = json.loads(flashcard['ebisu_model'])
        f_model = [ebisu.Atom.from_dict(atom_data) for atom_data in f_model]
        last_reviewed = flashcard['last_reviewed']
        elapsed_time = int((datetime.now() - datetime.strptime(last_reviewed, '%a, %d %b %Y %H:%M:%S %Z')).total_seconds())
        return ebisu.predictRecall(f_model, elapsed_time)


@app.route('/get_next_flashcard', methods=['GET'])
def get_next_flashcard():
    data = request.get_json()
    session_id = data.get('session_id')

    if session_id is None:
        return jsonify({'error': 'session_id parameter is required'}), 400

    # Check if session exists and is ongoing
    session_response = get_study_session(session_id)
    if session_response.status_code == 200:
        deck_id = session_response.json().get('deck_id')  # Get the deck_id from the response
    else:
        return session_response, session_response.status_code

    # Get all flashcards in the deck
    flashcards_response = get_flashcards(deck_id)
    if flashcards_response.status_code == 200:
        flashcards = flashcards_response.json().get('flashcards')
    else:
        return flashcards_response, flashcards_response.status_code

    # Get the recall probability for each flashcard
    for flashcard in flashcards:
        flashcard['recall_probability'] = get_recall_probability(flashcard)

    # Sort the flashcards by recall_probability
    flashcards = sorted(flashcards, key=lambda x: x['recall_probability'])

    # Return the flashcard with the lowest recall_probability
    return jsonify(flashcards[0]), 200
    # return jsonify({
    #     'question': flashcards[0]['question'],
    #     'answer': flashcards[0]['answer'],
    #     'card_id': flashcards[0]['card_id']
    # }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0')