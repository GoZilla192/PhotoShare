import base64
from io import BytesIO

import qrcode


# move this to .env later?
QR_VERSION = 1
QR_ERROR_CORRECTION = qrcode.constants.ERROR_CORRECT_L
QR_BOX_SIZE = 10
QR_BORDER = 4


def make_qr_code(url: str) -> str:
    """
    Generates a QR code for the given URL and returns it
    as a base64-encoded PNG string.

    Example usage:
        img_str = make_qr_code('img_url')
    in HTML:
        <img src="data:image/png;base64,{img_str}" alt="QR code">
    """
    qr = qrcode.QRCode(
        version=QR_VERSION,
        error_correction=QR_ERROR_CORRECTION,
        box_size=QR_BOX_SIZE,
        border=QR_BORDER,
    )

    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")

    return base64.b64encode(buffer.getvalue()).decode("utf-8")