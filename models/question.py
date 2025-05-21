

class Question:
    def __init__(self, text, options, correct_option, difficulty, hint=None):
        self.text = text
        self.options = options
        self.correct_option = correct_option
        self.difficulty = difficulty
        self.hint = hint
        self.used_help = {
            "skip": False,
            "eliminate": False,
            "hint": False
        }