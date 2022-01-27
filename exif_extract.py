#!/usr/bin/env python
# coding: utf-8

# In[52]:


import os
from os import walk 
from PIL import Image #Opens images and retrieves exif
from PIL.ExifTags import TAGS #Convert exif tags from digits to names
import csv 
from os.path import join

import datetime
from fractions import Fraction


# In[220]:


image_filepath = "/Users/harpe/OneDrive/Documents/HARPER STUFF/CCBER-capstone"
csvfile = 'exifdatatest.csv'


# In[9]:


# Some use full Exif info that we will iterate over to create the columns of CSV file
# exifdataobjs = ["ExifVersion", "ShutterSpeedValue","ApertureValue", "DateTimeOriginal", "DateTimeDigitized","BrightnessValue","ExposureBiasValue","MaxApertureValue","MeteringMode","Flash",
#     "FocalLength","UserComment","ColorSpace","ExifImageWidth","FocalLengthIn35mmFilm","SceneCaptureType","ExifImageHeight","ImageWidth" ,"ImageLength","Make","Model","Orientation","YCbCrPositioning",
#     "ExposureTime","XResolution","YResolution","FNumber","FNumber","ImageUniqueID" ,"ISOSpeedRatings","ISOSpeedRatings","ISOSpeedRatings","ISOSpeedRatings","ResolutionUnit","ExifOffset",
#     "ExposureMode","FlashPixVersion","WhiteBalance" ,"Software","DateTime","MakerNote"]
# len(exifdataobjs)


# In[176]:


# def _derationalize(rational):
#     return rational[0] / rational[1]

def create_lookups():
    lookups = {}

    lookups["metering_modes"] = ("Undefined",
                                 "Average",
                                 "Center-weighted average",
                                 "Spot",
                                 "Multi-spot",
                                 "Multi-segment",
                                 "Partial")

    lookups["exposure_programs"] = ("Undefined",
                                    "Manual",
                                    "Program AE",
                                    "Aperture-priority AE",
                                    "Shutter speed priority AE",
                                    "Creative (Slow speed)",
                                    "Action (High speed)",
                                    "Portrait ",
                                    "Landscape",
                                    "Bulb")

    lookups["resolution_units"] = ("",
                                   "Undefined",
                                   "Inches",
                                   "Centimetres")

    lookups["orientations"] = ("",
                               "Horizontal",
                               "Mirror horizontal",
                               "Rotate 180",
                               "Mirror vertical",
                               "Mirror horizontal and rotate 270 CW",
                               "Rotate 90 CW",
                               "Mirror horizontal and rotate 90 CW",
                               "Rotate 270 CW")
    
    lookups["color_space"] = ("","sRBG","Adobe RGB")
    
    lookups["white-balance"] = ("Auto","Manual")
    
    lookups["exposure-mode"] = ("Auto","Manual","Auto bracket")
    
    lookups["ycbcr-positioning"] = ("","Centered","Co-sited")

    return lookups


# In[211]:


def process_exif_dict(exif_dict): # defines function to make exif info human-readable
    date_format = "%Y:%m:%d %H:%M:%S"

    lookups = create_lookups()

    exif_dict["DateTimeOriginal"] =         datetime.datetime.strptime(exif_dict["DateTimeOriginal"], date_format)

    exif_dict["DateTimeDigitized"] =         datetime.datetime.strptime(exif_dict["DateTimeDigitized"], date_format)

    exif_dict["ColorSpace"] = lookups["color_space"][exif_dict["ColorSpace"]]
    
#    exif_dict["FNumber"] = \
#        _derationalize(exif_dict["FNumber"])
    exif_dict["FNumber"] =         "f/{}".format(exif_dict["FNumber"])

    try:
        exif_dict["MaxApertureValue"] = float(exif_dict["MaxApertureValue"])
        exif_dict["MaxApertureValue"] = "f/{:2.1f}".format(exif_dict["MaxApertureValue"])
    except:
        pass
    
#     exif_dict["FocalLength"] = \
#         _derationalize(exif_dict["FocalLength"])
    exif_dict["FocalLength"] = float(exif_dict["FocalLength"])
    exif_dict["FocalLength"] =         "{}mm".format(exif_dict["FocalLength"])
    
    try:
        exif_dict["FocalLengthIn35mmFilm"] = "{}mm".format(exif_dict["FocalLengthIn35mmFilm"])
    except:
        pass
    
    try:
        exif_dict["Orientation"] =             lookups["orientations"][exif_dict["Orientation"]]
    except:
        pass

    exif_dict["ResolutionUnit"] =         lookups["resolution_units"][exif_dict["ResolutionUnit"]]

    exif_dict["ExposureProgram"] =         lookups["exposure_programs"][exif_dict["ExposureProgram"]]

    exif_dict["MeteringMode"] =         lookups["metering_modes"][exif_dict["MeteringMode"]]

    exif_dict["WhiteBalance"] = lookups["white-balance"][exif_dict["WhiteBalance"]]

#     exif_dict["XResolution"] = \
#         int(_derationalize(exif_dict["XResolution"]))

#     exif_dict["YResolution"] = \
#         int(_derationalize(exif_dict["YResolution"]))

#     exif_dict["ExposureTime"] = \
#         _derationalize(exif_dict["ExposureTime"])
#     exif_dict["ExposureTime"] = \
#         str(Fraction(exif_dict["ExposureTime"]).limit_denominator(8000))

    exif_dict["ExposureBiasValue"] = format(float(exif_dict["ExposureBiasValue"]),".2f")
    #exif_dict["ExposureBiasValue"] = str(Fraction(float(exif_dict["ExposureBiasValue"])))
    exif_dict["ExposureBiasValue"] = "{} EV".format(exif_dict["ExposureBiasValue"])
        
    exif_dict["ExposureMode"] = lookups["exposure-mode"][exif_dict["ExposureMode"]]

    exif_dict["YCbCrPositioning"] = lookups["ycbcr-positioning"][exif_dict["YCbCrPositioning"]]
    
    return exif_dict


# In[221]:


def get_exif(fn): #Defining a function that opens an image, retrieves the exif data, corrects the exif tags from digits to names and puts the data into a dictionary
    i = Image.open(fn)   
    info = i._getexif()
    ret = {TAGS.get(tag, tag): value for tag, value in info.items()}
    exif_processed = process_exif_dict(ret)
    return exif_processed


# In[215]:


# def get_exif_pre(fn): #Defining a function that opens an image, retrieves the exif data, corrects the exif tags from digits to names and puts the data into a dictionary
#     i = Image.open(fn)   
#     info = i._getexif()
#     ret = {TAGS.get(tag, tag): value for tag, value in info.items()}
#     return ret


# In[228]:


exifdataobjs = ["ExifVersion","FNumber","MaxApertureValue","DateTimeOriginal", "DateTimeDigitized","DateTime","BrightnessValue","MeteringMode","Flash",
    "FocalLength","FocalLengthIn35mmFilm","ColorSpace","SceneCaptureType","ExifImageWidth","ExifImageHeight","Make","Model","Orientation","YCbCrPositioning",
     "ShutterSpeedValue","ExposureTime","ExposureMode","ExposureBiasValue","XResolution","YResolution","ResolutionUnit","ISOSpeedRatings","ExifOffset",
    "WhiteBalance" ,"Software"]


# In[229]:


Paths = [join(root, f).replace(os.sep,"/") for root, dirs, files in walk(image_filepath, topdown=True) for f in files if f.endswith('.JPG' or '.jpg')] #Creates list of paths for images

Filenames = [f for root, dirs, files in walk(image_filepath, topdown=True) for f in files if f.endswith(('.JPG' ,'.jpg'))] #Creates list of filenames for images
ExifData = list(map(get_exif, Paths)) # might have to iterate over files differently
#ExifData = list(map(get_exif_pre, Paths))


# In[79]:


len(ExifData) # this should be 29 but it is only taking .JPG (17) and not .jpg files 


# In[230]:


# iterate through diff exif variables and to prepare data for csv
num_lists = int(len(exifdataobjs))
lists = [[] for i in range(num_lists)]

i = 0

for obj in exifdataobjs:
    for j in ExifData:
        if obj in j: # trying to get rid of na error
            lists[i].append(j[obj])
        else:
            lists[i].append('NA')
    i+=1
    if i == len(exifdataobjs):
        break


# In[233]:


zipped = zip(*lists) #Combines the lists to be written into a csv.

with open(csvfile, "w", newline='') as f: #Writes a csv-file with the exif data
    writer = csv.writer(f)
    writer.writerow(exifdataobjs) # add exifdataobjs
    for row in zipped:
        writer.writerow(row)

