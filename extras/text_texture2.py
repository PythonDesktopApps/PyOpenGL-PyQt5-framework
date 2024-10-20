from PIL import Image, ImageDraw, ImageFont

import pyglet.font as pfont

from core_ext.texture import Texture

class TextTexture(Texture):
    def __init__(
        self,
        text="Python graphics",
        font_name="arial",
        font_size: float=12,
        text_color=(0, 0, 0),
        width: int=0,
        height: int=0,
        h_align: str="left",
        v_align: str="top",
        background_color=(255, 255, 255)
        ):

        """
        Create a Image containing text.

        :param str text: The text to render to the image
        :param str font_name: The font to use
        :param tuple text_color: Color of the text
        :param float font_size: Size of the font
        :param int width: The width of the image in pixels
        :param int height: the height of the image in pixels
        :param str h_align: "left" or "right" aligned
        :param str v_align: "top" or "bottom" aligned
        :param tuple background_color: The background color of the image
        """

        super().__init__()
        # Scale the font up, so it matches with the sizes of the old code back
        # when Pyglet drew the text.
        font_size *= 1.25

        # Text isn't anti-aliased, so we'll draw big, and then shrink
        scale_up = 2
        scale_down = 2

        font_size *= scale_up

        # Figure out the font to use
        font_name = font_name + ".ttf"
        font = None

        font = ImageFont.truetype(font_name, int(font_size))

        # result = pfont.load("Arial")
        # font = ImageFont.truetype(result.name, int(font_size))

        # This is stupid. We have to have an image to figure out what size
        # the text will be when we draw it. Of course, we don't know how big
        # to make the image. Catch-22. So we just make a small image we'll trash
        text_image_size = [10, 10]
        image = Image.new("RGBA", text_image_size)
        draw = ImageDraw.Draw(image)

        # Get size the text will be - pillow 9.4.0
        text_image_size = draw.multiline_textsize(text, font=font)
        # Add some extra pixels at the bottom to account for letters that drop below the baseline.
        text_image_size = [text_image_size[0], text_image_size[1] + int(font_size * 0.25)]

        # Create image of proper size
        text_height = text_image_size[1]
        text_width = text_image_size[0]

        image_start_x = 0
        specified_width = width
        if specified_width == 0:
            width = text_image_size[0]
        else:
            # Wait! We were given a field width.
            if h_align == "center":
                # Center text on given field width
                field_width = width * scale_up
                image_start_x = (field_width // 2) - (text_width // 2)
            else:
                image_start_x = 0

        # Find y of top-left corner
        image_start_y = 0

        if height and v_align == "middle":
            field_height = height * scale_up
            image_start_y = (field_height // 2) - (text_height // 2)

        if height:
            text_image_size[1] = height * scale_up

        if specified_width:
            text_image_size[0] = width * scale_up

        background_color = (*background_color, 1)
        # Create image
        image = Image.new("RGBA", text_image_size, background_color)
        draw = ImageDraw.Draw(image)

        # Convert to tuple if needed, because the multiline_text does not take a
        # list for a color
        text_color = (*text_color, 1)

        draw.multiline_text(
            (image_start_x, image_start_y), text, text_color, align=h_align, font=font
        )
        self._surface = image.resize(
            (max(1, text_image_size[0] // scale_down), text_image_size[1] // scale_down),
            resample=Image.LANCZOS,
        )

        # equivalent of blit?
        self.upload_data()
