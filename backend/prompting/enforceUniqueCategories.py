def enforce_unique_categories(sorted_feedback):
    """
    Enforces that an answer is not included in multiple categories for the same question and
    removes duplicates within the same category, preserving the original order.

    Parameters:
    - sorted_feedback (dict): The sorted feedback, structured by questions and categories.

    Returns:
    - dict: The updated sorted feedback with unique categories for each answer per question.
    """
    for question, categories in sorted_feedback.items():
        seen_answers = set()
        for category, answer_keys in categories.items():
            # Remove duplicates within the same category while preserving order
            unique_within_category = []
            [
                unique_within_category.append(item)
                for item in answer_keys
                if item not in unique_within_category
            ]
            # Filter out keys already seen in other categories, preserving order
            unique_keys = [
                key for key in unique_within_category if key not in seen_answers
            ]
            # Update the category with only unique answer keys
            sorted_feedback[question][category] = unique_keys
            # Update the set of seen answers
            seen_answers.update(unique_keys)

    return sorted_feedback
