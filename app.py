import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# In your app.py file, update the CHARACTERS dictionary to this:
CHARACTERS = {
    "tyrion": {
        "name": "Tyrion Lannister",
        "image": "tyrion.jpg",
        "description": "The sharp-witted Imp, a master of strategy and survival.",
        "prompt": "The story begins with Tyrion Lannister in the pitch-black, cold, and damp cells of the Black Cells..."
    },
    "daenerys": {
        "name": "Daenerys Targaryen",
        "image": "daenerys.jpg",
        "description": "The Mother of Dragons, a queen determined to reclaim her birthright.",
        "prompt": "The story begins with Daenerys Targaryen in the hot, dusty plains of the Dothki Sea..."
    },
    "jon": {
        "name": "Jon Snow",
        "image": "jon.jpg",
        "description": "The Bastard of Winterfell, a brother of the Night's Watch facing ancient evils.",
        "prompt": "The story begins with Jon Snow at Castle Black on The Wall..."
    }
}

@app.route('/')
def home():
    return render_template('index.html', characters=CHARACTERS)


@app.route('/play/<character_key>')
def play(character_key):
    character = CHARACTERS.get(character_key)
    if not character:
        return "Character not found!", 404

    model = genai.GenerativeModel('gemini-1.5-flash')
    master_prompt = f"You are a storyteller in 'A Song of Ice and Fire'... You are guiding a player as {character['name']}. Keep responses to a single, crisp paragraph. Always end by asking, 'What do you do?'.\n\n{character['prompt']}"

    response = model.generate_content(master_prompt)
    return render_template('game.html', story_text=response.text)


# This is our new API endpoint
@app.route('/continue_story', methods=['POST'])
def continue_story():
    data = request.get_json()
    story_history = data['history']
    player_action = data['action']

    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""Continue the story based on the player's action. Keep the story moving and describe the consequences. Keep the response to a single, crisp paragraph. Always end by asking, 'What do you do?'.

    STORY SO FAR:
    {story_history}

    PLAYER'S ACTION: {player_action}
    """

    response = model.generate_content(prompt)

    # We return just the new text as JSON
    return jsonify({'story_piece': response.text})


if __name__ == '__main__':
    app.run(debug=True)