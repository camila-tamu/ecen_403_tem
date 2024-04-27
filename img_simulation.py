# PACBED Image Simulation Generation Script
# Author: Tejini Murthy
# Sponsor: Samsung Austin Semiconductors
# Status: Confidential

# imports
import py4DSTEM                                         # library to make PACBED simulations
import numpy as np                                      # for matrix manipulations
import matplotlib.pyplot as plt                         # to create plots
from scipy.spatial.transform import Rotation as R       # to generate rotations for mistilt simulations
from tqdm import tqdm                                   # to loop over each rotation
from PIL import Image                                   # for TIFF formatting

print(py4DSTEM.__version__)

# function to create material structure from data
def defMaterial(positions, numbers, cell):
    material = py4DSTEM.process.diffraction.Crystal(positions, numbers, cell)
    material.plot_structure(figsize=(4,4))
    return material

# function to find 2 orthogonal axes to an axis for mistilt simulations
def findOrthogAxes(zoneAxis):
    za = np.array(zoneAxis)
    x = np.random.randn(3)      # create a 3D vector

    # use cross products to find orthogonals vectors
    o1 = np.cross(za, x)
    o2 = np.cross(za, o1)

    o1, o2 = o1 / np.linalg.norm(o1), o2 / np.linalg.norm(o2)   # normalize

    return o1, o2       # return vectors

# function to create the PACBED simulations
# use default values that can be overwritten for all parameters except material and thickness
def simImg(material, thickness, mistilt = 0, tiltStep = 0, zoneAxis = [0, 1, 1], accV = 200e3, semiAngle = 9.75, angleStep = 0):
    material.calculate_structure_factors(k_max=2.0, tol_structure_factor=0.0)   # calculate structure factors for material

    # convert the V_g to relativistic-corrected U_g
    material.calculate_dynamical_structure_factors(accV, "WK-CP", k_max=2.0, thermal_sigma=0.08, tol_structure_factor=0.0)

    # create diffraction pattern for matrix of beams
    beams = material.generate_diffraction_pattern(zone_axis_lattice=zoneAxis, tol_intensity=0., k_max=2.5, tol_excitation_error_mult=1)

    thickness *= 10     # thickness in e-10m for py4DSTEM functions

    # method for 0-tilt simulation
    if (mistilt == 0):
        # plot diffraction pattern
        py4DSTEM.process.diffraction.plot_diffraction_pattern(
            beams,
            scale_markers=1000,
            shift_labels=0.05,
            min_marker_size=0,
            figsize = (4,4),
        )

        # generate the PACBED pattern
        DP = material.generate_CBED(
            beams,
            thickness=thickness,
            alpha_mrad=semiAngle,
            pixel_size_inv_A=0.01,
            DP_size_inv_A=1.1,
            zone_axis_lattice=zoneAxis,
        )

        # plot PACBED pattern
        fig,ax = py4DSTEM.visualize.show(
            DP,
            ticks = False,
            mask_alpha = 0.99,
            returnfig=True
        )

        # save PACBED pattern image as TIFF and PNG files
        fig.savefig(f"{(thickness/10):0.0f} nm_{(mistilt):0.0f}mrad_{(tiltStep):0.0f}steps.tif")
        fig.savefig(f"{(thickness/10):0.0f} nm_{(mistilt):0.0f}mrad_{(tiltStep):0.0f}steps.png")

    # method for tilted simulations
    else:
        # get two orthogonal axes to the zone axis
        rotAxis1 = findOrthogAxes(zoneAxis)[0]
        rotAxis2 = findOrthogAxes(zoneAxis)[1]

        rot1, rot2 = mistilt, mistilt

        # create matrix of rotations
        tilt1, tilt2 = np.meshgrid(
            np.linspace(0, rot1, tiltStep), np.linspace(0, rot2, tiltStep)
        )

        fig,ax = plt.subplots(tiltStep, tiltStep, figsize=(12, 12.1))       # create subplotting for matrix of rotations in a grid for plot

        # normalize axes
        rotAxis1 = np.array(rotAxis1) / np.linalg.norm(rotAxis1)
        rotAxis2 = np.array(rotAxis2) / np.linalg.norm(rotAxis2)

        # arrays to store each pattern and tilted zone axis for PACBED patterns
        patterns = []
        tiltedZAs = []

        # loop over all the tilt values and the subplots together
        for ta, tb, a in tqdm(zip(tilt1.flat, tilt2.flat, ax.flat)):

            # generate the rotations
            Ra = R.from_rotvec(ta / 1000.0 * rotAxis1)
            Rb = R.from_rotvec(tb / 1000.0 * rotAxis2)

            tiltedZA = (Ra * Rb).apply(zoneAxis)    # rotate the original zone axis

            # generate diffraction pattern for this tilt
            pattern = Si.generate_dynamical_diffraction_pattern(
                beams=beams, thickness=thickness, zone_axis_lattice=tiltedZA
            )

            # plot the pattern in the correct axes in the figure
            py4DSTEM.process.diffraction.plot_diffraction_pattern(
                pattern,
                scale_markers=500,
                input_fig_handle=(fig, (a,)),
                add_labels=False,
                max_marker_size = 30,
            )

            # store pattern and tilted zone axis for this tilt
            patterns.append(pattern)
            tiltedZAs.append(tiltedZA)

            # set plot details for this tilt
            a.get_xaxis().set_ticks([])
            a.get_yaxis().set_ticks([])
            a.set_xlabel(None)
            a.set_ylabel(None)

        # plot rotated diffraction patterns in matrix grid
        plt.subplots_adjust(wspace=0, hspace=0)
        plt.show()

        print(len(patterns), len(tiltedZAs))    # confirm number of patterns and tilted zone axes match number of diffraction patterns
                                                # should be the same number

        # loop through each diffraction image
        for i in range(len(patterns)):
            # generate the PACBED pattern for this image
            DP = material.generate_CBED(
                patterns[i],
                thickness=thickness,
                alpha_mrad=semiAngle,
                pixel_size_inv_A=0.01,
                DP_size_inv_A=1.1,
                zone_axis_lattice=tiltedZAs[i],
            )

            # plot PACBED pattern for this image
            fig,ax = py4DSTEM.visualize.show(
                DP,
                ticks = False,
                mask_alpha = 0.99,
                returnfig=True
            )

            # save PACBED pattern image for this diffraction image as TIFF and PNG files
            fig.savefig(f"{(thickness/10):0.0f} nm_{(mistilt):0.0f}mrad_{(tiltStep):0.0f}steps_step{(i+1):0.0f}.tif")
            fig.savefig(f"{(thickness/10):0.0f} nm_{(mistilt):0.0f}mrad_{(tiltStep):0.0f}steps_step{(i+1):0.0f}.png")

# Silicon material
Si = defMaterial(
    [[0.25, 0.75, 0.25],
     [0.0,  0.0,  0.5],
     [0.25, 0.25, 0.75],
     [0.0,  0.5,  0.0],
     [0.75, 0.75, 0.75],
     [0.5,  0.0,  0.0],
     [0.75, 0.25, 0.25],
     [0.5,  0.5,  0.5],],
    14,
    5.468728
)

# loop through 1-120 nm and generate 0-tilt PACBED simulation
for i in range(1, 121):
    # no mistilt
    simImg(Si, i)

# generate tilted PACBED simulations examples
simImg(Si, 20, 10, 5)       # 20nm thickness, 10mrad mistilt, 5 tilt steps
simImg(Si, 60, 15, 4)       # 60nm thickness, 15mrad mistilt, 4 tilt steps
