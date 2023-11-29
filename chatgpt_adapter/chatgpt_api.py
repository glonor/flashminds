from flask import Flask, jsonify, request
from openai import OpenAI
import os
import json

app = Flask(__name__)

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

@app.route('/paraphrase', methods=['GET'])
def paraphrase():
    try:
        # Extract the input flashcard from the request
        input_flashcard = request.json.get('flashcard')

        # Use OpenAI function to generate paraphrased flashcard
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "As a paraphraser, generate a variation of json formatted flashcards that are similar to the original flashcards"},
                {"role": "user", "content": input_flashcard},
            ]
        )

        # Extract the paraphrased flashcard from OpenAI response
        paraphrased_flashcard = json.loads(completion.choices[0].message.content)

        # Return the paraphrased flashcard as JSON response
        return jsonify(paraphrased_flashcard)

    except Exception as e:
        # Handle errors and return an appropriate response
        return jsonify({'error': str(e)}), 500

@app.route('/generate_flashcard', methods=['GET'])
def generate_flashcard():
    try:
        # Extract the input text from the request
        input_text = request.json.get('text')

        # Use OpenAI function to generate a flashcard as per the system message
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "As a flashcard creator, generate RFC8259 compliant JSON responses adhering strictly to the specified format, including only the question and answer without any additional explanations"},
                {"role": "user", "content": input_text},
            ]
        )

        # Extract the generated flashcard from OpenAI response
        generated_flashcard = json.loads(completion.choices[0].message.content)

        # Return the generated flashcard as JSON response
        return jsonify(generated_flashcard)

    except Exception as e:
        # Handle errors and return an appropriate response
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)