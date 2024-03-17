import torch
from flask import Flask, request, render_template
from markupsafe import escape
from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("chat.html")


@app.post("/chat")
def chat():
    user_input = request.form.get("msg")
    return get_response(user_input)


def get_response(user_input: str):
    # Let's chat for 5 lines
    for step in range(5):
        # encode the new user input, add the eos_token and return a tensor in Pytorch
        new_user_input_ids = tokenizer.encode(
            user_input + tokenizer.eos_token, return_tensors="pt"
        )

        # append the new user input tokens to the chat history
        bot_input_ids = (
            torch.cat([chat_history_ids, new_user_input_ids], dim=-1)
            if step > 0
            else new_user_input_ids
        )

        # generated a response while limiting the total chat history to 1000 tokens,
        chat_history_ids = model.generate(
            bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id
        )

        return tokenizer.decode(
            chat_history_ids[:, bot_input_ids.shape[-1] :][0],
            skip_special_tokens=True,
        )
