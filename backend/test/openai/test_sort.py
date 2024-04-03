import json
from unittest.mock import MagicMock, patch

from openai import OpenAIError, RateLimitError
import pytest

from api.utils.exceptions import DataProcessingError, OpenAIRequestError
from prompting.sort import sort

"""
This test module verifies the functionality of the `sort` function, where the tests test the function's ability
to handle successful API calls, rate limit errors, API errors, JSON decoding errors, and unexpected errors. It also tests the
function's behavior when the is empty.

Each test function is decorated with `@patch("prompting.sort.OpenAI")`
to mock the `OpenAI` class, allowing the test to manipulate the behavior of the
`chat.completions.create` method as needed for each scenario.
"""


@patch("prompting.sort.OpenAI")
def test_sort_success(mock_openai):
    """
    Tests the successful sorting of feedback
    from a mocked OpenAI API response. It verifies that the function returns the
    expected output when the API call succeeds.
    """
    mock_response = MagicMock()
    mock_response.choices[0].message.content = json.dumps(
        {"Categories": {"Question1": {"category1": [1]}}}
    )
    mock_openai.return_value.chat.completions.create.return_value = mock_response

    api_key = "test_api_key"
    questions = ["What did you like about this unit?", "What could be improved?"]
    categories = {"Category": ["theme1", "theme2"]}
    feedbacks = [{"answers": ["It was informative", "More examples"], "key": 1}]

    result = sort(api_key, questions, categories, feedbacks)

    expected_output = {"Categories": {"Question1": {"category1": [1]}}}
    assert (
        result == expected_output
    ), "The function should return the expected output based on mock API response."


@patch("prompting.sort.OpenAI")
def test_rate_limit_error(mock_openai):
    """
    Tests the function's handling of a `RateLimitError`
    thrown by the OpenAI API. It ensures that an `OpenAIRequestError` is raised
    with the appropriate message when a rate limit is exceeded.
    """
    mock_openai.return_value.chat.completions.create.side_effect = RateLimitError(
        message="Rate limit exceeded",
        response=MagicMock(status_code=429),
        body="",
    )

    with pytest.raises(OpenAIRequestError) as excinfo:
        sort("test_api_key", ["Question1"], {"Category": ["theme1"]}, {"feedback": []})
    assert "Rate limit exceeded" in str(excinfo.value)


@patch("prompting.sort.OpenAI")
def test_openai_api_error(mock_openai):
    """
    Tests the function's handling of an `OpenAIError`
    thrown by the OpenAI API. It ensures that an `OpenAIRequestError` is raised
    with the appropriate message when an API error occurs.
    """
    mock_openai.return_value.chat.completions.create.side_effect = OpenAIError(
        "API error"
    )

    with pytest.raises(OpenAIRequestError) as excinfo:
        sort("test_api_key", ["Question1"], {"Category": ["theme1"]}, {"feedback": []})
    assert "API error" in str(excinfo.value)


@patch("prompting.sort.OpenAI")
def test_json_decoding_error(mock_openai):
    """
    Tests the function's handling of a JSON decoding error
    from the OpenAI API. It ensures that a `DataProcessingError` is raised with
    the appropriate message when the API response cannot be decoded.
    """
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Invalid JSON"
    mock_openai.return_value.chat.completions.create.return_value = mock_response

    with pytest.raises(DataProcessingError) as excinfo:
        sort("test_api_key", ["Question1"], {"Category": ["theme1"]}, {"feedback": []})
    assert "JSON decoding error" in str(excinfo.value)


@patch("prompting.sort.OpenAI")
def test_unexpected_error(mock_openai):
    """
    Tests the function's response to an unexpected error
    from the OpenAI API. It ensures that an `OpenAIRequestError` is raised with
    the appropriate message when an unexpected error occurs.
    """
    mock_openai.return_value.chat.completions.create.side_effect = Exception(
        "Unexpected error"
    )

    with pytest.raises(OpenAIRequestError) as excinfo:
        sort("test_api_key", ["Question1"], {"Category": ["theme1"]}, {"feedback": []})
    assert "An unexpected error occurred" in str(excinfo.value)


@patch("prompting.sort.OpenAI")
def test_empty_feedbacks(mock_openai):
    """
    Tests the function's response to an empty feedbacks input.
    It ensures that an `DataProcessingError` is raised with
    the appropriate message when an empty feedbacks is provided.
    """
    mock_openai.return_value.chat.completions.create.side_effect = MagicMock()

    api_key = "test_api_key"
    questions = ["Question1"]
    category = {"Category": ["theme1"]}

    with pytest.raises(DataProcessingError) as excinfo:
        sort(api_key, questions, category, [])
    assert "The student feedback data is empty." in str(excinfo.value)


@patch("prompting.sort.OpenAI")
def test_empty_questions(mock_openai):
    """
    Tests the function's response to an empty questions input.
    It ensures that an `DataProcessingError` is raised with
    the appropriate message when an empty questions is provided.
    """
    mock_openai.return_value.chat.completions.create.side_effect = MagicMock()

    api_key = "test_api_key"
    category = {"Category": ["theme1"]}
    feedbacks = [{"answers": ["It was informative", "More examples"], "key": 1}]

    with pytest.raises(DataProcessingError) as excinfo:
        sort(api_key, [], category, feedbacks)
    assert "The questions list is empty." in str(excinfo.value)


@patch("prompting.sort.OpenAI")
def test_empty_categories(mock_openai):
    """
    Tests the function's response to an empty categories input.
    It ensures that an `DataProcessingError` is raised with
    the appropriate message when an empty categories is provided.
    """
    mock_openai.return_value.chat.completions.create.side_effect = MagicMock()

    api_key = "test_api_key"
    questions = ["Question1"]
    feedbacks = [{"answers": ["It was informative", "More examples"], "key": 1}]

    with pytest.raises(DataProcessingError) as excinfo:
        sort(api_key, questions, {}, feedbacks)
    assert "The categories list is empty." in str(excinfo.value)
