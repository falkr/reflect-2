from fastapi import HTTPException
from typing import Dict, List


def transformKeysToAnswers(
    sorted_answers: Dict[str, Dict[str, List[int]]],
    questions: List[str],
    student_feedback: List[Dict[str, List[str]]],
) -> Dict[str, Dict[str, List[str]]]:
    """
    Transforms sorted answer keys into the belonging answers from the students.

    This function returns the sorted_answers dictionary, but replaces the keys with the
    actual answers from the students from answers_data.

    Parameters:
    - sorted_answers (dict): A dictionary where each key is a question and the value is another dictionary.
      This inner dictionary maps categories to a list of keys that indicate which answers belong to that category.
    - questions (list): A list of questions in the order they were asked.
    - answers_data (list): A list of dictionaries where each dictionary contains the 'key' of the answer
      and 'answers' which is a list of answers corresponding to each question.

    Returns:
    - dict: A nested dictionary where the first level of keys are questions, the second level of keys are categories,
      and the values are lists of answers that fall into each category for the corresponding question.
    """
    updated_sorted_answers = addKeysNotIncluded(sorted_answers, student_feedback)
    feedbackWithAnswers = {}
    key_to_answers = {entry["key"]: entry["answers"] for entry in student_feedback}

    for question in questions:
        feedbackWithAnswers[question] = {}

    try:
        for question, categories in updated_sorted_answers.items():
            for category, keys in categories.items():
                # Initialize each category with an empty list for this question
                feedbackWithAnswers[question][category] = []
                for key in keys:
                    # Append the answer to the correct category
                    question_index = questions.index(question)
                    feedbackWithAnswers[question][category].append(
                        key_to_answers[key][question_index]
                    )
    except:
        raise HTTPException(
            status_code=500, detail="Failed to transform keys to answers"
        )
    return feedbackWithAnswers


def addKeysNotIncluded(
    sorted_answers: Dict[str, Dict[str, List[int]]],
    student_feedback: List[Dict[str, any]],
) -> Dict[str, Dict[str, List[int]]]:
    """
    Adds a new category to each question in the sorted_answers dictionary that lists
    all feedback keys not included in the existing categories.

    Parameters:
    - sorted_answers (dict): A nested dictionary where the first level of keys are question strings,
      the second level of keys are category names, and the values are lists of integers (keys).
    - student_feedback (list): A list of feedback entries from students. This list is used to
      determine the total number of feedback entries.

    Returns:
    - dict: The modified sorted_answers dictionary with an additional category ("Not included by AI")
      added to each question, listing all feedback keys not categorized in the existing categories.
    """
    for question, categories in sorted_answers.items():
        includedKeys = []
        for category, keys in categories.items():
            for key in keys:
                includedKeys.append(key)

        allKeys = list(range(1, len(student_feedback) + 1))
        notIncludedKeys = [num for num in allKeys if num not in includedKeys]
        sorted_answers[question]["Not included by AI"] = notIncludedKeys
    return sorted_answers
