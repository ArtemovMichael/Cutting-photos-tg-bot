from PIL import Image
from PIL import ImageDraw

import io


def edit_photo(downloaded_file, dimension_x, dimension_y, delta_x=0, delta_y=0):
    image = Image.open(io.BytesIO(downloaded_file))
    width, height = image.size

    left = (width // 2) - dimension_x // 2 + delta_x
    top = (height // 2) - dimension_y // 2 + delta_y
    right = (width // 2) + dimension_x // 2 + delta_x
    bottom = (height // 2) + dimension_y // 2 + delta_y

    im1 = image

    # сделал, чтобы линии всегда были видны, даже если фотка меньше чем размер, который хотят
    draw = ImageDraw.Draw(im1)
    draw.line((max(left, 0), top, max(left, 0), bottom), fill=200, width=7)  # левая
    draw.line((min(right, width), top, min(right, width), bottom), fill=200, width=7)  # правая
    draw.line((left, max(top, 0), right, max(top, 0)), fill=200, width=7)  # верхяя
    draw.line((left, min(bottom, height), right, min(bottom, height)), fill=200, width=7)  #нижняя

    # у тебя покажется результат im1.show()
    # im1 = image.crop(left, top, right, bottom)
    img_byte_arr = io.BytesIO()  # тут мы в байты переводим фотку, чтобы как документ отправить
    im1.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    img_byte_arr.name = "photo.png"

    return img_byte_arr


def crop_picture(downloaded_file, dimension_x, dimension_y, delta_x=0, delta_y=0):
    image = Image.open(io.BytesIO(downloaded_file))
    width, height = image.size

    left = (width // 2) - dimension_x // 2 + delta_x
    top = (height // 2) - dimension_y // 2 + delta_y
    right = (width // 2) + dimension_x // 2 + delta_x
    bottom = (height // 2) + dimension_y // 2 + delta_y

    im1 = image.crop((max(left, 0), max(top, 0), min(right, width), min(bottom, height)))

    img_byte_arr = io.BytesIO()  # тут мы в байты переводим фотку, чтобы как документ отправить
    im1.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    img_byte_arr.name = "photo.png"

    return img_byte_arr