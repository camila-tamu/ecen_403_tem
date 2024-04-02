import py4DSTEM
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
from tqdm import tqdm
global path
global full_path_tif
from scipy.optimize import least_squares
from PIL import Image
import numpy
import pandas as pd
import os
import cv2
import matplotlib.image as mpimg
from scipy.optimize import curve_fit
def pre_process_image(filename):
    # Load your image (replace 'your_image.tif' with your actual image path)
    image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
    
    # Thresholding to segment the TEM pattern
    _, binary_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    
    # Calculate the center of mass
    M = cv2.moments(binary_image)
    center_x = int(M["m10"] / M["m00"])
    center_y = int(M["m01"] / M["m00"])
    
    # Get image dimensions
    height, width = image.shape
    
    # Calculate the shift needed to center the TEM pattern
    shift_x = width // 2 - center_x
    shift_y = height // 2 - center_y
    
    # Shift the image
    shifted_image = np.roll(image, shift_x, axis=1)
    shifted_image = np.roll(shifted_image, shift_y, axis=0)
    
    # Save the centered image 
    center_output_filename = 'C:/Users/Angelo Carrion/Centered_Exp.tif'
    cv2.imwrite(center_output_filename, shifted_image)

    
    #start scaling the image
    image = plt.imread(center_output_filename)
    # Get the aspect ratio of the image
    aspect_ratio = image.shape[1] / image.shape[0]
    
    # Set the size of the figure based on the aspect ratio
    fig_width = 11  # Adjust as needed
    fig_height = fig_width / aspect_ratio
    
    # Create a figure with the specified size and background color
    fig = plt.figure(figsize=(fig_width, fig_height), facecolor='black')
    
    # Display the image in grayscale
    plt.imshow(image, cmap='gray')
    
    # Turn off axis
    plt.axis('off')
    
    # Save the displayed image
    blowup_output_filename = 'C:/Users/Angelo Carrion/blowup_Exp.tif'
    plt.savefig(blowup_output_filename, bbox_inches='tight', pad_inches=0)
    # Close the figure to release memory
    plt.close(fig)

    #start the resize
    image = cv2.imread(blowup_output_filename, cv2.IMREAD_GRAYSCALE)
    
    # Get the center of the image
    center_x, center_y = image.shape[1] // 2, image.shape[0] // 2
    
    # Calculate the desired dimensions of the resized image
    desired_width, desired_height = 384, 384
    
    # Calculate the cropping region
    left = max(0, center_x - desired_width // 2)
    top = max(0, center_y - desired_height // 2)
    right = min(image.shape[1], center_x + desired_width // 2)
    bottom = min(image.shape[0], center_y + desired_height // 2)
    
    # Crop the region containing the TEM pattern
    cropped_region = image[top:bottom, left:right]
    
    # Resize the cropped region to the desired dimensions
    resized_cropped_region = cv2.resize(cropped_region, (desired_width, desired_height), interpolation=cv2.INTER_LINEAR)
    
    # Save the final image
    resize_output_filename = 'C:/Users/Angelo Carrion/Resized_Exp.tif'
    cv2.imwrite(resize_output_filename, resized_cropped_region)

    #beginnning the rotattion for the image
    # Load your image
    image = cv2.imread(resize_output_filename, cv2.IMREAD_GRAYSCALE)
    
    # Preprocess the image (e.g., apply Gaussian blur, edge detection)
    blurred_image = cv2.GaussianBlur(image, (5, 5), 0)
    edges = cv2.Canny(blurred_image, 50, 150)
    
    # Find contours in the edge-detected image
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Calculate the orientation angle of the largest contour
    if contours:
        # Select the largest contour based on area
        largest_contour = max(contours, key=cv2.contourArea)
        # Fit an ellipse to the contour
        ellipse = cv2.fitEllipse(largest_contour)
        # Extract the angle of rotation from the fitted ellipse
        rotation_angle = ellipse[2]
        # Adjust rotation angle to orient the image correctly
        if ellipse[1][1] > ellipse[1][0]:
            rotation_angle += 211
    else:
        rotation_angle = 0  # Default to no rotation if no contours are found
    
    # Rotate the image by the calculated angle
    center_x, center_y = image.shape[1] // 2, image.shape[0] // 2
    rotation_matrix = cv2.getRotationMatrix2D((center_x, center_y), rotation_angle, 1.0)
    rotated_image = cv2.warpAffine(image, rotation_matrix, (image.shape[1], image.shape[0]), flags=cv2.INTER_LINEAR)
    
    # Save the rotated image
    global processed_output_file
    processed_output_filename = 'C:/Users/Angelo Carrion/processed_Exp_image.tif'
    cv2.imwrite(processed_output_filename, rotated_image)
    os.remove(center_output_filename)
    os.remove(blowup_output_filename)
    #.remove( resize_output_filename)
    return processed_output_filename


def get_best_image(filename, images):
        def linear_func(x, a, b):
            return a * x + b
        #opening both the input file and the 
        #simulated files
        img = Image.open(filename)
        sim_file = '% s' % images
        add_on="/"
        file_tif = ''.join([add_on ,sim_file])
        global full_path_tif
        full_path_tif =''.join([path ,file_tif])
        img2 = Image.open(full_path_tif).convert('L')
        imarray = numpy.array(img)
        imarray2 = numpy.array(img2)
        #reshape images into 1D arrays
        flatten_image1 = imarray.reshape(-1) # flatten the array into a 1D vector
        flatten_image2 = imarray2.reshape(-1) # flatten the array into a 1D vector
        imarray = numpy.array(flatten_image1)
        imarray2 = numpy.array(flatten_image2)
        #using curve fit, best for non-linear least square fitting methods
        params1, _ = curve_fit(linear_func, flatten_image1, flatten_image2)
        #creating the desired linear function using the input picture
        #and the paramters to create a line that should be comapred to
        fitted_line = linear_func(flatten_image1, *params1)
        mse = (np.mean((flatten_image2 - fitted_line) ** 2))/100
        #print(full_path_tif)
        #print(f'Mean Squared Error percentage: {mse}')
        return mse, full_path_tif




#input image
filename ='C:/Users/Angelo Carrion/Exp_2.tif'

    # Load the TIFF file
image = mpimg.imread(filename)
plt.figure(facecolor='black')
    # Create a new figure and display the image with black borders
plt.imshow(image, cmap='gray')
    
    # Remove axis
plt.axis('off')
    
    # Save the figure
bright_output_filename = 'C:/Users/Angelo Carrion/Bright_Exp.tif'
plt.savefig(bright_output_filename)
processed_output_file = pre_process_image(bright_output_filename)
os.remove(bright_output_filename)
list_num = []
list_name = []
for images in os.listdir(path):
    # check if the image ends with tif 
    list_num.append(get_best_image(processed_output_file, images)[0])
    list_name.append(get_best_image(processed_output_file, images)[1])
min_value = min(list_num)
min_value_name = list_name[list_num.index(min_value)]
print(min_value)
print(min_value_name)
best_fit_image = '% s' %min_value_name
img = Image.open(best_fit_image)
img.show()
img.close()
#Exp 1 - rotation angle 0
#EXp 2 - rotation angle 211