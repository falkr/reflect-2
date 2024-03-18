from openai import OpenAI, OpenAIError, RateLimitError
import json
from api.utils.exceptions import DataProcessingError, OpenAIRequestError


def sort(api_key, questions, categories, feedbacks, use_cheap_model=True):
    """
    Sorts student feedback into predefined categories based on their content.

    This function uses the OpenAI API to process and sorts student feedback into categories.
    The categorization is based on a given set of categories and questions answered by the students.
    The output is saved to a JSON file named 'sortAnswers.json' in the current directory.

    Parameters:
    - api_key (str): The API key for OpenAI.
    - questions (list[str]): A list of questions that students answered in their feedback.
    - categorise (dict): A dictionary with a key "Category" that maps to a list of category names.
    - feedbacks (list[dict]): A list of dictionaries, where each dictionary represents a student's feedback.
                              Each feedback dictionary must have 'answers' (list[str]) and 'key' (int) as keys.
    - use_cheap_model (bool, optional): If True (default), uses a cheaper and less powerful model for processing.
                                        If False, uses a more powerful and expensive model.

    Returns:
    dict: A dictionary representing the sorted feedback according to the categories.
    """
    try:
        if use_cheap_model:
            model = "gpt-3.5-turbo-1106"
        else:
            model = "gpt-4-0125-preview"

        if "Category" in categories:
            categories_dict = categories["Category"]
        else:
            categories_dict = categories

        categorise_str = json.dumps(categories_dict, indent=2)

        # Convert lists to JSON-formatted strings
        feedbacks_str = json.dumps(feedbacks, indent=2)
        questions_str = ", ".join(questions)

        # Prepare prompt
        prompt = (
            """
            You will receive a JSON file with feedback from students based on questions about a lecture. Each student feedback has a unique key that identifies it. Your task is to categorize this feedback based on their content into predefined categories.

            Data format on the student feedback
            Is a list of dictionaries, where each dictionary contains these keys:
            - answers: List[str] is a list of strings that represent the answers of the student for each question; answers[0] is answer for question 1, answers[1] is answer for question 2 and so on.
            - key is a int representing the key of a student's feedback. Here are the students' feedback:
            Here is the feedback:
            """
            + feedbacks_str
            + """
            You will be given a number of sets of categories, here are they:
            """
            + categorise_str
            + """
            Here are the questions that the students answered:

            """
            + questions_str
            + """
            Use the key value from each piece of feedback to represent the feedback in the categorization to avoid too much text.

            Task Instructions:
            Categorization: Sort the feedback based on the questions provided above into the assigned categories.
            Format of response: Organize your answers in a structured format as shown below. Include all keys that represent 
            feedback in the relevant categories. If a piece of feedback does not fit into any of the categories, place the key under 'Other'.
            It is important that a student's feedback is only placed in one category for each question.
            The structure should look like this:

            Categories: {
                Question1: {
                    category1: [
                            1,
                            5,
                            7,
                            ...
                    ],
                    category2: [
                            2,
                            4,
                            8,
                            ...
                    ],
                    ...,
                    Other: [
                            12,
                            3,
                            3,
                            ...
                        ],
                },
                Question2: {
                    category1 [
                            1,
                            4,
                            12
                    ],
                    category2: [
                            2,
                            5,
                            7
                            ...
                    ],
                    ...
                    Other: [
                            9,
                            5,
                            8,
                            ...
                        ],
                },
                ...
            }


            Important:
            Make sure to include all keys under each question in one of the categories, if for example answers[0] does not fit into any 
            category under question 1, place it under category 'Other'.
            """
        )

        # Initialize OpenAI client
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

    except RateLimitError as e:
        raise OpenAIRequestError(f"Rate limit exceeded: {str(e)}")
    except OpenAIError as e:
        raise OpenAIRequestError(f"OpenAI API error: {str(e)}")
    except json.JSONDecodeError as e:
        raise DataProcessingError(f"JSON decoding error: {str(e)}")
    except Exception as e:
        raise OpenAIRequestError(f"An unexpected error occurred: {str(e)}")
