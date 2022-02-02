# CCBER-Capstone

## Scanner.py
Scanner is a script that helps read and decode barcodes/datamatrixes. The method uses preprocessing to accurately identify regions where the 
QR/Datamatrix may be. When provided a path to the image folder, the script will iterate through each image in the folder, apply the scanner method, and return the decoded value(if it exists).

The Python libraries required to run the scanner are located in the requirements.txt. To install the packages accordingly, simply use:
```
pip install -r /path/to/requirements.txt
```
