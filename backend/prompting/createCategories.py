from openai import OpenAI
import json
import os


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

    if use_cheap_model:
        model = "gpt-3.5-turbo-1106"
        inputPrice = 0.0010
        outputPrice = 0.0020
    else:
        model = "gpt-4-0125-preview"
        inputPrice = 0.01
        outputPrice = 0.03

    # Convert data to JSON string if it's not already a string
    if not isinstance(student_feedback, str):
        json_string = json.dumps(student_feedback, indent=2)
    else:
        json_string = student_feedback

    questions_string = ", ".join(questions)

    # Prepare prompt
    prompt = (
        """
        Analyze the feedback data from students regarding a learning unit to provide a teacher with a thorough overview. The feedback student_feedback is a list structured as follows:
        - learning_unit is a string that represents the learning unit name.
        - participation is a string that represents the participation level of the student.
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
        Summary: {
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
    )

    output = response.choices[0].message.content

    response_json = json.loads(output)

    absolute_path = os.path.dirname(__file__)
    output_file_path = os.path.join(absolute_path, "data/categorize.json")

    with open(output_file_path, "w") as file:
        json.dump(response_json, file, indent=2)

    print(
        "COST: ",
        ((inputPrice * (len(prompt) / 1000)) + (outputPrice * (len(output) / 1000))),
        "$",
    )

    return response_json
