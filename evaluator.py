# evaluator.py

def evaluate_output(actual_output: str, expected_output: str) -> bool:
    """
    Compares actual vs expected output.
    Handles float precision and whitespace robustness.
    """
    try:
        actual = float(actual_output.strip())
        expected = float(expected_output.strip())
        return abs(actual - expected) < 1e-6
    except ValueError:
        return actual_output.strip() == expected_output.strip()