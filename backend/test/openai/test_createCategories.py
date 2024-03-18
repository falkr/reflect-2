from unittest.mock import MagicMock, patch

from openai import OpenAIError, RateLimitError
import pytest
from api.utils.exceptions import DataProcessingError, OpenAIRequestError
from prompting.createCategories import createCategories

"""
This test module verifies the functionality of the `createCategories` function, where he tests the function's ability
to handle successful API calls, rate limit errors, API errors, JSON decoding errors, and unexpected errors.

Each test function is decorated with `@patch("prompting.createCategories.OpenAI")`
to mock the `OpenAI` class, allowing the test to manipulate the behavior of the
`chat.completions.create` method as needed for each scenario.
"""


@patch("prompting.createCategories.OpenAI")
def test_create_categories_success(mock_openai):
    """
    Tests the successful creation of categories
    from a mocked OpenAI API response. It verifies that the function returns the
    expected output when the API call succeeds.
    """
    mock_response = MagicMock()
    mock_response.choices[0].message.content = (
        '{"Category": {"Question1": ["theme1", "theme2"]}}'
    )
    mock_openai.return_value.chat.completions.create.return_value = mock_response

    api_key = "test_api_key"
    questions = ["What did you like about this unit?", "What could be improved?"]
    student_feedback = {
        "feedback": [{"answers": ["It was informative", "More examples"], "key": 1}]
    }

    result = createCategories(api_key, questions, student_feedback)

    expected_output = {"Category": {"Question1": ["theme1", "theme2"]}}
    assert (
        result == expected_output
    ), "The function should return the expected output based on mock API response."


@patch("prompting.createCategories.OpenAI")
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
        createCategories("test_api_key", ["Question1"], {"feedback": []})
    assert "Rate limit exceeded" in str(excinfo.value)


@patch("prompting.createCategories.OpenAI")
def test_openai_api_error(mock_openai):
    """
    Tests the function's response to a general `OpenAIError`.
    It confirms that an `OpenAIRequestError` is raised with the correct message
    when the API returns an error.
    """
    mock_openai.return_value.chat.completions.create.side_effect = OpenAIError(
        "API error"
    )

    with pytest.raises(OpenAIRequestError) as excinfo:
        createCategories("test_api_key", ["Question1"], {"feedback": []})
    assert "API error" in str(excinfo.value)


@patch("prompting.createCategories.OpenAI")
def test_json_decoding_error(mock_openai):
    """
    Tests the function's behavior when the API response
    contains invalid JSON. It ensures that a `DataProcessingError` is raised with
    the appropriate message when the JSON decoding fails.
    """
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Invalid JSON"
    mock_openai.return_value.chat.completions.create.return_value = mock_response

    with pytest.raises(DataProcessingError) as excinfo:
        createCategories("test_api_key", ["Question1"], {"feedback": []})
    assert "JSON decoding error" in str(excinfo.value)


@patch("prompting.createCategories.OpenAI")
def test_unexpected_error(mock_openai):
    """
    Tests the function's behavior when an unexpected exception
    is encountered during the API call. It ensures that an `OpenAIRequestError` is
    raised with the appropriate message for unexpected errors.
    """
    mock_openai.return_value.chat.completions.create.side_effect = Exception(
        "Unexpected error"
    )

    with pytest.raises(OpenAIRequestError) as excinfo:
        createCategories("test_api_key", ["Question1"], {"feedback": []})
    assert "Unexpected error" in str(excinfo.value)
