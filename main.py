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
import ocr
import micrcopy 
import checkocr
from word2number import w2n
import re
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dir", default="C:\\Users\\dipto\\Documents\\Project\\Images",
    help="path to input image to be OCR'd")
ap.add_argument("-p", "--preprocess", type=str, default="thresh",
	help="type of preprocessing to be done")
ap.add_argument("-r", "--reference", default="C:\\Users\\dipto\\Documents\\Project\\Reference Images\\micr_e13b_reference.png",
	help="path to reference MICR E-13B font")
args = vars(ap.parse_args())
# load the directories
for root, dirs, files in os.walk(args["dir"]):
    output='['
    for name in files:
        if "TIF" or "PNG" or "JPEG" in name:
            amt=ocr.readAmount(os.path.join(root, name),args['preprocess'])
            micrfont=micrcopy.readMICR(os.path.join(root, name),args['reference'])
            amtupper = amt.upper()
            wordnum = ''
            centwordnum=''
            datanew=[]
            #Dictionary that contains the set of numerical words
            f=open("num.txt","r") 
            data = f.readlines()
            datanew =list(map(str.rstrip, data))
            f.close()
            #If the phrase"and" is not located in the check
            if "AND" not in amtupper:
                amtupper+=" AND ZERO"
            #Divides the dolalr amount and the cent amount
            dollar,cents = amtupper.split(" AND ")
            wordlst= dollar.split(' ')
            #Checks if the words in dollar is in the num.txt dictionary
            try:
                for word in wordlst:
                    if word in datanew:
                        wordnum+=word + ' '
                numamt = w2n.word_to_num(wordnum)
            except ValueError:
            #returns an "Un-Readable statement if none of the words are in the num.txt dictionary"
                amt +="(Un-Readable) "
                amtupper+="(Un-Readable) "
                numamt=0
            #turns the cents into a decimal if the cents are written as "##/100"
            try:
                num,den = cents.split( '/' )
                result = (float(num)/float(den))
                numamt+=result
            except ValueError:
            #turns the cents into a decimal if the cents are written as words
                try: 
                    centsplit=cents.split(' ')
                    for word in centsplit:
                        if word in datanew:
                            centwordnum+=word + ' '
                    centnum = w2n.word_to_num(centwordnum)
                    centamt = centnum / 100
                    numamt+=centamt
                except ValueError:
            #turns the cents into a decimal by finding the first two characters of the cent 
            # if its numerical but doesnt have a "/" symbol
                    try:
                        first2cents = cents[:2]
                        centfinal=float(float(first2cents)/100)
                        numamt+=centfinal
                    except ValueError:
            #returns an "Un-Readable statement if none of the methods above worked"
                        centword = " Un-Readable "
                        wordnum += centword
                        centzero= 0 
                        numamt+=centzero
            # T = Transit (delimit bank branch routing transit #)
            # U = On-us (delimit customer account number)
            # A = Amount (delimit transaction amount)
            # D = Dash (delimit parts of numbers, such as routing or account)
            money = '${0:.2f}'.format(numamt)
            check=checkocr.CheckOCR(name, amt, money, micrcopy.SplitIntoCatagories(micrfont))
            output=(output + '{ "Image":"' + str(check.imageName) + '", ' + 
            '"Amount Paid":"' + str(check.amtword) + '", ' + 
            '"Amount paid (number)":"' + str(check.amtnum) + '", ' + 
            '"MICR":' + '{"Original MICR Value":"' + str(micrfont) + '", ' + 
            '"Check #":"' + str(check.micr.actnum) + '", ' + 
            '"Bank Branch Routing Transit #":"' + str(check.micr.routnum) + '", ' + 
            '"Customer Account #":"' + str(check.micr.checknum) + '"}' + '},\n')
            print(name + ': ' + money)
    output=output[0:len(output)-2] + ']'
    file = open("checkoutput.json","w",encoding="utf-8") 
    file.write(output)
    file.close()
