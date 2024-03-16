import json
from difflib import get_close_matches


# Load the storage file
def load_storage(filepath: str) -> dict:
    with open(filepath, "r") as file:
        storage: dict = json.load(file)

    return storage


# Store the prompts/suggestions from user to file
def save_storage(filepath: str, data: dict) -> None:
    with open(filepath, "w") as file:
        json.dump(data, file, indent=2)


# Find the best match from the storage for user questions
def find_best_match(user_question: str, questions: dict) -> str | None:
    match = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return match[0] if match else None


# Get the answer for the questions
def get_answer(question: str, storage: dict) -> str:
    for s in storage:
        if question == s["question"]:
            return s["answer"]


# Create the chat bot and perform actions
def chat_bot(filepath: str):
    storage: dict = load_storage(filepath)

    while True:
        user_question = input("You: ")

        if user_question.lower() == "quit":
            print("Bot: Thank you for using me, Goddbye ^^")
            break

        best_match: str | None = find_best_match(
            user_question, [s["question"] for s in storage]
        )

        if best_match:
            answer = get_answer(best_match, storage)
            print(f"Bot: {answer}")
        else:
            print(
                "Bot: I don't know the answer for your question, if possible can you help with the answer?"
            )

            user_answer = input("Type answer or skip to skip: ")

            if user_answer.lower() != "skip":
                storage.append({"question": user_question, "answer": user_answer})
                save_storage(filepath, storage)

                print("Bot: Thank you for the answer, I learned something new ^^")


# Initialize the chat bot
if __name__ == "__main__":
    chat_bot("storage.json")
