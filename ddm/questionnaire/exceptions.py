class QuestionValidationError(Exception):
    def __init__(self, question, message=None, item_errors=None, scale_errors=None):
        if item_errors is None:
            item_errors = []
        if scale_errors is None:
            scale_errors = []

        question_type = question.DEFAULT_QUESTION_TYPE

        item_error_prefix = f'Item error for {question_type} {question.pk}: '
        self.item_errors = [item_error_prefix + str(e) for e in item_errors]

        scale_error_prefix = f'Scale error for {question_type} {question.pk}: '
        self.scale_errors = [scale_error_prefix + str(e) for e in scale_errors]

        error_message = f'Validation error for {question_type} {question.pk}: {message}.'

        errors = self.item_errors + self.scale_errors
        if message is not None:
            errors.append(error_message)
        self.errors = errors

        # check if message is provided and add to errors.
        super().__init__(error_message)
