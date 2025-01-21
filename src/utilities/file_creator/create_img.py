# create_img.py

# .png or .jpg: image files

from PIL import Image, ImageDraw

# Create an image with RGB mode and size 200x200
img = Image.new("RGB", (200, 200), color="blue")
draw = ImageDraw.Draw(img)
draw.text((50, 50), "Hello", fill="white")
img.save("./test_files/example.jpg")