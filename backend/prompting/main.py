from openai import OpenAI
import json
import os


def analyze_student_feedback(api_key, data, use_cheap_model=True):

    if use_cheap_model:
        model = "gpt-3.5-turbo-1106"
        inputPrice = 0.0010
        outputPrice = 0.0020
    else:
        model = "gpt-4-0125-preview"
        inputPrice = 0.01
        outputPrice = 0.03

    # Convert data to JSON string if it's not already a string
    if not isinstance(data, str):
        json_string = json.dumps(data, indent=2)
    else:
        json_string = data

    # Prepare prompt
    prompt = (
        """
  Analyze the student feedback data for various learning units to provide a comprehensive overview for a teacher. The analysis should:

  1. First give a summary part about the overall trends and common themes in the 'Best learning success' and 'Least understood concept' responses. Ensure every individual feedback is taken into account.
  2. Categorize and sort the feedback into meaningful groups based on similarities of themes in 'Best learning success' and 'Least understood concept'. Here you have to show every feedback in their respective category.
  3. Ensure every individual feedback is written, ensuring that none are omitted.
  4. Provide the analysis in a structured and easy-to-understand format, making it convenient for the teacher to understand the student's experiences and perspectives comprehensively.
  5. If there are feedback that is not relevant, sort them out.
  6. Create the report in this format (It's important that you include all the relevant answers in the categorized feeback):
    summary{
      best learning success{
        summary of the best learning success feedback
      }
      least learning success{
        summary of the least learning success feedback
      }
    }
    categorized feedback{
      best learning success{
        theme
        theme
        theme
        ...
      }
      least learning success{
        theme
        theme
        theme
        ...
        }
    }


  Feedback data:
  """
        + json_string
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
    output_file_path = os.path.join(absolute_path, "data/analysis_result.json")

    with open(output_file_path, "w") as file:
        json.dump(response_json, file, indent=2)

    print(
        "COST: ",
        ((inputPrice * (len(prompt) / 1000)) + (outputPrice * (len(output) / 1000))),
        "$",
    )

    return response_json
