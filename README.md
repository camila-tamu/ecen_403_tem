# ECEN 403/404 - TEM Capstone Project
By Camila Brigueda, Angelo Carrion, and Tejini Murthy with the help of the Analytical Engineering Team at Samsung Austin Semiconductors



# Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
    - [Database Installation](#database-installation)
    - [GUI Installation](#gui-installation)
- [Usage](#usage)

# Introduction
Welcome to the ECEN 403/404 TEM Capstone Project repository! This repository contains the code and resources for our project. Tranmission Electron Microscopy (TEM) takes an electron
charged sample, positively charged probe, and acceleration voltage to capture images of the patterns. These images are then used to analyze and interpret interactions at the molecular
level. Samsung Austin Semiconductor (SAS) needs a better method of determining TEM sample thickness since it is important for quantitative interpretation of energy dispersive X-ray
spectrometry (EDX) and geographic phase analysis (GPA) to obtain the accurate and reliable composition measurement and strain profile.

<br />

The project aims to create an analytical database with a working graphical user interface (GUI) using the position averaged convergent beam electron diffraction (PACBED) technique.
This technique is a precise and convenient TEM thickness determination technique in scanning transmission electron microscopy (STEM). Overall, this is essential for technology node sample
preparation and imaging processes as it is more accurate and ensures mechanical stability during wafer manufacturing and device processing.



# Features

**FILL THIS OUT !!!!!!!!!!!!!!!!**

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

    conda create -n py4dstem

<br />

    conda activate py4dstem

<br />

    conda install -c conda-forge py4dstem py4d-browser pymatgen jupyterlab

<br />

    conda create -n foo -c conda-forge python=3.11 pyfftw

<br />
    
    conda install -c conda-forge ipympl opencv

<br />

### GUI Installation:

This allows you to use Tkinter:

    pip install tk

<br />

This allows you to use OpenCV which is a Python library that allows you to process images:

    pip install opencv-python

<br />

This allows you to use Pillow, which is another image processing library, and Pandas, which allows for the Table View
by using pandastable:

    pip install pillow pandas pandastable


# Usage

**FILL THIS OUT !!!!!!!!!!!!!!!!**


