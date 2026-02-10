# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import os
import aiohttp
from PIL import (Image, ImageDraw, ImageEnhance,
                 ImageFilter, ImageFont, ImageOps)

from anony import config
from anony.helpers import Track


class Thumbnail:
    def __init__(self):
        self.cfont = ImageFont.truetype("anony/helpers/cfont.ttf", 30)
        self.dfont = ImageFont.truetype("anony/helpers/font2.otf", 23)
        self.nfont = ImageFont.truetype("anony/helpers/font.ttf", 15)
        self.tfont = ImageFont.truetype("anony/helpers/font.ttf", 40)

    async def save_thumb(self, output_path: str, url: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                open(output_path, "wb").write(await resp.read())
            return output_path

    def clear(self, text):
        ctext = text.strip()[:25]
        return ctext + "..." if len(text.strip()) > 25 else ctext

    def change_size(self, maxWidth, maxHeight, image):
        ratio = min(maxWidth / image.width, maxHeight / image.height)
        newWidth = int(image.width * ratio)
        newHeight = int(image.height * ratio)
        return image.resize((newWidth, newHeight), Image.LANCZOS)

    def get_duration(self, duration: str, time="0:24"):
        m1, s1 = map(int, duration.split(":"))
        m2, s2 = map(int, time.split(":"))
        tsec = (m1 * 60 + s1) - (m2 * 60 + s2)
        min, sec = divmod(tsec, 60)
        return f"{min}:{sec:02d}"

    def make_sq(self, image):
        size = 275
        width, height = image.size
        side_length = min(width, height)
        left = (width - side_length) / 2
        top = (height - side_length) / 2
        right = (width + side_length) / 2
        bottom = (height + side_length) / 2

        crop = image.crop((left, top, right, bottom))
        resize = crop.resize((size, size), Image.LANCZOS)

        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, size, size), radius=30, fill=255)
        rounded = ImageOps.fit(resize, (size, size))
        rounded.putalpha(mask)
        return rounded

    def add_controls(self, img):
        img = self.change_size(1920, 1080, img)
        box = (460, 190, 1460, 890)
        img = img.filter(ImageFilter.GaussianBlur(25))
        region = img.crop(box)
        controls = Image.open("anony/helpers/controls.png")
        enhancer = ImageEnhance.Brightness(region)
        dark_region = enhancer.enhance(0.5)

        mask = Image.new("L", dark_region.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, box[2] - box[0], box[3] - box[1]), 40, fill=255)
        img.paste(dark_region, box, mask)
        img.paste(controls, (502, 600), controls)
        return img

    async def generate(self, song: Track) -> str:
        try:
            temp = f"cache/temp_{song.id}.jpg"
            output = f"cache/{song.id}.png"
            if os.path.exists(output):
                return output

            await self.save_thumb(temp, song.thumbnail)
            thumb = Image.open(temp).convert("RGBA")
            bg = self.add_controls(thumb)
            image = self.make_sq(thumb)
            bg.paste(image, (535, 275), image)

            draw = ImageDraw.Draw(bg)
            draw.text(
                (835, 315), "Jerry Bots", fill=(192, 192, 192), font=self.nfont
            )
            draw.text(
                (835, 355),
                self.clear(song.title),
                (255, 255, 255),
                font=self.tfont,
            )
            draw.text(
                (837, 425),
                self.clear(song.channel_name),
                (255, 255, 255),
                font=self.cfont,
            )
            draw.text(
                (1340, 630),
                self.get_duration(song.duration),
                (192, 192, 192),
                font=self.dfont,
            )
            bg.save(output)
            os.remove(temp)
            return output
        except:
            config.DEFAULT_THUMB
