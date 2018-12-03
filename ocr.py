#This part of the program helps read the cash amount given 
#and converts the amount given from string to numerical int
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
#finds the read line in the check which contains the amount paid 
def matches(lines):
	f=open("num.txt","r") 
	data = f.readlines()
	datanew =list(map(str.rstrip, data))
	score = {}
	for line in lines:
		words=line.upper().split(' ')
		score[line]=0
		for word in words:
			if word in datanew:
				score[line]+=1 
	maxline=max(score, key=score.get)
	return(maxline)

def readAmount(imgPath, preprocess):
    
    #print(os.path.join(root, name))
	image = cv2.imread(imgPath)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	#Removing some noise
	kernel = np.ones((1, 1), np.uint8)
	image = cv2.dilate(image, kernel, iterations=1)
	image = cv2.erode(image, kernel, iterations=1)
	if preprocess == "thresh":
		gray = cv2.threshold(gray, 0, 255,
			cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

	#make a check to see if median blurring should be done to remove
	#noise
	elif preprocess == "blur":
		gray = cv2.medianBlur(gray, 3)

	# write the grayscale image to disk as a temporary file so we can
	# apply OCR to it
	filename = "{}.png".format(os.getpid())
	cv2.imwrite(filename, gray)
	# load the image, apply OCR, and then delete
	# the temporary file
	Spellchecked=''
	result = pytesseract.image_to_string(Image.open(filename))
	lines=result.split('\n')
	probableLines= matches(lines)
	#Spell check and auto-correct the extracted line
	if len(probableLines) > 0:
		from enchant.checker import SpellChecker
		chkr = SpellChecker(DictWithPWL("en_US", "num.txt"))
		chkr.set_text(probableLines)
		for err in chkr:
			sug = err.suggest()
			if len(sug)>0:
				err.replace(sug[0])
		Spellchecked = chkr.get_text()
	words=Spellchecked.split(' ')
	#remove any unreadable characters
	star='*'
	for word in words:
		if star in word:
			Spellchecked=Spellchecked.replace(word, ' ')
			break
	os.remove(filename)
	return(Spellchecked)
		