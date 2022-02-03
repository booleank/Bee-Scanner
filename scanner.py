from pylibdmtx import pylibdmtx
from pyzbar import pyzbar
from pyzbar.pyzbar import ZBarSymbol
from pathlib import Path

import cv2
import PIL
import glob
import sys
import shutil
import numpy as np
import os
import time

def decoder(image_path, dilate_kernel):

    '''function that takes an image path and a parameter(set, i.e (7,7))
        returns the decoded (if possible) output
    '''

    #preprocessing using opencv
    
    image = cv2.imread(image_path) #read the image
    image = cv2.resize(image, (1200,800)) #resize the image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #convert to grayscale, necessary for thresholding

    blur = cv2.GaussianBlur(gray,(5,5),0) #smooth the image to reduce noise

    #takes in an image, returns a binary image
    #algorithm determines the threshhold for each pixel based on a region around it
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, \
                                      cv2.THRESH_BINARY_INV ,5,9) 
    #increases the white region in the image
    #may require tuning depending on the location of barcode relative to other black area
    kernel = np.ones(dilate_kernel, np.uint8) 
    thresh = cv2.dilate(thresh,kernel, iterations = 1)

    #remove noise based on a kernel size 
    noise_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10,10))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, noise_kernel)

    #fill in the small holes based on a kernel size
    fill_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (8,8)) 
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, fill_kernel)

    #identify white, connected points 
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours: #iterate through each contour to find the QR code
        area = cv2.contourArea(cnt)
        if  area>1000: #conditional to filter out candidates
            perimeter =  cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt,  0.01*perimeter, True) #approximate the perimeter where constant can be changed(margin-of-error)
            xmin,ymin,width,height = cv2.boundingRect(approx) #get the coordinates of bounding rectangle around candidates
            cv2.rectangle(image, (xmin,ymin),(xmin+width, ymin+height),(0,0,255),2)
            candidate = gray[ymin : ymin + height , xmin  : xmin + width] #from the gray image, locate the candidate

            #scanners
            barcode = pyzbar.decode(candidate,symbols = [ZBarSymbol.QRCODE]) 
            dmtx = pylibdmtx.decode(candidate)

            if len(barcode) != 0:
                return bytes.decode(barcode[0][0]) #extract the QR-reading 
            elif len(dmtx) !=0 :
                return bytes.decode(dmtx[0][0]) #extract the datamatrix reading

    if len(barcode) == 0 and len(dmtx) == 0:
        return []

if __name__ == "__main__":

    start_time = time.time() #start the timer to see how long program runs
    
    path = sys.argv[1] #user needs to specify path; path refers to the second argument passed in the command prompt

    if os.path.exists(path): #check if the path exists
        
        dir = os.path.dirname(path)
        
        desk_dir = os.chdir(dir) 
        
        renamed_image_folder = "renamed images"

        #check if default folder "renamed images" exists, if so, ask user for a new name
        if os.path.exists(os.path.join(dir,renamed_image_folder)):
            renamed_image_folder = input("Since 'renamed image' file exists already, choose a different for the folder:")
        
        #make a new folder of the name inputted
        os.mkdir(renamed_image_folder)

        #change directory
        renamed_dir = os.chdir(os.path.join(dir,renamed_image_folder))
        
        renamed_images_path = os.getcwd()
        
        num_of_success = 0
        
        num_of_unsuccessful = 0
        
        print("Processing the images... This may take a while.")
        
        for file in os.listdir(path):
                
            image_path = os.path.join(path,file)
            result = decoder(image_path, (7,7))

            if len(result) != 0:
                #check if barcode reader works
                #copy the image from original, rename the file, and place into the renamed file 
                shutil.copy(image_path, os.path.join(renamed_images_path,result +".JPG")) 
                num_of_success += 1
            else:
                #check datamatrix reader 
                result = decoder(image_path,(5,5))
                if len(result) != 0:
                    shutil.copy(image_path, os.path.join(renamed_images_path,result+".JPG"))
                    num_of_success += 1
                else:
                    print("{} could not be read".format(image_path))
                    num_of_unsuccessful += 1
        print("\nTotal Renamed Images: {} \nTotal Unsuccessful Readings: {}".format\
                        (num_of_success,num_of_unsuccessful))
        print("Done")
        print("This code took %s seconds" % (time.time() - start_time))
