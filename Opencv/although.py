# import pubchempy as ppy
# from pubchemprops.pubchemprops import *
# vals=ppy.get_compounds("O=S(=[O])(O[H])O[H]","smiles")
# lore=vals[0]
# #print(lore.record)
# # print(vals[0].synonyms)
# propstring="Wikipedia, Boiling Point, Melting Point, Flash Point, Solubility, Density, Vapor Density, Vapor Pressure, Viscosity, Heat of Combustion, Heat of Vaporization, Ionization Potential, Dissociation Constants"
# mainlist={}
# failedprops=[]
# for val in propstring.split(", "):
#     print(get_first_layer_props("1-bromo-2-methylbutane",["Complexity"]))
#     try:
#         mainlist[val]=(get_second_layer_props("1-bromo-2-methylbutane",[val])[val][0]["Value"]["StringWithMarkup"][0]["String"])
#     except (KeyError,IndexError,TypeError):
#         failedprops.append(val)
#         continue
# pluh=get_second_layer_props("acetic-acid",["Boiling Point"])["Boiling Point"][0]["Value"]["StringWithMarkup"][0]["String"]
# pluh2=get_second_layer_props("acetic-acid",["Melting Point"])["Melting Point"][0]["Value"]["StringWithMarkup"][0]["String"]
# pluh3=get_second_layer_props("acetic-acid",["Solubility"])["Solubility"][0]["Value"]["StringWithMarkup"][0]["String"]
# print(mainlist)
# print(failedprops)
import cv2
import numpy as np

# Load image (grayscale is usually best for these operations)
image = cv2.imread("/Users/nikhilk/Desktop/Senior_Research_Stuff/Computer-Systems-Project/static/sulfuric_acid.jpg", cv2.IMREAD_GRAYSCALE)

if image is None:
    raise ValueError("Image not found. Check the file path.")

# 1. Gaussian Blur
# (ksize must be odd: 3,5,7,...)
blurred = cv2.GaussianBlur(image, (5, 5), 0)

# 2. Dilation
# Create a kernel (structuring element)
erosion_size = 0.5
element = cv2.getStructuringElement(cv2.MORPH_RECT, (int(1 * erosion_size+2), int(1 * erosion_size+2)),
                                       list(map(int, (erosion_size, erosion_size))))
dilated= cv2.erode(blurred, element)

# Save or display results
cv2.imwrite("dilated.png", dilated)
# print(ppy.get_properties("Volume3D",lore.cid))