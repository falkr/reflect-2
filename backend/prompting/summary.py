from typing import Dict, List
from openai import OpenAI, OpenAIError, RateLimitError
import json
from api.utils.exceptions import DataProcessingError, OpenAIRequestError


def createSummary(
    api_key, answers: Dict[str, Dict[str, List[str]]], use_cheap_model=True
) -> str:
    """
    Generates a summary of student feedback based on categorized responses using the OpenAI API.

    This function takes a dictionary of categorized student responses, formats them into a prompt,
    and uses the OpenAI API to generate a summary. The summary aims to provide key insights and an
    overview of the feedback categorized by the users.

    Parameters:
    - api_key (str): The API key required to authenticate with the OpenAI service.
    - answers (Dict[str, Dict[str, List[str]]]): A dictionary where each key represents a category,
      and its value is another dictionary mapping questions to a list of student responses.
    - use_cheap_model (bool, optional): Determines which OpenAI model to use for processing the request.
      Defaults to True, using a cheaper, less powerful model. If False, uses a more expensive,
      more powerful model.

    Returns:
    str: A string representation of a JSON object containing the generated summary.

    Side Effects:
    - Prints the estimated cost of the OpenAI API call, calculated based on the length of the prompt
      and the length of the generated output.

    Example:
    >>> api_key = "your_openai_api_key"
    >>> answers = {
        "Category1": {
            "Question1": ["Answer1", "Answer2"],
            "Question2": ["Answer3", "Answer4"]
        },
        "Category2": {
            "Question3": ["Answer5", "Answer6"],
            "Question4": ["Answer7", "Answer8"]
        }
    }
    >>> summary = createSummary(api_key, answers)
    >>> print(summary)
    {
        "summary": "Here is the summary..."
    }
    """
    try:
        if use_cheap_model:
            model = "gpt-3.5-turbo-1106"
        else:
            model = "gpt-4-0125-preview"

        if not answers:
            raise DataProcessingError("No student feedback has been provided.")

        answers_str = json.dumps(answers)

        prompt = (
            """
            You will receive a JSON file containing a categorized report based on students responding to questions from their teachers. The students' responses are sorted into appropriate categories.
            Based on this information, we need a paragraph consisting of a summary that provides an overview of the feedbacks. The summary should highlight the key points and insights into the feedbacks and overall categorise.
            Here is the data you'll have to analyze:
            """
            + answers_str
            + """
            Provide the summary in this format:
            {
                summary: here is the summary
            }
            """
        )

        client = OpenAI(api_key=api_key)

        # Call the API
        response = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant designed to output JSON. Your job is to help the teacher to sort feedbacks into the provided categorise.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )

        output = response.choices[0].message.content

        response_json = json.loads(output)

        return response_json

    except DataProcessingError:
        raise
    except RateLimitError as e:
        raise OpenAIRequestError(f"Rate limit exceeded: {str(e)}")
    except OpenAIError as e:
        raise OpenAIRequestError(f"OpenAI API error: {str(e)}")
    except json.JSONDecodeError as e:
        raise DataProcessingError(f"JSON decoding error: {str(e)}")
    except Exception as e:
        raise OpenAIRequestError(f"An unexpected error occurred: {str(e)}")
