import cv2
import pytesseract
from matplotlib import pyplot as plt
img_path="/Users/nikhilk/Desktop/EverythingElse/acetic_acid.png"
image=cv2.imread(img_path)
image=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
image=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
maintext=pytesseract.image_to_string(image)[5:]
print(maintext)