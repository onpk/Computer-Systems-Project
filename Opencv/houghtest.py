import math
import sys

import cv2
import cv2 as cv
import numpy as np
import pytesseract
import pubchempy as ppy
from PIL import Image
from math import atan,pi
from DECIMER import predict_SMILES
import re
# from sci.morphology import skeletonize

def slope(pointlist):
    a,b,c,d=pointlist
    return (d-b)/(c-a)
# def get_skeleton(bond_mask):
#     binary = bond_mask > 0
#     skeleton = skeletonize(binary)
#     return skeleton.astype(np.uint8)
def anglebetween(slopea,slopeb):
    holder=abs((slopeb-slopea)/(1+slopea*slopeb))
    radangle=atan(holder)
    return (radangle*180)/pi
def erosion(src):
    erosion_size = 0.5
    element = cv.getStructuringElement(cv.MORPH_RECT, (int(1 * erosion_size+2), int(1 * erosion_size+2)),
                                       list(map(int, (erosion_size, erosion_size))))
    erosion_dst = cv.erode(src, element)
    return erosion_dst
def remove_line_fragments(binary_img):
    # binary_img should be white=foreground (255), black=background (0)
    num_labels, labels, stats, centroids = cv.connectedComponentsWithStats(binary_img)
    cleaned = np.zeros_like(binary_img)
    for i in range(1, num_labels):
        x, y, w, h, area = stats[i]
        aspect = max(w, h) / max(1, min(w, h))  # aspect ratio
        # THESE PARAMETERS REMOVE LINE FRAGMENTS
        if area < 15:
            continue  # too small, must be noise
        if aspect > 8:
            continue  # long and thin → line fragment
        if (w <= 2 or h <= 2) and area < 40:
            continue  # thin fragment
        cleaned[labels == i] = 255
    return cleaned

def shrink_line(x1, y1, x2, y2, shrink=0.15):
    dx = x2 - x1
    dy = y2 - y1

    x1n = int(x1 + shrink * dx)
    y1n = int(y1 + shrink * dy)
    x2n = int(x2 - shrink * dx)
    y2n = int(y2 - shrink * dy)

    return x1n, y1n, x2n, y2n
def mainhough(argv):
    default_file = 'Opencv/acetic_acid.png'
    # otherfile="/Users/nikhilk/Desktop/EverythingElse/Chatpic.png"
    # print(type(argv))
    filename = argv if len(argv) > 0 else default_file
    print(filename)
    # Loads an image
    #src = cv.GaussianBlur(cv.imread(cv.samples.findFile(filename), cv.IMREAD_GRAYSCALE),(1,1),0)
    # cv.samples.addSamplesDataSearchPath("/Users/nikhilk/Desktop/Senior_Research_Stuff/Opencv")
    # src=cv.imread(filename,cv.IMREAD_GRAYSCALE)
    # src = cv.medianBlur(cv.imread(filename, cv.IMREAD_GRAYSCALE), 1)
    src=cv.imread(filename, cv.IMREAD_GRAYSCALE)
    srcn=src.cvtColor(src,cv.COLOR_BGR2GRAY) if len(src.shape)==3 else src
    thresh=cv.adaptiveThreshold(srcn,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,cv.THRESH_BINARY_INV,31,8)
    thresh=remove_line_fragments(thresh)
    lore=remove_line_fragments(thresh)
    kernel2=cv.getStructuringElement(cv.MORPH_RECT,(1,10))
    #src=cv.blur(cv.imread(cv.samples.findFile(filename), cv.IMREAD_GRAYSCALE),(3,3))
    src = erosion(src)
    # Check if image is loaded fine
    if src is None:
        print('Error opening image!')
        print('Usage: hough_lines.py [image_name -- default ' + default_file + '] \n')
        return -1

    # dst = cv.Canny(src, 150, 200, apertureSize=5, L2gradient=True)
    dst = cv.Canny(src, 120, 200)
    #dst=src

    # Copy edges to the images that will display the results in BGR
    # cdst = cv.cvtColor(dst, cv.COLOR_GRAY2BGR)
    # print(pytesseract.image_to_boxes(Image.open(otherfile)))
    cdstP = np.copy(dst)
    linesP = cv.HoughLinesP(dst, 1, np.pi / 180, 50, None, 40, 10)

    temparr=np.concatenate(linesP,axis=1).flatten()
    newarr=[temparr[i:i+4] for i in range(0,len(temparr),4) ]
    print(np.array(newarr))

    print(f"\n{linesP}")
    mask = np.zeros_like(thresh)
    slopelist=[]
    # cv.imshow("sdfsd",cdst)
    if linesP is not None:
        # for i in range(0, len(linesP)):
        #     l = linesP[i][0]
        #     cv.line(mask, (l[0], l[1]), (l[2], l[3]), (0, 0, 255), 2, cv.LINE_AA)
        for l in linesP:
            x1, y1, x2, y2 = l[0]
            cv.line(mask, (x1, y1), (x2, y2), (255, 0, 0), 2)
    cdost=cv.bitwise_and(thresh,cv.bitwise_not(mask))
    # cv.imshow("Source", mask)
    # cv.imshow("Detected Lines (in red) - Standard Hough Line Transform", cdst)
    # imask=cv.bitwise_not(mask)
    # print(cdstP)
    # print("---------")
    # print(mask)
    # cv.imshow("Detecasd", cdstP)
    # cv.imshow("Dedsfsdf - Probabilistic Line Transform", mask)
    cdstP = cv.bitwise_not(cv.bitwise_and(cdstP, mask))
    config = "--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    imgstring = pytesseract.image_to_boxes(cv.bitwise_not(cdost), config=config)

    print(imgstring)
    for line in newarr:
        slopelist.append(float(slope(line)))
    print(slopelist)
    anglelist= {}
    for i in range(len(slopelist)):
        for j in range(len(slopelist)-1):
            angleval=(anglebetween(slopelist[i], slopelist[j + 1]))
            if not math.isnan(angleval):
                anglelist[f"{slopelist[i]},{slopelist[j]}"]=(anglebetween(slopelist[i],slopelist[j+1]))
    print(anglelist)
    bitwised=cv.bitwise_not(cdost)
    cv2.imwrite("static/modified_output.jpg",bitwised)

    return bitwised,imgstring


def detect_atoms(clean_img):
    gray = cv2.cvtColor(clean_img, cv2.COLOR_BGR2GRAY)

    _, bw = cv2.threshold(gray, 0, 255,
                          cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(bw)
    atoms = []
    for i in range(1, num_labels):
        x, y = centroids[i]

        atom = {
            "id": i,
            "pos": (int(x), int(y)),
            "symbol": classify_atom(bw)
        }

        atoms.append(atom)
    return atoms
#make this more advanced later
def classify_atom(mask):
    area = np.sum(mask)

    if area < 40:
        return "H"

    if area < 150:
        return "O"

    return "C"
def extract_bonds(bond_mask):
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        bond_mask
    )
    bonds = []
    for i in range(1, num_labels):
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]

        p1 = (x, y)
        p2 = (x + w, y + h)

        bonds.append({
            "p1": p1,
            "p2": p2
        })
    return bonds
def although(argv):
    default_file = 'Opencv/acetic_acid.png'
    filename = argv if len(argv) > 0 else default_file
    gray=cv2.imread(filename,cv2.IMREAD_GRAYSCALE)
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    bw = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11, 2
    )
    if np.mean(bw) > 127:
        bw = cv2.bitwise_not(bw)
    h, w = bw.shape
    min_dim = min(h, w)
    edges = cv2.Canny(gray, 50, 150)

    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=60,
        minLineLength=int(min_dim * 0.05),
        maxLineGap=10
    )

    bond_mask = np.zeros_like(gray)

    if lines is not None:
        for x1, y1, x2, y2 in lines[:, 0]:
            # x1,y1,x2,y2=shrink_line(x1,y1, x2, y2)
            cv2.line(bond_mask, (x1, y1), (x2, y2), 255, thickness=5)
    output = gray.copy()
    output[bond_mask > 0] = 255
    pytstring=pytesseract.image_to_boxes(output, config="--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    cv2.imwrite("static/modified_output.jpg", output)
    smiles=predict_SMILES(filename)
    smiles2=smiles.replace("+","").replace("3","")
    # smiles2=re.sub(r"\d+","",smiles2)
    print(smiles2)
    vals = ppy.get_compounds(smiles2, "smiles")
    name=vals[0].iupac_name
    return output,[name,smiles2]



if __name__ == "__main__":
    cdist,res = although(sys.argv[1:])
    cdist = cv.cvtColor(cdist, cv.COLOR_BGR2RGB)
    print(res)
    cimage = Image.fromarray(cdist)
    cimage.show()

#For basic alkanes, just count the number of corners and add two to that count --> Pass that to smiles
#For alkenes and alkynes somehow distinguish between double and single bonds
#For compound with substituents, apply the previous two rules, and add the other elements after the algorithm
#Have a variable that distinguishes between cyclo compounds, normal compounds, and mixed compounds. The variable change will change how the corner count will be passed


#Next major task --> combine bondmask and letters detected to get smiles script
#Maybe can estimate the bond lines, and not get the bond lines exactly working (not many compounds have O OH and this specific set of bonds)


#What I have left to do:
#Get the bond positions from the detected files
#Learn Pubchempy
#Combine letters and bond positions into a smiles script that can be passed into pubchempy
#use the script to get the properties (idk how to do this right now)