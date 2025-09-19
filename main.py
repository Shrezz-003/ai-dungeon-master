import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

CHARACTERS = {
    "tyrion": {
        "name": "Tyrion Lannister",
        "prompt": "The story begins with Tyrion Lannister in the pitch-black, cold, and damp cells of the Black Cells, deep beneath the Red Keep in King's Landing. He is awaiting his trial for the murder of King Joffrey. Start the story now."
    },
    "daenerys": {
        "name": "Daenerys Targaryen",
        "prompt": "The story begins with Daenerys Targaryen in the hot, dusty plains of the Dothraki Sea, far from Westeros. She has just emerged from the funeral pyre of her husband, Khal Drogo, unburnt and with three newly hatched dragons. Start the story now."
    },
    "jon": {
        "name": "Jon Snow",
        "prompt": "The story begins with Jon Snow at Castle Black on The Wall. As a new recruit to the Night's Watch, he faces the harsh cold, the disdain of his brothers, and the ever-present, ancient threat that lies beyond the wall. Start the story now."
    }
}


def summarize_story(history):
    """Summarizes the story history using the AI."""
    print("\n[The Maester pauses to review his notes...]\n")

    model = genai.GenerativeModel('gemini-1.5-flash')

    # Create a string of the entire conversation
    story_so_far = " ".join([part.text for message in history for part in message.parts])

    # Create the summarization prompt
    prompt = f"Summarize the following story events into a single, concise paragraph that can be used as context to continue the adventure. Focus on key characters, locations, and plot developments:\n\n{story_so_far}"

    response = model.generate_content(prompt)
    return response.text


def select_character():
    print("Choose your destiny:")
    for key, character in CHARACTERS.items():
        print(f"- Type '{key}' to play as {character['name']}")

    while True:
        choice = input("> ").lower().strip()
        if choice in CHARACTERS:
            return choice
        else:
            print("That is not a valid choice.")


def run_game():
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel('gemini-1.5-flash')

        chosen_key = select_character()
        character = CHARACTERS[chosen_key]
        print(f"\nYou have chosen {character['name']}. The story begins...")

        master_prompt = f"""You are a master storyteller in the world of 'A Song of Ice and Fire'. You will guide a player through a story from the point of view of {character['name']}.
        Describe scenes vividly but keep each story response to a single, short, and crisp paragraph. Always end by asking the player, 'What do you do?'.

        {character['prompt']}
        """

        chat = model.start_chat(history=[])
        initial_response = chat.send_message(master_prompt)
        print("\n" + initial_response.text + "\n")

        turn_count = 0
        while True:
            player_action = input("> ")
            if player_action.lower().strip() in ['quit', 'exit']:
                print("Your story ends here.")
                break

            response = chat.send_message(player_action)
            print("\n" + response.text + "\n")
            turn_count += 1

            # --- The Memory Logic ---
            if turn_count % 5 == 0:
                summary = summarize_story(chat.history)
                # Start a new chat with the summary as the new history
                new_history = [
                    {'role': 'user', 'parts': [master_prompt]},
                    {'role': 'model', 'parts': [summary]}
                ]
                chat = model.start_chat(history=new_history)
                print("[The story so far has been recorded. The adventure continues.]\n")


    except Exception as e:
        print(f"❌ An error occurred: {e}")


if __name__ == "__main__":
    run_game()