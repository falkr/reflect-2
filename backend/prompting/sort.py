from openai import OpenAI
import json
import os


def sort(api_key, questions, categorise, feedbacks, use_cheap_model=True):

    if use_cheap_model:
        model = "gpt-3.5-turbo-1106"
        inputPrice = 0.0010
        outputPrice = 0.0020
    else:
        model = "gpt-4-0125-preview"
        inputPrice = 0.01
        outputPrice = 0.03

    if isinstance(categorise, dict) and "Summary" in categorise:
        categorise_str = json.dumps(categorise["Summary"], indent=2)
    else:
        print("Error: 'categorise' is not a dictionary or does not contain 'Summary'.")
        return

    # Convert lists to JSON-formatted strings
    feedbacks_str = json.dumps(feedbacks, indent=2)
    questions_str = ", ".join(questions)

    # Prepare prompt
    prompt = (
        """
        You will receive a JSON file with feedback from students based on questions about a lecture. Each student feedback has a unique key that identifies it. Your task is to categorize this feedback based on their content into predefined categories.

        Data format on the student feedback
        Is a list of dictionaries, where each dictionary contains these keys:
        - learning_unit is a string that represents the learning unit name.
        - participation is a string that represents the participation level of the student.
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
    )

    output = response.choices[0].message.content

    response_json = json.loads(output)

    absolute_path = os.path.dirname(__file__)
    output_file_path = os.path.join(absolute_path, "data/analysis_result1.json")

    with open(output_file_path, "w") as file:
        json.dump(response_json, file, indent=2)

    print(
        "COST: ",
        ((inputPrice * (len(prompt) / 1000)) + (outputPrice * (len(output) / 1000))),
        "$",
    )

    return response_json
