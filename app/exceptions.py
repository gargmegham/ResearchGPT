from dataclasses import dataclass
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


@dataclass(frozen=True)
class Responses_500:
    """ """

    middleware_exception: APIException = APIException(
        status_code=500,
        internal_code=2,
        detail="Middleware could not be initialized",
    )
    websocket_error: APIException = APIException(
        status_code=500,
        internal_code=3,
        msg="Websocket error",
        detail="Websocket error",
    )
    database_not_initialized: APIException = APIException(
        status_code=500,
        internal_code=4,
        msg="Database not initialized",
        detail="Database not initialized",
    )
    cache_not_initialized: APIException = APIException(
        status_code=500,
        internal_code=5,
        msg="Cache not initialized",
        detail="Cache not initialized",
    )
    vectorestore_not_initialized: APIException = APIException(
        status_code=500,
        detail="Vector Store not initialized",
        msg="Vector Store not initialized",
        internal_code=5,
    )


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
