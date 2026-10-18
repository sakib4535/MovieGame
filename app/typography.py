"""Shape Bengali share-card text, including on Windows Pillow builds without Raqm."""
from functools import lru_cache
from .config import ROOT


@lru_cache(maxsize=1)
def font_bytes():
    return (ROOT / 'web' / 'fonts' / 'NotoSansBengali.ttf').read_bytes()


def shape(text, size):
    import uharfbuzz as hb
    font = hb.Font(hb.Face(font_bytes()))
    font.scale = (size * 64, size * 64)
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(font, buffer)
    return buffer.glyph_infos, buffer.glyph_positions


def text_width(text, size):
    _, positions = shape(text, size)
    return sum(p.x_advance for p in positions) / 64


def draw_bengali(canvas, xy, text, size, color):
    import freetype
    from PIL import Image
    face = freetype.Face(str(ROOT / 'web' / 'fonts' / 'NotoSansBengali.ttf'))
    face.set_pixel_sizes(0, size)
    infos, positions = shape(text, size)
    x, baseline = xy[0], xy[1] + size
    for info, pos in zip(infos, positions):
        face.load_glyph(info.codepoint, freetype.FT_LOAD_RENDER)
        glyph = face.glyph
        bitmap = glyph.bitmap
        if bitmap.width and bitmap.rows:
            mask = Image.frombytes('L', (bitmap.width, bitmap.rows), bytes(bitmap.buffer),
                                   'raw', 'L', bitmap.pitch)
            left = round(x + pos.x_offset / 64 + glyph.bitmap_left)
            top = round(baseline - pos.y_offset / 64 - glyph.bitmap_top)
            canvas.paste(color, (left, top), mask)
        x += pos.x_advance / 64
        baseline -= pos.y_advance / 64
