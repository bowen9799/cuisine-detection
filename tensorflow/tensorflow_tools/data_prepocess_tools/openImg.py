
from PIL import Image
import sys,os
img_path=sys.argv[1]
im = Image.open(img_path)
if im == None:
    os._exit(1)
else:
    im_format = im.format
#    print(" #### file open ok",im_format)
    if im_format != "JPEG":
        im = im.convert("RGB")
        im.save(img_path, "JPEG")
        print(" convert image to RGB JPEG at:", img_path)
    im = im.convert("RGB")
    im.save(img_path, "JPEG")
    #print(" direct save image to RGB JPEG at:", img_path)

