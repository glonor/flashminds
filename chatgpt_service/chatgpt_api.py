from flask import Flask, jsonify, request
from openai import OpenAI
import os
import json

app = Flask(__name__)

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

MAX_RETRIES = 3

class FlashcardFormatError(Exception):
    pass

@app.route('/paraphrase', methods=['POST'])
def paraphrase():
    try:
        # Extract the input flashcard from the request
        input_flashcard = request.json.get('flashcard')


        for attempt in range(MAX_RETRIES):
            try:
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

                # Check that json formatted flashcard has only a question and answer
                if 'question' not in paraphrased_flashcard or 'answer' not in paraphrased_flashcard or len(paraphrased_flashcard) != 2:
                    # raise a custom exception if the flashcard is not in the correct format
                    raise FlashcardFormatError('Paraphrased flashcard is not in the correct format')
                    

                # Return the paraphrased flashcard as JSON response
                return jsonify(paraphrased_flashcard), 200

            except (json.JSONDecodeError, FlashcardFormatError) as e:
                # Retry if JSON loading fails
                if attempt < MAX_RETRIES - 1:
                    continue
                else:
                    print(f'Error generating paraphrase: {e}')
                    return jsonify({'message': 'Unable to generate a valid JSON representation from ChatGPT after multiple attempts'}), 500

    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error generating paraphrase: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500

@app.route('/generate_flashcard', methods=['POST'])
def generate_flashcard():
    try:
        # Extract the input text from the request
        input_text = request.json.get('text')

        for attempt in range(MAX_RETRIES):
            try:

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
                return jsonify(generated_flashcard), 200
            
            except json.JSONDecodeError:
                    # Retry if JSON loading fails
                    if attempt < MAX_RETRIES - 1:
                        continue
                    else:
                        return jsonify({'message': 'Unable to generate a valid JSON representation from ChatGPT after multiple attempts'}), 500

    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error generating flashcard: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)