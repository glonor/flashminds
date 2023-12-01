import ebisu
from datetime import datetime

import requests
from flask import Flask, jsonify, request
import json
from os import environ

app = Flask(__name__)
DL_API_URL = environ.get('DL_URL')
CHATGPT_URL = environ.get('CHATGPT_URL')

def get_flashcard(user_id, deck_id, card_id):
    try:
        endpoint = f'/users/{user_id}/decks/{deck_id}/flashcards/{card_id}'
        response = requests.get(f'{DL_API_URL}{endpoint}')
        return response
    except requests.RequestException as e:
        return jsonify({'error': f'Error making request to remote server: {e}'}), 500


def update_session_statistics(user_id, deck_id, session_id, confidence):
    try:
        endpoint = f'/users/{user_id}/decks/{deck_id}/study_sessions/{session_id}'
        response = requests.put(f'{DL_API_URL}{endpoint}', json={'confidence': confidence})
        return response
    except requests.RequestException as e:
        return jsonify({'error': f'Error making request to remote server: {e}'}), 500


def update_flashcard(user_id, deck_id, card_id, update_data):
    try:
        endpoint = f'/users/{user_id}/decks/{deck_id}/flashcards/{card_id}'
        response = requests.put(f'{DL_API_URL}{endpoint}', json=update_data)
        return response
    except requests.RequestException as e:
        return jsonify({'error': f'Error making request to remote server: {e}'}), 500

# Endpoint to review a flashcard
@app.route('/review_flashcard', methods=['POST'])
def review_flashcard():
    try:
        # Retrieve data from the incoming request
        data = request.get_json()
        user_id = data.get('user_id')
        deck_id = data.get('deck_id')
        card_id = data.get('card_id')
        confidence = data.get('confidence')
        session_id = data.get('session_id')

        if card_id is None or session_id is None or user_id is None or deck_id is None or confidence is None or not (1 <= confidence <= 5):
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Check if session exists and is ongoing
        session_response = get_study_session(user_id, deck_id, session_id)
        if session_response.status_code != 200:
            return session_response.json(), session_response.status_code
        session = session_response.json().get('study_session')
        if session.get('end_time') != None:
            return jsonify({'message': 'Session is already over'}), 400

        # Get flashcard model
        response = get_flashcard(user_id, deck_id, card_id)
        flashcard = response.json().get('flashcard')
        if response.status_code == 200:
            if flashcard['ebisu_model'] is None:
                model = ebisu.initModel(firstHalflife=10, lastHalflife=10e3, firstWeight=0.9, numAtoms=5, initialAlphaBeta=2.0)
            else:
                prior_model =  flashcard['ebisu_model']
                last_reviewed = flashcard['last_reviewed']
                # Get the elapsed time since the last review in hours
                elapsed_time = int((datetime.now() - datetime.strptime(last_reviewed, '%a, %d %b %Y %H:%M:%S %Z')).total_seconds() / 3600)
                confidence_score = (confidence - 1) / 4.0
                decoded_data = json.loads(prior_model)
                prior_model = [ebisu.Atom.from_dict(atom_data) for atom_data in decoded_data]

                # To avoid division by zero error
                if elapsed_time == 0:
                    elapsed_time = 1

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
        response = update_session_statistics(user_id, deck_id, session_id, confidence)
        if response.status_code != 200:
            return response.json(), response.status_code

        # Update flashcard
        response = update_flashcard(user_id, deck_id, card_id, update_data)

        # Check the response from the server and return a response to the client
        if response.status_code == 200:
            return jsonify({'message': 'Flashcard reviewed successfully'}), 200
        else:
            return response.json(), response.status_code

    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error reviewing flashcard: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500
    
def get_study_session(user_id, deck_id, session_id):
    try:
        endpoint = f'/users/{user_id}/decks/{deck_id}/study_sessions/{session_id}'
        response = requests.get(f'{DL_API_URL}{endpoint}')
        return response
    except requests.RequestException as e:
        return jsonify({'error': f'Error making request to remote server: {e}'}), 500


def get_flashcards(user_id, deck_id):
    try:
        endpoint = f'/users/{user_id}/decks/{deck_id}/flashcards'
        response = requests.get(f'{DL_API_URL}{endpoint}')
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
        elapsed_time = int((datetime.now() - datetime.strptime(last_reviewed, '%a, %d %b %Y %H:%M:%S %Z')).total_seconds() / 3600)
        return ebisu.predictRecall(f_model, elapsed_time)


@app.route('/get_next_flashcard', methods=['GET'])
def get_next_flashcard():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        deck_id = data.get('deck_id')
        user_id = data.get('user_id')
        chatgpt = data.get('chatgpt')

        if session_id is None or deck_id is None or user_id is None:
            return jsonify({'message': 'Missing required fields'}), 400

        # Check if session exists and is ongoing
        session_response = get_study_session(user_id, deck_id, session_id)
        if session_response.status_code != 200:
            return session_response.json(), session_response.status_code
        
        session = session_response.json().get('study_session')
        if session.get('end_time') != None:
            return jsonify({'message': 'Session is already over'}), 400

        # Get all flashcards in the deck
        flashcards_response = get_flashcards(user_id, deck_id)
        if flashcards_response.status_code == 200:
            flashcards = flashcards_response.json().get('flashcards')
        else:
            return flashcards_response.json(), flashcards_response.status_code

        # Get the recall probability for each flashcard
        for flashcard in flashcards:
            flashcard['recall_probability'] = get_recall_probability(flashcard)

        # Sort the flashcards by recall_probability
        flashcards = sorted(flashcards, key=lambda x: x['recall_probability'])

        # Get the flashcard with the lowest recall_probability
        flashcard = {
            'question': flashcards[0]['question'],
            'answer': flashcards[0]['answer']
        }

        if chatgpt:
            # Generate paraphrased flashcard
            paraphrase_url = f'{CHATGPT_URL}/paraphrase'
            paraphrase_payload = {
                'flashcard': "{flashcard}"
            }
            paraphrase_response = requests.post(paraphrase_url, json=paraphrase_payload)

            # Check the response from the server
            if paraphrase_response.status_code == 200:
                paraphrased_flashcard = paraphrase_response.json()
                paraphrased_flashcard['card_id'] = flashcards[0]['card_id']
                return jsonify(paraphrased_flashcard), 200

        # Return the flashcard if paraphrasing is not required or if paraphrasing fails
        # return jsonify({
        #     'question': flashcards[0]['question'],
        #     'answer': flashcards[0]['answer'],
        #     'card_id': flashcards[0]['card_id']
        # }), 200

        # For debugging purposes    
        return jsonify(flashcards[0]), 200

    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error getting next flashcard: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500

# Endpoint to start a study session
@app.route('/start_study_session', methods=['POST'])
def start_study_session():
    try:
        # Retrieve data from the incoming request
        data = request.get_json()
        user_id = data.get('user_id')
        deck_id = data.get('deck_id')

        if user_id is None or deck_id is None:
            return jsonify({'message': 'Missing required fields'}), 400

        # Create a new study session
        endpoint = f'/users/{user_id}/decks/{deck_id}/study_sessions'
        response = requests.post(f'{DL_API_URL}{endpoint}')
        session_id = response.json().get('session_id')
        if response.status_code == 200:
            return jsonify({'message': 'Study session started successfully', 'session_id': session_id}), 200
        else:
            return response.json(), response.status_code

    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error starting study session: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500
    
# Endpoint to end a study session
@app.route('/end_study_session', methods=['POST'])
def end_study_session():
    try:
        # Retrieve data from the incoming request
        data = request.get_json()
        user_id = data.get('user_id')
        deck_id = data.get('deck_id')
        session_id = data.get('session_id')

        if user_id is None or deck_id is None or session_id is None:
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Check if session exists and is ongoing
        session_response = get_study_session(user_id, deck_id, session_id)
        if session_response.status_code != 200:
            return session_response.json(), session_response.status_code
        
        session = session_response.json().get('study_session')
        if session.get('end_time') != None:
            return jsonify({'message': 'Session is already over'}), 400

        # End the study session
        endpoint = f'/users/{user_id}/decks/{deck_id}/study_sessions/{session_id}'
        response = requests.put(f'{DL_API_URL}{endpoint}', json={'end_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')})
        if response.status_code != 200:
            return response.json(), response.status_code
        
        # Return the average confidence for the session
        average_confidence = session.get('average_confidence')
        return jsonify({'message': 'Study session ended successfully', 'average_confidence': average_confidence}), 200
            

    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error ending study session: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)