from lib.errors import NotFoundError, ValidationError


def test_not_found_error_has_message():
    error = NotFoundError("Product 1 not found")
    assert error.message == "Product 1 not found"


def test_not_found_error_default_message():
    error = NotFoundError()
    assert error.message == "Resource not found"


def test_validation_error_has_message_and_details():
    error = ValidationError("Invalid input", details=["name required"])
    assert error.message == "Invalid input"
    assert error.details == ["name required"]
