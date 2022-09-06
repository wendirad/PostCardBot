from io import BytesIO

from aiogram import Bot

from PIL import Image, ImageDraw


async def create_postcard(postcard_image, from_user, to_user):
    """Create postcard."""

    image_byte = BytesIO()
    image_out = BytesIO()

    telegram_image = await (
        (await Bot.get_current().get_file(postcard_image)).download(
            destination_file=image_byte
        )
    )

    image = Image.open(telegram_image)

    drawer = ImageDraw.Draw(image)
    drawer.text((100, 100), from_user, (255, 255, 255))
    drawer.text((100, 200), to_user, (255, 255, 255))

    image.save(image_out, format="PNG")
    image_out.seek(0)

    return image_out
