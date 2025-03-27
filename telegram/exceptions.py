class BotException(BaseException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class CredentialsNotFound(BotException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        