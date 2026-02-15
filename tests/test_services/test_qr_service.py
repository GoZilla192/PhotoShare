import pytest
from app.service.qr_service import QrService


def test_make_png_base64_returns_string():
    service = QrService()

    result = service.make_png_base64("hello")

    assert isinstance(result, str)
    assert len(result) > 0

def test_make_png_base64_returns_string():
    service = QrService()

    result = service.make_png_base64("hello")

    assert isinstance(result, str)
    assert len(result) > 0