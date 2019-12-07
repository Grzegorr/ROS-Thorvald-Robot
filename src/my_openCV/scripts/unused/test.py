import cv2
import numpy
from matplotlib import pyplot as plt

img = cv2.imread('cebulachwasty.png',0)
cv2.imshow('original',  img)
#edges = cv2.Canny(img,60,60)
#cv2.namedWindow('Canny')
#cv2.imshow('Canny',  edges)

#Checking size of the picture
shape = img.shape
#1080x1920
print(shape)

#applying Sobel in Y and X separately
gx = cv2.Sobel(img, cv2.CV_16S, 1, 0)
gy = cv2.Sobel(img, cv2.CV_16S, 0, 1)

##show sobels
#cv2.imshow('Sobel y',  gy)
#cv2.imshow('Sobel x',  gx)

orient_gradsR = numpy.empty([1080, 1920],  dtype = numpy.int8)
orient_gradsA = numpy.empty([1080, 1920])

for x in range(0, shape[0]):
    for y in range(0, shape[1]):
        r = numpy.sqrt(gx[x][y]**2 + gy[x][y]**2)
        ang = numpy.arctan2(gy[x][y], gx[x][y])
        ang_bin = int(16*ang/(2*numpy.pi))+7
        #print(gy[x][y], gx[x][y], r, ang)
        #print(int(r))
        orient_gradsR[x][y] = r
        orient_gradsA[x][y] = ang_bin
        #print(ang_bin)

#cv2.imshow('R',  orient_gradsR)


for i in range(0,img.shape[0]/20):
    for j in range(0,img.shape[1]/20):
        bins = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        #center of the cell
        x_cen = i*20
        y_cen = j*20
        print("Center of a cell:" + str(x_cen) + str(y_cen))
        for x in range(x_cen-20, x_cen+19):
            for y in range(y_cen-20, y_cen+19):
                bin = orient_gradsA[x][y]
                #print(bin)
                bins[int(bin)] += orient_gradsR[x][y]
        print(bins)
        arg1 = numpy.argmax(bins)
        bins[arg1] = 0
        arg2 = numpy.argmax(bins)
        #print(arg1)
        #print(arg2)
        if abs(arg1-arg2) == 7 or abs(arg1-arg2) == 8 or abs(arg1-arg2) == 9:
            print("HIT")
            cv2.rectangle(img, (x_cen-20,y_cen-20), (x_cen+19,y_cen+19), [0, 255, 0], thickness = -1) 

cv2.rectangle(img, (1060-20,1900-20), (1060+19,1900+19), [0, 255, 0], thickness = -1) 
cv2.imshow('detected',  img)



#bin_n = 16 # Number of bins
#bin = numpy.int32(bin_n*ang/(2*numpy.pi))
#
#bin_cells = []
#mag_cells = []
#
#cellx = celly = 8
#
#for i in range(0,img.shape[0]/celly):
#    for j in range(0,img.shape[1]/cellx):
#        bin_cells.append(bin[i*celly : i*celly+celly, j*cellx : j*cellx+cellx])
#        mag_cells.append(mag[i*celly : i*celly+celly, j*cellx : j*cellx+cellx])   
#
#hists = [numpy.bincount(b.ravel(), m.ravel(), bin_n) for b, m in zip(bin_cells, mag_cells)]
#hist = numpy.hstack(hists)


cv2.waitKey(0) 
