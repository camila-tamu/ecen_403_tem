# ECEN 403/404 - Texas A&M University Electrical Engineering Capstone Project
By Camila Brigueda, Angelo Carrion, and Tejini Murthy with the help of the Analytical Engineering Team at Samsung Austin Semiconductors

<br />

# Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
    - [Database Installation](#database-installation)
    - [GUI Installation](#gui-installation)
- [Usage](#usage)

<br />

# Introduction
Welcome to the ECEN 403/404 TEM Capstone Project repository! This repository contains the code and resources for our project. Tranmission Electron Microscopy (TEM) takes an electron charged sample, positively charged probe, and acceleration voltage to capture images of the patterns. These images are then used to analyze and interpret interactions at the molecular level. Samsung Austin Semiconductor (SAS) needs a better method of determining TEM sample thickness since it is important for quantitative interpretation of energy dispersive X-ray spectrometry (EDX) and geographic phase analysis (GPA) to obtain the accurate and reliable composition measurement and strain profile.

<br />

The project aims to create an analytical database with a working graphical user interface (GUI) using the position averaged convergent beam electron diffraction (PACBED) technique. This technique is a precise and convenient TEM thickness determination technique in scanning transmission electron microscopy (STEM). A convolution neural network (CNN) will also be trained using many simulation images to receive the most accurate prediction for the sample thickness. Overall, this is essential for technology node sample preparation and imaging processes as it is more accurate and ensures mechanical stability during wafer manufacturing and device processing.

<br />

# Features

This project incorporates a variety of coding libraries such as PILLOW, SciPy, matplotlib, and others, to implement various image processing techniques such as resizing, image brightening, and image rotation. Additionally, the project uses the mean squared error (MSE) algorithm to accurately predict the thickness of TEM samples by comparing input data with a reference database. 

<br />

The GUI is designed to be visually engaging, allowing users to enter various parameters and view them in a table format. Users can also preview the selected input image within the GUI. When the "Determine Thickness" button is clicked, the corresponding output image is displayed alongside the input image, and the calculated thickness is presented in the table view for easy reference. The GUI also includes a "Save Image" button, enabling users to save the output image for future use or reference. This features make the interface user-friendly and practical for various image processing tasks.

<br />

The CNN is...  *** FILL THIS OUT ***

<br />

# Installation

To get started with this project, you can follow these steps: 

Clone the repository to your local machine:

    git clone https://github.com/camila-tamu/ecen_403_tem.git

<br />

Navigate to the project directory

    cd ecen_403_tem


<br />

   
### Database Installation:

For the database, you will need to install Miniconda or Anaconda, however, Miniconda is recommended. From the link below, you can download the appropriate version of Miniconda.

    https://docs.anaconda.com/free/miniconda/
    
<br />

Once Miniconda has been downloaded, you can open it and install it with the recommended settings. Once this is done, you can open the Miniconda Terminal and run the lines of code below. This may take some time.

    conda update conda

 <br />
 
This command will create an environment with the py4dstem modules necessary to run this application.

    conda create -n py4dstem

<br />

This command will put the user into the py4dstem environment so all the necessary modules can be used.

    conda activate py4dstem

<br />

This command is going to copy the different libraries associated with py4dstem, py4d-browser, pymatgen, and jupyterlab.

    conda install -c conda-forge py4dstem py4d-browser pymatgen jupyterlab

<br />

This command will need to be used if there is an error when installing the packages from the above line of code. 

    conda create -n foo -c conda-forge python=3.11 pyfftw

<br />

This command is going to copy the different libraries associated with ipympl and opencv.

    conda install -c conda-forge ipympl opencv

<br />

### GUI Installation:

This command allows you to use Tkinter which was the selected framework for the Python application:

    pip install tk

<br />

This command allows you to use OpenCV which is a Python library that allows you to process images:

    pip install opencv-python

<br />

This command allows you to use Pillow, which is another image processing library, and Pandas, which allows for the Table View by using pandastable:

    pip install pillow pandas pandastable

<br />

# Usage

This project will be used by Samsung Austin Semiconductors to predict the optimal TEM sample thickness measurement for various experimental TEM files. The idea is to take a .tif/.tiff file selected from the user and perform image pre-processing technqiues to make the experimental image match one of the images in the simulation database folder that the user chooses. Once all the image processing is finished, the measurement algorithm compares the processed input image with the simulations for an accurate TEM prediction. The accuracy of the measurement algorithm is used to determine the optimal sample thickness and this is important for EDX and GPA to obtain reliable composition measurements and strain profile.
