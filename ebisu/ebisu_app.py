import ebisu
from datetime import datetime

import requests
from flask import Flask, jsonify, request
import json

BL_API_BASE_URL = "http://business_logic:5000"

app = Flask(__name__)

@app.route('/review_flashcard', methods=['POST'])
def review_flashcard():
    # Retrieve data from the incoming request
    data = request.get_json()
    card_id = data.get('card_id')
    confidence = data.get('confidence')

    if card_id is None or confidence is None or not (1 <= confidence <= 5):
        return jsonify({'error': 'card_id and confidence parameters are required, and confidence must be between 1 and 5'}), 400


    # Check that flashcard has been reviewed at least once
    get_flashcard_model_endpoint = f'{BL_API_BASE_URL}/get_flashcard_model'
    
    response = requests.get(get_flashcard_model_endpoint, json={'card_id': card_id})
    
    if response.status_code == 204:
        model = ebisu.initModel(firstHalflife=10, lastHalflife=10e3, firstWeight=0.9, numAtoms=5, initialAlphaBeta=2.0)
    elif response.status_code == 200:
        prior_model = response.json().get('model')
        last_reviewed = response.json().get('last_reviewed')
        elapsed_time = int((datetime.now() - datetime.strptime(last_reviewed, '%a, %d %b %Y %H:%M:%S %Z')).total_seconds())
        # Map the confidence score to a scale between 0 and 1
        confidence_score = (confidence - 1) / 4.0
        decoded_data = json.loads(prior_model)

        prior_model = [ebisu.Atom.from_dict(atom_data) for atom_data in decoded_data]

        model = ebisu.updateRecall(prior_model, confidence_score, 1, elapsed_time)
    elif response.status_code == 404:
        return jsonify({f'error': {response.json().get('message')}}), 404
    else:
        return jsonify({f'error': {response.json().get('error')}}), response.status_code

    # Encode the model to JSON
    model_json = json.dumps(ebisu.Atom.to_dict(model))

    # Create a new JSON payload with model and card_id
    update_data = {
        'card_id': card_id,
        'ebisu_model': model_json,
        'last_reviewed': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    }

    # Make a request to the remote server
    endpoint = '/update_flashcard'

    try:
        # Make a POST request to the remote server
        response = requests.post(f'{BL_API_BASE_URL}{endpoint}', json=update_data)

        # Check the response from the server and return a response to the client
        if response.status_code == 201:
            return jsonify({'message': 'Flashcard reviewed successfully'}), 201
        else:
            return jsonify(response.json()), response.status_code

    except requests.RequestException as e:
        return jsonify({'error': f'Error making request to remote server: {e}'}), 500
    

if __name__ == '__main__':
    app.run(host='0.0.0.0')