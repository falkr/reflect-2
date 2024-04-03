from fastapi import HTTPException
import pytest

from prompting.transformKeysToAnswers import addKeysNotIncluded, transformKeysToAnswers


def test_successful_transformation():
    """
    Test successful transformation of sorted answer keys into actual answers.
    """
    sorted_answers = {
        "What did you learn?": {"Positive": [1, 2], "Needs Improvement": [3]}
    }
    questions = ["What did you learn?"]
    student_feedback = [
        {"key": 1, "answers": ["Learned A"]},
        {"key": 2, "answers": ["Learned B"]},
        {"key": 3, "answers": ["Need more examples"]},
    ]

    expected_output = {
        "What did you learn?": {
            "Positive": ["Learned A", "Learned B"],
            "Needs Improvement": ["Need more examples"],
            "Not included by AI": [],
        }
    }
    assert (
        transformKeysToAnswers(sorted_answers, questions, student_feedback)
        == expected_output
    )


def test_handling_missing_keys_error():
    """
    Test the function's behavior when some keys in sorted_answers are missing from student_feedback.
    The function should raise an HTTPException indicating there are mismatched keys.
    """
    sorted_answers = {
        "What did you learn?": {
            "Positive": [1, 4],  # Assuming key 4 does not have corresponding feedback
            "Needs Improvement": [2],
            "Not included by AI": [3],
        }
    }
    questions = ["What did you learn?"]
    student_feedback = [
        {"key": 1, "answers": ["Learned A"]},
        {"key": 2, "answers": ["Could be better"]},
        {"key": 3, "answers": ["Missed class"]},
    ]

    with pytest.raises(HTTPException):
        transformKeysToAnswers(sorted_answers, questions, student_feedback)


def test_keys_not_included():
    """
    Test that keys not included in the sorted_answers are correctly added
    to the 'Not included by AI' category.
    """
    sorted_answers = {
        "What did you learn?": {"Positive": [1], "Needs Improvement": [2]}
    }
    questions = ["What did you learn?"]
    student_feedback = [
        {"key": 1, "answers": ["Learned A"]},
        {"key": 2, "answers": ["Could use more detail"]},
        {"key": 3, "answers": ["Didn't understand the assignment"]},
        {"key": 4, "answers": ["Missed the class, need recap"]},
    ]

    expected_output = {
        "What did you learn?": {
            "Positive": ["Learned A"],
            "Needs Improvement": ["Could use more detail"],
            "Not included by AI": [
                "Didn't understand the assignment",
                "Missed the class, need recap",
            ],
        }
    }

    actual_output = transformKeysToAnswers(sorted_answers, questions, student_feedback)
    assert actual_output == expected_output
