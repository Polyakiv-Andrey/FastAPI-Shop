import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class EnsureSessionIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        session_id = request.cookies.get("session_id")
        response = await call_next(request)

        if not session_id:
            session_id = str(uuid.uuid4())
            if isinstance(response, Response):
                response.set_cookie(key="session_id", value=session_id)

        return response
