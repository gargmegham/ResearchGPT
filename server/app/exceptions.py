from typing import Optional


def error_codes(status_code: int, internal_code: int) -> str:
    return f"{status_code}{str(internal_code).zfill(4)}"


class APIException(Exception):
    """
    API Exception:
    - status_code: HTTP status code
    - internal_code: Internal error code
    - msg: Message for user
    - detail: Detail message for user
    - ex: Exception
    """

    status_code: int = 500
    internal_code: int = 0
    msg: Optional[str]
    detail: Optional[str]
    ex: Optional[Exception]

    def __init__(
        self,
        *,
        status_code: int,
        internal_code: int,
        msg: Optional[str] = None,
        detail: Optional[str] = None,
        ex: Optional[Exception] = None,
    ):
        self.status_code = status_code
        self.code = error_codes(status_code=status_code, internal_code=internal_code)
        self.msg = msg
        self.detail = detail
        self.ex = ex
        super().__init__(ex)

    def __call__(
        self,
        lazy_format: Optional[dict[str, str]] = None,
        ex: Optional[Exception] = None,
    ) -> "APIException":
        if self.msg is not None and self.detail is not None and lazy_format is not None:
            # lazy format for msg and detail
            self.msg = self.msg.format(**lazy_format)
            self.detail = self.detail.format(**lazy_format)
        if ex is not None:
            # set exception if exists
            self.ex = ex
        return self


class InvalidToken(APIException):
    """
    Invalid Token
    """

    status_code: int = 401
    internal_code: int = 1001
    msg: str = "Invalid Token"
    detail: str = "Invalid Token"

    def __init__(self, ex: Optional[Exception] = None):
        super().__init__(
            status_code=self.status_code,
            internal_code=self.internal_code,
            msg=self.msg,
            detail=self.detail,
            ex=ex,
        )


class MySQLConnectionError(Exception):
    """
    MySQL Connection Error
    """

    status_code: int = 500
    internal_code: int = 1001
    msg: str = "Database Connection Error"
    detail: str = "Database Connection Error"

    def __init__(self, ex: Optional[Exception] = None):
        super().__init__(
            status_code=self.status_code,
            internal_code=self.internal_code,
            msg=self.msg,
            detail=self.detail,
            ex=ex,
        )


class ChatroomNotFound(APIException):
    """
    Chatroom Not Found
    """

    status_code: int = 404
    internal_code: int = 2001
    msg: str = "Chatroom Not Found"
    detail: str = "Chatroom Not Found"

    def __init__(self, ex: Optional[Exception] = None):
        super().__init__(
            status_code=self.status_code,
            internal_code=self.internal_code,
            msg=self.msg,
            detail=self.detail,
            ex=ex,
        )


class InternalServerError(APIException):
    """
    Internal Server Error
    """

    status_code: int = 500
    internal_code: int = 9999
    msg: str = "This error is a server side error. It will be reported automatically, and we will fix it quickly."
    detail: str = "Internal Server Error"

    def __init__(self, ex: Optional[Exception] = None):
        super().__init__(
            status_code=self.status_code,
            internal_code=self.internal_code,
            msg=self.msg,
            detail=self.detail,
            ex=ex,
        )


class GptException(Exception):
    """
    Base exception for gpt related exceptions
    """

    def __init__(self, *, msg: str | None = None) -> None:
        self.msg = msg
        super().__init__()


class GptConnectionException(GptException):
    def __init__(self, *, msg: str | None = None) -> None:
        self.msg = msg
        super().__init__(msg=msg)


class GptLengthException(GptException):
    def __init__(self, *, msg: str | None = None) -> None:
        self.msg = msg
        super().__init__(msg=msg)


class GptContentFilterException(GptException):
    def __init__(self, *, msg: str | None = None) -> None:
        self.msg = msg
        super().__init__(msg=msg)


class GptTooMuchTokenException(GptException):
    def __init__(self, *, msg: str | None = None) -> None:
        self.msg = msg
        super().__init__(msg=msg)


class GptTextGenerationException(GptException):
    def __init__(self, *, msg: str | None = None) -> None:
        self.msg = msg
        super().__init__(msg=msg)


class GptOtherException(GptException):
    def __init__(self, *, msg: str | None = None) -> None:
        self.msg = msg
        super().__init__(msg=msg)


class GptModelNotImplementedException(GptException):
    def __init__(self, *, msg: str | None = None) -> None:
        self.msg = msg
        super().__init__(msg=msg)


class GptBreakException(GptException):
    def __init__(self, *, msg: str | None = None) -> None:
        self.msg = msg
        super().__init__(msg=msg)


class GptContinueException(GptException):
    def __init__(self, *, msg: str | None = None) -> None:
        self.msg = msg
        super().__init__(msg=msg)


class GptInterruptedException(GptException):
    def __init__(self, *, msg: str | None = None) -> None:
        self.msg = msg
        super().__init__(msg=msg)
