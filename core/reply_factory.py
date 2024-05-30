
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    if not current_question_id:
        return True, ""

    # Find the question
    question = PYTHON_QUESTION_LIST[current_question_id - 1]
    if not question:
        return False, "Invalid question ID."

    # Store the answer
    answers = session.get("answers", {})
    answers[current_question_id] = answer
    session["answers"] = answers

    # Validate the answer
    if answer not in question["options"]:
        return False, "Invalid answer."

    return True, ""


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    if current_question_id is None:
        return PYTHON_QUESTION_LIST[0]["question_text"], PYTHON_QUESTION_LIST[0]["id"]

    next_index = current_question_id
    if next_index < len(PYTHON_QUESTION_LIST):
        next_question = PYTHON_QUESTION_LIST[next_index]
        return next_question["question_text"], next_index + 1
    
    return None, None


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    answers = session.get("answers", {})
    score = sum(1 for q in PYTHON_QUESTION_LIST if answers.get(q["id"]) == q["answer"])
    return f"You have completed the quiz, Your score is {score}/{len(PYTHON_QUESTION_LIST)}."