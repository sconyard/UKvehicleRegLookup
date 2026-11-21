"""Thin client for the DVLA Vehicle Enquiry Service (VES) API.

Kept free of Streamlit so it can be unit tested and reused.
API docs: https://developer-portal.driver-vehicle-licensing.api.gov.uk/apis/vehicle-enquiry-service/vehicle-enquiry-service-description.html
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import requests

LIVE_URL = "https://driver-vehicle-licensing.api.gov.uk/vehicle-enquiry/v1/vehicles"
UAT_URL = "https://uat.driver-vehicle-licensing.api.gov.uk/vehicle-enquiry/v1/vehicles"

# UK registrations are at most 7 alphanumeric characters once spaces are removed.
_VALID_REG = re.compile(r"^[A-Z0-9]{1,7}$")

# Friendly messages for the status codes the VES API documents.
_STATUS_MESSAGES = {
    400: "Invalid registration number format.",
    403: "Access denied - check your DVLA API key.",
    404: "Vehicle not found.",
    429: "Too many requests - the API rate limit was hit, try again shortly.",
    500: "DVLA service error, try again later.",
    503: "DVLA service unavailable, try again later.",
}


def normalise_reg(reg: str) -> str:
    """Upper-case a registration and strip all whitespace, e.g. ' ab12 cde ' -> 'AB12CDE'."""
    return re.sub(r"\s+", "", reg or "").upper()


def is_valid_reg(reg: str) -> bool:
    return bool(_VALID_REG.match(reg))


def parse_reg_list(text: str) -> list[str]:
    """Split free text (commas, semicolons or new lines) into unique normalised registrations.

    Spaces inside a registration are allowed ("AB12 CDE"), so spaces are not separators.
    Order is preserved and duplicates are dropped.
    """
    regs = (normalise_reg(part) for part in re.split(r"[,;\n\r]+", text or ""))
    return list(dict.fromkeys(r for r in regs if r))


@dataclass
class LookupResult:
    registration: str
    ok: bool
    status_code: int | None = None
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class VehicleEnquiryClient:
    def __init__(
        self,
        api_key: str,
        url: str = LIVE_URL,
        timeout: float = 10.0,
        session: requests.Session | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("A DVLA API key is required.")
        self.url = url
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update({"x-api-key": api_key, "Accept": "application/json"})

    def lookup(self, registration: str) -> LookupResult:
        reg = normalise_reg(registration)
        if not is_valid_reg(reg):
            return LookupResult(reg, ok=False, error="Not a valid UK registration (max 7 letters/numbers).")

        try:
            resp = self.session.post(self.url, json={"registrationNumber": reg}, timeout=self.timeout)
        except requests.RequestException as exc:
            return LookupResult(reg, ok=False, error=f"Could not reach the DVLA API: {exc}")

        if resp.status_code == 200:
            try:
                return LookupResult(reg, ok=True, status_code=200, data=resp.json())
            except ValueError:
                return LookupResult(reg, ok=False, status_code=200, error="DVLA API returned invalid JSON.")

        return LookupResult(reg, ok=False, status_code=resp.status_code, error=_error_message(resp))


def _error_message(resp: requests.Response) -> str:
    """Prefer the API's own error detail, fall back to a friendly message for the status code."""
    try:
        errors = resp.json().get("errors") or []
        if errors:
            first = errors[0]
            detail = first.get("detail") or first.get("title")
            if detail:
                return str(detail)
    except (ValueError, AttributeError):
        pass
    return _STATUS_MESSAGES.get(resp.status_code, f"Unexpected response from DVLA API (HTTP {resp.status_code}).")
