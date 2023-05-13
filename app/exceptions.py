from typing import Optional


def error_codes(status_code: int, internal_code: int) -> str:
    return f"{status_code}{str(internal_code).zfill(4)}"


class APIException(Exception):
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
        if (
            self.msg is not None and self.detail is not None and lazy_format is not None
        ):  # lazy format for msg and detail
            self.msg = self.msg.format(**lazy_format)
            self.detail = self.detail.format(**lazy_format)
        if ex is not None:  # set exception if exists
            self.ex = ex
        return self


class InternalServerError(APIException):
    status_code: int = 500
    internal_code: int = 9999
    msg: str = "이 에러는 서버측 에러 입니다. 자동으로 리포팅 되며, 빠르게 수정하겠습니다."
    detail: str = "Internal Server Error"

    def __init__(self, ex: Optional[Exception] = None):
        super().__init__(
            status_code=self.status_code,
            internal_code=self.internal_code,
            msg=self.msg,
            detail=self.detail,
            ex=ex,
        )


class GptException(Exception):  # Base exception for gpt
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
