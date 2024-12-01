from typing import Optional

from fastapi import Header, HTTPException, status, Request


def check_field(field: str):
    def inner(request: Request):
        value = request.headers.get(field)
        if value is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The header field for {field} is missing",
            )
    return inner


filename_ = check_field('filename')
fileformat = check_field('Content-Type')
