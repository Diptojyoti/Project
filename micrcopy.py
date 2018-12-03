#This part of the program helps read the Magnetic Ink Character Recognition font inside the check
# import the necessary packages
from enchant import DictWithPWL
import numpy as np
import enchant
from PIL import Image
import pytesseract
from skimage.segmentation import clear_border
from imutils import contours
import imutils
import argparse
import cv2
import os
import word2number
import re
import checkocr
#Splits the MICR numbers to their given categories
def SplitIntoCatagories(micrspace):
    # T = Transit (delimit bank branch routing transit #)
    # U = On-us (delimit customer account number)
    # A = Amount (delimit transaction amount)
    # D = Dash (delimit parts of numbers, such as routing or account)
    micru = findChar('U', micrspace)
    micrt = findChar('T', micrspace)
    micrd = findChar('D', micrspace)
    micra = findChar('A', micrspace)

    return checkocr.MICR(micrd, micrt, micru)

#Seperates the micr numbers to their given sections
def findChar(char, line):
    for pos in range(len(line)):
        if line[pos]==char:
            pos+=1
            numers=''
            tempPos=pos
            while(tempPos<len(line) and line[tempPos]!=char):
                numers+=line[tempPos]
                tempPos+=1
            if tempPos==len(line):
                stringAfterPos=line[pos:]
                try:
                    posOfNexA=stringAfterPos.index('A')
                except:
                    posOfNexA=len(line)
                try:
                    posOfNexU=stringAfterPos.index('U')
                except:
                    posOfNexU=len(line)
                try:
                    posOfNexT=stringAfterPos.index('T')
                except:
                    posOfNexT=len(line)
                try:
                    posOfNexD=stringAfterPos.index('D')
                except:
                    posOfNexD=len(line)

                minpos=min(posOfNexA,posOfNexD,posOfNexT,posOfNexU)
                #adds the minimum position with position of the current letter
                numers=line[pos:pos + minpos]               
                if numers==None:
                    return ""
            return (numers.replace('U','').replace('T','').replace('A','').replace('D',''))
            

def readMICR(imgPath, refPath):
    # load the input image, grab its dimensions, and apply array slicing
    # to keep only the bottom 20% of the image (that's where the account
    # information is)
    image = cv2.imread(imgPath)
    (h, w,) = image.shape[:2]
    delta = int(h - (h * 0.15))
    bottom = image[delta:h, 0:w]

    #Converting image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    grayNOT=gray = cv2.bitwise_not(gray)
    grayNOT= cv2.threshold(grayNOT, 0, 255, cv2.THRESH_BINARY_INV |
        cv2.THRESH_OTSU)[1]

    # convert the bottom image to grayscale, then apply a blackhat
    # morphological operator to find dark regions against a light
    # background (i.e., the routing and account numbers)
    gray = cv2.cvtColor(bottom, cv2.COLOR_BGR2GRAY)

    filename = "{}.png".format(os.getpid())
    cv2.imwrite(filename, gray)
    #reading the bottom 20% of the image which should only include the MICR numbers in the check
    #DISCLAIMER: this part of the program utilizes a custom tesseract trained data 
    #which can read the MICR based font "micrencoding"
    micr = pytesseract.image_to_string(Image.open(filename),
	lang= "micrencoding")
    micrspace = "".join(micr.split())

    


    os.remove(filename)
    return(micrspace)
