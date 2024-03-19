def enforce_unique_categories(sorted_feedback):
    """
    Enforces that an answer is not included in multiple categories for the same question.

    Parameters:
    - sorted_feedback (dict): The sorted feedback, structured by questions and categories.

    Returns:
    - dict: The updated sorted feedback with unique categories for each answer per question.
    """
    for question, categories in sorted_feedback.items():
        seen_answers = set()
        for category, answer_keys in list(categories.items()):
            # Get unique answer keys for the category, excluding previously seen answers
            unique_keys = [key for key in answer_keys if key not in seen_answers]
            # Update the category with only unique answer keys
            sorted_feedback[question][category] = unique_keys
            # Update the set of seen answers
            seen_answers.update(unique_keys)

    return sorted_feedback
