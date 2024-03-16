import sqlite3
from difflib import get_close_matches


# Create Database connection and Create Table questions if it does not exists
def load_database(filepath: str) -> dict:
    conn = sqlite3.connect(filepath)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY,
            question TEXT NOT NULL,
            answer TEXT NOT NULL
        )
    """
    )

    return [conn, cursor]


# Load the data from table questions
def load_data_from_table(cursor):
    resp = cursor.execute("SELECT * FROM questions ORDER BY id ASC")
    return resp.fetchall()


# Store the prompts/suggestions from user to questions table
def save_data_to_table(conn, cursor, data: dict) -> None:
    cursor.execute(
        "INSERT INTO questions (question, answer) VALUES (?, ?)",
        (data["question"], data["answer"]),
    )
    conn.commit()

    return load_data_from_table(cursor)


# Find the best match from the questions table for user questions
def find_best_match(user_question: str, questions: dict) -> str | None:
    match = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return match[0] if match else None


# Get the answer for the questions
def get_answer(question: str, questions: dict) -> str:
    for s in questions:
        if question == s[1]:
            return s[2]


# Create the chat bot and perform actions
def chat_bot(filepath: str):
    try:
        conn, cursor = load_database(filepath)

        questions = load_data_from_table(cursor)

        while True:
            user_question = input("You: ")

            if user_question.lower() == "quit":
                print("Bot: Thank you for using me, Goddbye ^^")
                break

            best_match: str | None = find_best_match(
                user_question, [s[1] for s in questions]
            )

            if best_match:
                answer = get_answer(best_match, questions)
                print(f"Bot: {answer}")
            else:
                print(
                    "Bot: I don't know the answer for your question, if possible can you help with the answer?"
                )

                user_answer = input("Type answer or skip to skip: ")

                if user_answer and user_answer.lower() != "skip":
                    questions = save_data_to_table(
                        conn, cursor, {"question": user_question, "answer": user_answer}
                    )

                    print("Bot: Thank you for the answer, I learned something new ^^")

    finally:
        conn.close()


# Initialize the chat bot
if __name__ == "__main__":
    chat_bot("questions.db")
