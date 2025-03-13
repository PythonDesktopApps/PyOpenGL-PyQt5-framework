import pygame
import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw
from PIL import Image

from core_ext.texture import Texture

class TextTexture(Texture):
    """
    Define a text texture by using pygame
    """
    def __init__(self, text="Python graphics",
                 system_font_name="Arial",
                 font_file_name=None,
                 font_size=24,
                 font_color=(0, 0, 0),
                 background_color=(255, 255, 255),
                 transparent=False,
                 image_width=None,
                 image_height=None,
                 align_horizontal=0.0,
                 align_vertical=0.0,
                 image_border_width=0,
                 image_border_color=(0, 0, 0)):
        super().__init__()
        # Set a default font
        # font = pygame.font.SysFont(system_font_name, font_size)
        font = qtg.QFont(system_font_name, font_size)
        # The font can be overrided by loading font file
        if font_file_name is not None:
            font_id = qtg.QFontDatabase.addApplicationFont(font_file_name)
            font_str = qtg.QFontDatabase.applicationFontFamilies(font_id).at(0)
            font = qtg.QFont(font_str, font_size)
            # font = pygame.font.Font(font_file_name, font_size)
        # Render text to (antialiased) surface
        font_surface = qtw.QLabel(text)
        # TODO set antialiasing
        font_surface.setFont(font)
        font_surface.setStyleSheet("color: " + str(font_color))
        # font_surface = font.render(text, True, font_color)

        # Determine size of rendered text for alignment purposes
        fm = qtg.QFontMetrics(font)
        (text_width, text_height) = fm.width(text), fm.height()
        # If image dimensions are not specified,
        # use the font surface size as default
        if image_width is None:
            image_width = text_width
        if image_height is None:
            image_height = text_height
        # Create a surface to store the image of text
        # (with the transparency channel by default)
        # self._surface = pygame.Surface((image_width, image_height),
        #                                pygame.SRCALPHA)

        # Create a surface to store the image of text with transparency channel
        self._surface = Image.new('RGBA', (image_width, image_height), 
                                 (0, 0, 0, 0) if transparent else background_color)

        # Create a QPixmap to render the text
        pixmap = qtg.QPixmap(image_width, image_height)
        # Make it transparent if needed
        pixmap.fill(qtg.QColor(0, 0, 0, 0) if transparent else qtg.QColor(*background_color))

        # Create a painter to draw on the pixmap
        painter = qtg.QPainter(pixmap)
        painter.setFont(font)
        painter.setPen(qtg.QColor(*font_color))

        # Calculate position for text based on alignment
        x_pos = int(align_horizontal * (image_width - text_width))
        y_pos = int(align_vertical * (image_height - text_height) + fm.ascent())  # Add ascent for proper vertical alignment

        # Draw the text
        painter.drawText(x_pos, y_pos, text)

        # Add border if needed
        if image_border_width > 0:
            painter.setPen(qtg.QPen(qtg.QColor(*image_border_color), image_border_width))
            painter.drawRect(0, 0, image_width-1, image_height-1)

        painter.end()

        # Convert QPixmap to PIL Image
        qimage = pixmap.toImage().convertToFormat(qtg.QImage.Format_RGBA8888)
        ptr = qimage.bits()
        ptr.setsize(qimage.byteCount())
        self._surface = Image.frombuffer('RGBA', (qimage.width(), qimage.height()), 
                                        bytes(ptr), 'raw', 'RGBA', 0, 1)

        # No need for blit since we've already drawn the text on the pixmap
        self.upload_data()
        
