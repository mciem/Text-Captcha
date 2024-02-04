import string
from random import randint, choices, choice

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT = "fonts/arial.ttf"
COLORS = ["black", "white", "blue", "red", "green", "cyan", "yellow", "red"]


def add_blurred_objects(image):
    dr = ImageDraw.Draw(image)

    for _ in range(randint(1, 5)):
        shape_type = randint(0, 1)

        x0, y0 = randint(0, image.width), randint(0, image.height)
        x1, y1 = x0 + randint(10, 50), y0 + randint(10, 50)

        if shape_type == 0:
            dr.rectangle((x0, y0, x1, y1), fill=(0, 0, 0, 0))
        else:
            dr.ellipse((x0, y0, x1, y1), fill=(0, 0, 0, 0))

    b_im = image.filter(ImageFilter.BoxBlur(3))

    image.paste(b_im, mask=b_im)

    return image


def add_noise(image):
    w, h = image.size
    dr = ImageDraw.Draw(image)

    for _ in range(randint(5, 15)):
        x1, y1 = randint(0, w), randint(0, h)
        x2, y2 = randint(0, w), randint(0, h)
        dr.line((x1, y1, x2, y2), fill=choice(COLORS), width=1)

    for _ in range(randint(100, 500)):
        x, y = randint(0, w), randint(0, h)
        dr.point((x, y), fill=choice(COLORS))

    return image


def apply_wave_distortion(im):
    a_range = (1, 2)
    f_range = (0.03, 0.5)
    p_range = (0, 2 * np.pi)

    a = randint(*a_range)
    f = np.random.uniform(*f_range)
    p = np.random.uniform(*p_range)

    nx, ny = im.size
    xgrid, ygrid = np.meshgrid(np.arange(nx), np.arange(ny))

    ygrid_wave = ygrid + a * np.sin(2 * np.pi * f * xgrid + p)

    image_data = np.array(im)
    n_im_data = np.zeros_like(image_data)

    for x in range(nx):
        for y in range(ny):
            xi = x
            yi = int(ygrid_wave[y, x])
            if yi >= ny or yi < 0:
                continue
            n_im_data[y, x] = image_data[yi, xi]

    n_im = Image.fromarray(n_im_data, 'RGBA')
    return n_im


def cut_and_rotate_char(s, size) -> Image:
    c_img = gen_weird_char(s, size)

    c_point = randint(1, c_img.width - 1)

    l_part = c_img.crop((0, 0, c_point, c_img.height))
    r_part = c_img.crop((c_point, 0, c_img.width, c_img.height))

    l_part = l_part.rotate(randint(-5, 5), fillcolor=(0, 0, 0, 0), expand=True)
    r_part = r_part.rotate(randint(-5, 5), fillcolor=(0, 0, 0, 0), expand=True)

    n_width = l_part.width + r_part.width + randint(1, 3)
    n_img = Image.new('RGBA', (n_width, max(l_part.height, r_part.height)), (255, 255, 255, 0))

    n_img.paste(l_part, (0, (n_img.height - l_part.height) // 2), l_part)
    n_img.paste(r_part, (l_part.width + randint(1, 3), (n_img.height - r_part.height) // 2), r_part)
    n_img = n_img.crop(n_img.getbbox())

    return n_img


def gen_weird_char(s: str, size: int) -> Image:
    im = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    dr = ImageDraw.Draw(im)

    fo = ImageFont.truetype(FONT, (size // 2) - 5)

    text_width, text_height, _, _ = dr.textbbox((0, 0), text=s, font=fo)

    x = (size - text_width) / 2
    y = (size - text_height) / 2

    dr.text((x, y), s, fill=choice(COLORS), font=fo)

    im = im.rotate(randint(-30, 30), fillcolor=(0, 0, 0, 0))
    im = apply_wave_distortion(im)

    im = im.crop(im.getbbox())
    return im


def encode(image, data) -> Image:
    e = image.copy()
    width, height = image.size

    b_data = ''.join(format(ord(c), '08b') for c in data)

    if len(b_data) > width * height:
        raise ValueError("Data is too large to be encoded in this image.")

    d_index = 0
    for row in range(height):
        for col in range(width):
            if d_index < len(b_data):
                pixel = list(e.getpixel((col, row)))
                pixel[0] = pixel[0] & ~1 | int(b_data[d_index])
                e.putpixel((col, row), tuple(pixel))
                d_index += 1
            else:
                break

    return e


def generate(n) -> list[Image, str]:
    ans = choices(string.digits + string.ascii_lowercase, k=n)

    im = Image.new("RGBA", (n * 80, 100), (255, 255, 255, 0))

    x, y = 0, 0
    for c in ans:
        ch = cut_and_rotate_char(c, 100)

        x += randint(5, 15)
        y = randint(0, 60)

        im.paste(ch, (x, y))

        x += randint(40, 100)

    im = add_noise(im)
    im = add_blurred_objects(im)
    im = encode(im, "".join(choices(string.ascii_letters, k=32)))

    im.show()

    return im, ans


generate(4)
