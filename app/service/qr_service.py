from __future__ import annotations

import base64
from io import BytesIO

import qrcode


class QrService:
    def make_png_base64(self, data: str) -> str:
        """
        Returns base64-encoded PNG (no data: prefix).
        """
        img = qrcode.make(data)
        buf = BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("ascii")