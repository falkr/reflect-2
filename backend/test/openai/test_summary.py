from unittest.mock import MagicMock, patch

from openai import OpenAIError, RateLimitError
import pytest

from api.utils.exceptions import DataProcessingError, OpenAIRequestError
from prompting.summary import createSummary

"""
This test module verifies the functionality of the `summary` function, where he tests the function's ability
to handle successful API calls, rate limit errors, API errors, JSON decoding errors, and unexpected errors.

Each test function is decorated with `@patch("prompting.summary.OpenAI")`
to mock the `OpenAI` class, allowing the test to manipulate the behavior of the
`chat.completions.create` method as needed for each scenario.
"""


@patch("prompting.summary.OpenAI")
def test_summary_success(mock_openai):
    """
    Tests the successful creation of a summary
    from a mocked OpenAI API response. It verifies that the function returns the
    expected output when the API call succeeds.
    """
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"summary": "Here is the summary..."}'
    mock_openai.return_value.chat.completions.create.return_value = mock_response

    api_key = "test_api_key"
    answers = {
        "Category1": {
            "Question1": ["Answer1", "Answer2"],
            "Question2": ["Answer3", "Answer4"],
        },
        "Category2": {
            "Question3": ["Answer5", "Answer6"],
            "Question4": ["Answer7", "Answer8"],
        },
    }

    result = createSummary(api_key, answers)

    expected_output = {"summary": "Here is the summary..."}
    assert (
        result == expected_output
    ), "The function should return the expected output based on mock API response."


@patch("prompting.summary.OpenAI")
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
        createSummary("test_api_key", {})
    assert "Rate limit exceeded" in str(excinfo.value)


@patch("prompting.summary.OpenAI")
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
        createSummary("test_api_key", {})
    assert "API error" in str(excinfo.value)


@patch("prompting.summary.OpenAI")
def test_json_decoding_error(mock_openai):
    """
    Tests the function's behavior when the API response
    contains invalid JSON. It ensures that a `DataProcessingError` is raised with
    the appropriate message when the JSON decoding fails.
    """
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "invalid json"
    mock_openai.return_value.chat.completions.create.return_value = mock_response

    with pytest.raises(DataProcessingError) as excinfo:
        createSummary("test_api_key", {})
    assert "JSON decoding error" in str(excinfo.value)


@patch("prompting.summary.OpenAI")
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
        createSummary("test_api_key", {})
    assert "Unexpected error" in str(excinfo.value)
