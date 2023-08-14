'''
Format Idea (to make a diameter vs distance plot)
Refrence: https://github.com/SQRLab/beam_curve_fit/blob/master/beam-profiler.py 
*This code  reads a folder with various iamges (.tif)
*Then each image is read and the diameter of the beam across the x axis is measured
(y can also be measured but they are relatively the same so only one is accounted for)
*The information of the Diameter is stored into an array as well as the distance from 
where the image was taken (taken from the file name)
*Then is able to plot the data in a scatter plot then curvefitted into the beam waist 
equation
'''
import os
from PIL import Image
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

#Gaussian functions 
def gaussianbeam(x, a, m, w, offs):
    return a*np.exp(-2*(x-m)**2/w**2)+ offs

def waist_function(z, w0, z0, off):
     #Gaussian funciton waist
    return w0*np.sqrt(1+((z-off)/z0)**2)

# Reading from the folder 397 ,includes all the 
# images at diffrent distances (mm)
root = '397_25' #can modify this for diffrent folder names
fnames = os.listdir(root)
length = len(fnames)
wavelength = fnames[0][7:10]

# Saving the names, x and y diameter measured by the camera
# and the pixels into arrays for further calculations
filenames = [] 
xDiameter = []
w_stddevs = []

#getting the images and reading them to then determine the beam diameter
for i in range(length):
    filepaths = os.path.join(root, fnames[i])
    names = fnames[i] ## to get the distance that is in the name
    filenames.append(names)

    #getting the images
    img = Image.open(filepaths)
    im = np.asarray(img).astype(float)
    if len(im.shape) > 2:
        im = im.mean(axis = -1)
    pix_len = 4.84e-6 ##defult pixel length of the camera 

    # shape of the beam 
    h, w = im.shape
    x = np.arange(w)
    y = np.arange(h)

    # fit x
    xdata = x
    ydata = im.sum(0)
    # a, m, w, offs
    p0 = (ydata.max(), xdata.max()/2, xdata.max()/4, im[0,0])
    px, cov = curve_fit(gaussianbeam, xdata, ydata, p0)
    mx, wx = px[1], abs(px[2])
    #coveriance for w
    perr = np.sqrt(np.diag(cov)) ##the error needed in the plot
    w_stddevs.append(perr[2])

    px1=pix_len*1e6
    wx1=wx*pix_len*1e6
    xDiameter.append(wx1)   

### distances away from the lens 
distance = []
for k in range(len(filenames)):
    cameradistance = 17 # mm
    d = int(filenames[k][0:3]) + cameradistance
    distance.append(d)  

###ploting the data in a diameter vs distance plot
## curve fit of the data
w0_guess = min(xDiameter)
offset_guess = distance[np.argmin(xDiameter)]
popt, _ =  curve_fit(waist_function, distance,xDiameter, sigma = w_stddevs, p0=(w0_guess,50,offset_guess))
smoothvals = np.linspace(min(distance), max(distance), 1000)
#z, w0, z0, off
print(popt[0])
yfit = waist_function(smoothvals, *popt)

plt.scatter(distance,xDiameter, color = 'orange', label = 'Expirimental', linewidths= 3)
plt.errorbar(distance, xDiameter, yerr =np.array(w_stddevs), ls = 'none', ecolor = 'b')
plt.title("Diameter vs Distance (for {} nm)".format(wavelength), fontsize = 20)
plt.xlabel('Distance in (mm)', fontsize = 15)
plt.ylabel('Diameter of the beam ($\mu$m)', fontsize = 15)
plt.plot(smoothvals, yfit, color = 'orange', label = 'Gaussian beam fit',linewidth = 3 )
plt.rc('font', size = 15)
plt.rc('axes', titlesize =15)

plt.legend()
plt.show()






