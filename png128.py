#!/usr/bin/env python3
from PIL import Image
from PIL.Image import Resampling

image = Image.open('rpi-logo-big.png')
image.thumbnail((128, 64), Resampling.BICUBIC)
image.save('rpi-logo.png', 'PNG')
