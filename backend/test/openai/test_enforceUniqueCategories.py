from prompting.enforceUniqueCategories import enforce_unique_categories


def test_no_duplicates():
    """
    Test that enforce_unique_categories leaves feedback unchanged when there are no duplicates.
    """
    sorted_feedback = {
        "Question1": {"Category1": [1, 2], "Category2": [3, 4]},
        "Question2": {"Category1": [5, 6], "Category2": [7, 8]},
    }
    expected_output = sorted_feedback.copy()
    assert (
        enforce_unique_categories(sorted_feedback) == expected_output
    ), "Function should not modify feedback without duplicates."


def test_remove_duplicates_within_same_category():
    """
    Test that duplicates within the same category are removed.
    """
    sorted_feedback = {"Question1": {"Category1": [1, 1, 2], "Category2": [3, 4, 4]}}
    expected_output = {"Question1": {"Category1": [1, 2], "Category2": [3, 4]}}
    assert (
        enforce_unique_categories(sorted_feedback) == expected_output
    ), "Function should remove duplicates within the same category."


def test_remove_duplicates_across_categories():
    """
    Test that an answer key appearing in multiple categories is retained only in the first occurrence.
    """
    sorted_feedback = {
        "Question1": {"Category1": [1, 2], "Category2": [2, 3], "Category3": [1, 4]}
    }
    expected_output = {
        "Question1": {"Category1": [1, 2], "Category2": [3], "Category3": [4]}
    }
    assert (
        enforce_unique_categories(sorted_feedback) == expected_output
    ), "Function should remove duplicates across categories."


def test_complex_scenario_with_multiple_questions():
    """
    Test a more complex scenario with multiple questions and overlapping answer keys across categories and questions.
    """
    sorted_feedback = {
        "Question1": {"Category1": [1, 2], "Category2": [2, 3, 4], "Category3": [4, 5]},
        "Question2": {"Category1": [1, 6], "Category2": [2, 7, 8], "Category3": [1, 9]},
    }
    expected_output = {
        "Question1": {"Category1": [1, 2], "Category2": [3, 4], "Category3": [5]},
        "Question2": {"Category1": [1, 6], "Category2": [2, 7, 8], "Category3": [9]},
    }
    assert (
        enforce_unique_categories(sorted_feedback) == expected_output
    ), "Function should correctly handle complex scenarios with multiple questions."
