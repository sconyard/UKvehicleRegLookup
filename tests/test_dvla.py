from unittest.mock import MagicMock

import pytest
import requests

from dvla import VehicleEnquiryClient, is_valid_reg, normalise_reg, parse_reg_list


def make_client(status=200, payload=None, exc=None):
    session = MagicMock(spec=requests.Session)
    session.headers = {}
    if exc:
        session.post.side_effect = exc
    else:
        resp = MagicMock(status_code=status)
        resp.json.return_value = payload if payload is not None else {}
        session.post.return_value = resp
    return VehicleEnquiryClient("test-key", session=session), session


@pytest.mark.parametrize("raw,expected", [(" ab12 cde ", "AB12CDE"), ("A1", "A1"), ("", ""), (None, "")])
def test_normalise_reg(raw, expected):
    assert normalise_reg(raw) == expected


@pytest.mark.parametrize("reg,valid", [("AB12CDE", True), ("A1", True), ("AB12CDEF", False), ("AB-12", False), ("", False)])
def test_is_valid_reg(reg, valid):
    assert is_valid_reg(reg) is valid


def test_parse_reg_list_splits_dedupes_and_keeps_inner_spaces():
    assert parse_reg_list("ab12 cde, XY34FGH\n\nab12cde;  k1  ") == ["AB12CDE", "XY34FGH", "K1"]


def test_requires_api_key():
    with pytest.raises(ValueError):
        VehicleEnquiryClient("")


def test_successful_lookup_sends_normalised_json_body():
    client, session = make_client(payload={"registrationNumber": "AB12CDE", "make": "FORD"})
    result = client.lookup("ab12 cde")
    assert result.ok and result.data["make"] == "FORD"
    _, kwargs = session.post.call_args
    assert kwargs["json"] == {"registrationNumber": "AB12CDE"}
    assert kwargs["timeout"] > 0
    assert session.headers["x-api-key"] == "test-key"


def test_invalid_reg_does_not_call_api():
    client, session = make_client()
    result = client.lookup("NOT-A-REG!")
    assert not result.ok
    session.post.assert_not_called()


def test_api_error_detail_is_surfaced():
    payload = {"errors": [{"status": "404", "title": "Vehicle Not Found", "detail": "Record for vehicle not found"}]}
    client, _ = make_client(status=404, payload=payload)
    result = client.lookup("AB12CDE")
    assert not result.ok and result.status_code == 404
    assert result.error == "Record for vehicle not found"


def test_falls_back_to_status_message():
    client, _ = make_client(status=403, payload={})
    assert "API key" in client.lookup("AB12CDE").error


def test_network_error_is_reported_not_raised():
    client, _ = make_client(exc=requests.ConnectionError("boom"))
    result = client.lookup("AB12CDE")
    assert not result.ok and "Could not reach" in result.error
