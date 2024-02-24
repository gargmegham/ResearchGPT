import jwt
from fastapi import Request, Response
from starlette.responses import Response

from app.globals import DEBUG_MODE, JWT_SECRET
from app.logger import api_logger


async def auth(request: Request, call_next):
    """
    Exception handler middleware for FastAPI http requests
    """
    try:
        headers = request.headers
        try:
            token = headers["Authorization"].split(" ")[1]
        except KeyError:
            token = headers["authorization"].split(" ")[1]
        try:
            options = {"verify_signature": False} if DEBUG_MODE else {}
            decoded = jwt.decode(
                token, JWT_SECRET, algorithms=["HS256"], options=options
            )
        except jwt.ExpiredSignatureError as err:
            ...
        request.state.user_id = int(decoded["user_id"])
        return await call_next(request)
    except ValueError as err:
        api_logger.error(f"Value error in authentication middleware: {err}")
        return Response("Unauthorized", status_code=401)
    except AttributeError as err:
        api_logger.error(f"Attribute error in authentication middleware: {err}")
        return Response("Unauthorized", status_code=401)
    except KeyError as err:
        api_logger.error(f"Key error in authentication middleware: {err}")
        return Response("Unauthorized", status_code=401)
    except IndexError as err:
        api_logger.error(f"Index error in authentication middleware: {err}")
        return Response("Unauthorized", status_code=401)
    except jwt.PyJWTError as err:
        api_logger.error(f"Invalid token error from pyjwt\n {err}")
        return Response("Unauthorized", status_code=401)
    except Exception as err:
        api_logger.error(f"Error in authentication middleware: {err}")
        return Response("Internal server error", status_code=500)
