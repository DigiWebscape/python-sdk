"""
DigiWebscape SDK — Error Types
"""

from typing import Optional, Any


class DigiWebscapeError(Exception):
    """Base exception for all DigiWebscape API errors."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 0,
        request_id: Optional[str] = None,
        details: Optional[Any] = None
    ) -> None:
        super().__init__(f"[{code}] {message} (HTTP {status_code})")
        self.code = code
        self.message = message
        self.status_code = status_code
        self.request_id = request_id
        self.details = details
