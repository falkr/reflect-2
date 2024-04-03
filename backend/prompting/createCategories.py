from openai import OpenAI, OpenAIError, RateLimitError
import json
from api.utils.exceptions import DataProcessingError, OpenAIRequestError


def createCategories(api_key, questions, student_feedback, use_cheap_model=True):
    """
    Analyzes students' feedback on a learning unit to provide a summary of the most repeated themes
    for a teacher. It uses OpenAI's API to generate a categorization based on the feedback data.

    Parameters:
    - api_key (str): The API key for OpenAI.
    - questions (list): A list of strings representing the questions asked to students.
    - student_feedback (str, dict): The feedback data from students. Can be a dictionary or a JSON string.
    - use_cheap_model (bool, optional): Flag to decide whether to use a cheaper model or not. Defaults to True.

    Returns:
    - dict: A dictionary with the summary of themes per question based on the students' feedback.
    """
    try:
        if use_cheap_model:
            model = "gpt-3.5-turbo-1106"
        else:
            model = "gpt-4-0125-preview"

        if len(student_feedback) == 0:
            raise DataProcessingError("The student feedback data is empty.")

        if not questions:
            raise DataProcessingError("The questions list is empty.")

        json_string = json.dumps(student_feedback, indent=2)

        # Process questions to handle compound questions
        formatted_questions = []
        for question in questions:
            parts = question.rsplit("? ", 1)
            if len(parts) > 1:
                formatted_question = " AND ".join(parts[:-1]) + "? " + parts[-1]
            else:
                formatted_question = question
            formatted_questions.append(f'"{formatted_question}"')

        questions_string = "; ".join(formatted_questions)

        # Prepare prompt
        prompt = (
            """
            Analyze the feedback data from students regarding a learning unit to provide a teacher with a thorough overview. The feedback student_feedback is a list structured as follows:
            - answers: List[str] is a list of strings that represent the answers of the student for each question; answers[0] is answer for question 1, answers[1] is answer for question 2 and so on.
            - key is a int representing the key of a student's feedback. 
            Here are the students' feedback:
            """
            + json_string
            + """
            The questions asked to the students are as follows:
            """
            + questions_string
            + """Based on this information, I request the following:

            1. Create a summary that highlights the most repeated themes from the students' feedback. You do not need to mention how many belong to each theme.
        
            Please format the response as follows:
            Category: {
            Question1: [
                theme,
                theme,
                etc.
            ],
            Question2: [
                theme,
                theme,
                etc.
            ],
            ...
            }
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
                    "content": "You are a helpful assistant designed to output JSON. Your job is to help the teacher to sort what kind of information is important and what is not so the teacher can prepare for the next lecture.",
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
