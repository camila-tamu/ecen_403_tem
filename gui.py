import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from pandastable import Table, TableModel
import pandas as pd

"""
Team Name: Team 6
Company: Samsung Austin Semiconductor
Team Members: Camila Brigueda, Angelo Carrion, Tejini Murthy
Date: March 1, 2024

This script creates a GUI application using tkinter for loading images and displaying simulation data in a table.
"""



"""
    Opens a file dialog for the user to select an image file. The selected image is displayed in the provided label.
    Also creates a new window for user to input parameters: Accelerating Voltage, Zone Axis, and Convergence Angle.
    The input values are added to the table when the user clicks the Submit button.

    Parameters:
    ----------
    img_label : tk.Label
        The label in which the selected image will be displayed.
"""
def load_image(img_label):
    # Load the image
    file_path = filedialog.askopenfilename(filetypes = [("Image files", "*.png *.jpg *.jpeg *.tif *.tiff")])
    if file_path:
        img = Image.open(file_path)
        img = img.resize((512, 512), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)
        img_label.config(image = img)
        img_label.image = img

    # Create a new window for user input
    input_window = tk.Toplevel(window)
    input_window.title("Input Parameters")

    # Create labels and entry fields for each parameter
    voltage_label = tk.Label(input_window, text = "Accelerating Voltage:")
    voltage_label.pack()
    voltage_entry = tk.Entry(input_window)
    voltage_entry.pack()

    axis_label = tk.Label(input_window, text = "Zone Axis:")
    axis_label.pack()
    axis_entry = tk.Entry(input_window)
    axis_entry.pack()

    angle_label = tk.Label(input_window, text = "Convergence Angle:")
    angle_label.pack()
    angle_entry = tk.Entry(input_window)
    angle_entry.pack()

    # Create a button that will retrieve the input values when clicked
    submit_button = tk.Button(input_window, text = "Submit", command=lambda: retrieve_input(voltage_entry, axis_entry, angle_entry, input_window, table, df))
    submit_button.pack()



"""
    Retrieves the values from the provided entry fields, adds them to the DataFrame, and updates the table.
    Also closes the input window.

    Parameters:
    ----------
    voltage_entry : tk.Entry
        The entry field for the Accelerating Voltage.
    axis_entry : tk.Entry
        The entry field for the Zone Axis.
    angle_entry : tk.Entry
        The entry field for the Convergence Angle.
    input_window : tk.Toplevel
        The window that contains the entry fields.
    table : Table
        The table to be updated.
    df : pd.DataFrame
        The DataFrame that contains the data for the table.
"""
def retrieve_input(voltage_entry, axis_entry, angle_entry, input_window, table, df):
    voltage = voltage_entry.get()
    axis = axis_entry.get()
    angle = angle_entry.get()

    # Insert the input values to the DataFrame
    new_data = pd.DataFrame({
        'Simulation Measurements': ['Accelerating Voltage', 'Zone Axis', 'Convergence Angle'],
        'Simulation Results': [voltage, axis, angle],
    })
    df = pd.concat([df, new_data])

    # Update the table
    table.updateModel(TableModel(df))
    table.redraw()

    input_window.destroy()


window = tk.Tk()
window.grid_columnconfigure(0, weight = 1)
window.grid_rowconfigure(1, weight = 1)


# Left frame for image loading
left_frame = tk.Frame(window)
left_frame.grid(row = 0, column = 0, sticky = 'nsew')

img_label = tk.Label(left_frame)
img_label.grid(row = 0, column = 0, padx = 10, pady = 10, sticky = "nw")

load_button = tk.Button(left_frame, text = "Load Image", relief = "raised", height = 5, width = 20, font = 15, command = lambda: load_image(img_label))
load_button.grid(row = 1, column = 0, padx = 10, pady = 10, sticky = "nsew")


# Right frame for table view
right_frame = tk.Frame(window)
right_frame.grid(row = 0, column = 1, sticky = 'nsew')

data = {
    'Simulation Measurements': ['Material', 'Thickness'],
    'Simulation Results': ['Si', '20 nm'],
}

df = pd.DataFrame(data)  # Create an empty DataFrame, replace this with your data

table = Table(right_frame, dataframe = df,
    showtoolbar = True,
    showstatusbar = True,
    editable = False,
    rowheight = 100, 
    cellwidth = 250, 
    thefont = ('Calibri', 15), 
    rowheaderwidth = 250, 
    rowselectedcolor = 'light blue')
table.show()

window.mainloop()