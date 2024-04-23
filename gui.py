import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from pandastable import Table, TableModel
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import Database

"""
    Team Name: Team 6 - Analytical Database for TEM Sample Thickness Determination
    Company: Samsung Austin Semiconductor
    Team Members: Camila Brigueda, Angelo Carrion, Tejini Murthy
    Date: April 9, 2024

    This script creates a GUI application using tkinter for loading images and displaying simulation data in a table.
"""



"""
    Converts an image file to TIFF format.

    This function opens an image file, converts it to TIFF format, and saves the new image. 
    The new image has the same name as the original file but with a '.tif' extension.

    Parameters:
    ----------
    file_path : str
        The path to the image file to be converted.

    Returns:
    -------
    str
        The path to the newly created TIFF image.    
"""
def convert_to_tif(file_path):
    img = Image.open(file_path)
    new_file_path = file_path.rsplit('.', 1)[0] + '.tif'
    img.save(new_file_path, 'TIFF')

    return new_file_path



"""
    Clears the canvas of any images. Opens a file dialog for the user to select an image file. 
    The selected image is displayed in the provided label. Also creates a new window for user to input 
    parameters: Accelerating Voltage, Zone Axis, and Convergence Angle. The input values are added to
    the table when the user clicks the Submit button.

    Parameters:
    ----------
    input_img_label : tk.Label
        The label in which the selected image will be displayed.
"""
loaded_image = None
file_path = None
def load_image(input_img_label):
    global loaded_image
    global file_path

    # Clear Canvas
    for widget in input_img_label.winfo_children():
        widget.destroy()

    empty_image = tk.PhotoImage()
    input_img_label.config(image = empty_image)
    input_img_label.image = empty_image
    input_img_label.config(image = empty_image)
    input_img_label.image = empty_image

    file_path = filedialog.askopenfilename(filetypes = [("Image files", "*.png *.jpg *.jpeg *.tif *.tiff")])

    if not file_path:
        return
    if file_path:
        if file_path.lower().endswith('.tif') or file_path.lower().endswith('.tiff'):
            tif_file_path = file_path
        else:
            tif_file_path = convert_to_tif(file_path)

        img = Image.open(tif_file_path)
        fig = Figure(figsize =  (3, 3))
        ax = fig.add_subplot(111)
        ax.imshow(img, cmap = 'gray')
        ax.axis('off')

        # Removes the white space around the image
        fig.subplots_adjust(left = 0, right = 1, bottom = 0, top = 1)

        canvas = FigureCanvasTkAgg(fig, master = input_img_label)
        canvas.draw()
        canvas.get_tk_widget().pack()
        loaded_image = ImageTk.PhotoImage(img)
        input_img_label.config(image = loaded_image)
        input_img_label.image = loaded_image

    create_input_window(window, table, df, input_img_label)



def clear_entry(event, entry, default_text):
    if entry.get() == default_text:
        entry.delete(0, tk.END)


def fill_entry(event, entry, default_text):
    if entry.get() == '':
        entry.insert(0, default_text)



def create_input_window(window, table, df, input_img_label):
    # Create a new window for user input
    input_window = tk.Toplevel(window)
    input_window.title("Input Parameters")
    input_window.geometry("400x400+350+300")

    message_label = tk.Label(input_window, text = "Please enter the values without units. \nExample: 200, 001, 10", font = ('Calibri', 12))
    message_label.pack()

    # Create labels and entry fields for each parameter
    voltage_label = tk.Label(input_window, text = "Accelerating Voltage:", font = ('Calibri', 12, 'bold'))
    voltage_label.pack()
    voltage_entry = tk.Entry(input_window, width = 30)
    voltage_default_text = "Enter voltage in kV"
    voltage_entry.insert(0, voltage_default_text)
    voltage_entry.bind("<FocusIn>", lambda event: clear_entry(event, voltage_entry, voltage_default_text))
    voltage_entry.bind("<FocusOut>", lambda event: fill_entry(event, voltage_entry, voltage_default_text))
    voltage_entry.pack()

    axis_label = tk.Label(input_window, text = "Zone Axis:", font = ('Calibri', 12, 'bold'))
    axis_label.pack()
    axis_entry = tk.Entry(input_window, width = 30)
    axis_default_text = "Enter zone axis in format [hkl]"
    axis_entry.insert(0, axis_default_text)
    axis_entry.bind("<FocusIn>", lambda event: clear_entry(event, axis_entry, axis_default_text))
    axis_entry.bind("<FocusOut>", lambda event: fill_entry(event, axis_entry, axis_default_text))
    axis_entry.pack()

    angle_label = tk.Label(input_window, text = "Convergence Angle:", font = ('Calibri', 12, 'bold'))
    angle_label.pack()
    angle_entry = tk.Entry(input_window, width = 30)
    angle_default_text = "Enter angle in mrad"
    angle_entry.insert(0, angle_default_text)
    angle_entry.bind("<FocusIn>", lambda event: clear_entry(event, angle_entry, angle_default_text))
    angle_entry.bind("<FocusOut>", lambda event: fill_entry(event, angle_entry, angle_default_text))
    angle_entry.pack()

    # Create a button that will retrieve the input values when clicked
    submit_button = tk.Button(input_window, text = "Submit", command = lambda: retrieve_input(voltage_entry, 
        axis_entry, angle_entry, input_window, table, df, input_img_label, voltage_default_text, axis_default_text, angle_default_text))
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
voltage, axis, angle = "", "", ""
def retrieve_input(voltage_entry, axis_entry, angle_entry, input_window, table, df, input_img_label, 
    voltage_default_text = "Enter voltage in kV", axis_default_text = "Enter zone axis in format [hkl]", angle_default_text = "Enter angle in mrad"):
    global measurements
    global results
    global loaded_image
    global voltage
    global axis
    global angle
    voltage, axis, angle = "", "", ""

    voltage = voltage_entry.get()
    axis = axis_entry.get()
    angle = angle_entry.get()
    
    # Validate the user inputs
    if ((voltage == "") or (axis == "") or (angle == "") or (voltage == voltage_default_text) or (axis == axis_default_text) or (angle == angle_default_text)):
        empty_image = tk.PhotoImage()
        loaded_image = empty_image
        input_img_label.config(image = loaded_image)
        input_img_label.image = loaded_image
        messagebox.showerror("Error", "Please input all parameters.")
        input_window.destroy()
        create_input_window(window, table, df, input_img_label)
    else:
        # Check if the 'Simulation Measurements' titles exist in the DataFrame
        measurements = ['Accelerating Voltage', 'Zone Axis', 'Convergence Angle']
        results = [str(voltage) + ' kV', '[' + str(axis) + ']', str(angle) + ' mrad']

        for i, measurement in enumerate(measurements):
            if measurement in df['Simulation Measurements'].values:
                # Overwrite the existing values
                df.loc[df['Simulation Measurements'] == measurement, 'Simulation Results'] = results[i]
            else:
                # Append the new values
                df = df.append({'Simulation Measurements': measurement, 'Simulation Results': results[i]}, ignore_index = True)

        # Update the table
        table.updateModel(TableModel(df))
        table.redraw()

        input_img_label.config(image = loaded_image)
        input_img_label.image = loaded_image

        input_window.destroy()



"""
    Outputs the image from the database that matches the input image that is being processed. The image is 
    then displayed onto the GUI next to the input image.
"""
output_img = None
def output_image():
    global measurements
    global results
    global loaded_image
    global file_path

    if loaded_image is None:
        messagebox.showerror("Error", "No image has been loaded.")
        return

    # Load the TIFF file
    image = mpimg.imread(file_path)
    plt.figure(facecolor = 'black')
    
    # Create a new figure and display the image with black borders
    plt.imshow(image, cmap = 'gray')
        
    # Remove axis
    plt.axis('off')
    
    # Getting the path to the user's Downloads folder
    downloads_folder = os.path.expanduser("~/Downloads")

    # Save the figure
    bright_output_filename = os.path.join(downloads_folder, "Bright_Exp.tif")
    # bright_output_filename = 'C:/Users/Angelo Carrion/Bright_Exp.tif'
    plt.savefig(bright_output_filename)
    processed_output_file = Database.pre_process_image(bright_output_filename)

    Database.directory_path = filedialog.askdirectory(title = "Please select the directory where your simulations are located.")
    if not Database.directory_path:
        messagebox.showerror("Error", "You must select a directory.")
        return

    list_num = []
    list_name = []

    for images in os.listdir(Database.directory_path):
    # Check if the image ends with tif 
        list_num.append(Database.get_best_image(processed_output_file, images)[0])
        list_name.append(Database.get_best_image(processed_output_file, images)[1])
    
    min_value = min(list_num)
    min_value_name = list_name[list_num.index(min_value)]
    names_with_same_error = []

    # Extract ones place and tenths place from the minimum value
    ones_place = int(min_value) % 10
    reference_tenths = int(min_value * 10) % 10

    # values_with_same_error = [value for value in list_num if int(value * 10) % 10 == reference_tenths and int(value) % 10 == ones_place]

    # Get names associated with the values at these indices
    # Find indices of values with the same error place as the minimum value
    indices_with_same_error = [i for i, value in enumerate(list_num) if int(value * 10) % 10 == reference_tenths and int(value) % 10 == ones_place]

    # Get names associated with the values at these indices
    names_with_same_error = [list_name[i] for i in indices_with_same_error]

    number = ''.join(filter(str.isdigit, min_value_name))
    if number:
        result = number
        add_on = " nm"
        best = ''.join([result, add_on])
    else:
        print("No numbers found in the string.")

    # Initialize a list to store the nm_best strings
    nm_best_list = []

    # Iterate over each name with the same error
    for name in names_with_same_error:
        number = ""
        
        # Iterate over each character in the name string
        for char in name:
            if char.isdigit():
                number += char

        if number:  # Check if any digits were found in the string
            result = number
            add_on = " nm"
            nm_best = ''.join([result, add_on])  # Construct the string with the extracted number and " nm"
            nm_best_list.append(nm_best)  # Append nm_best to the list  
        else:
            print("No numbers found in the string for name:", name)

    numerical_value_best = int(''.join(filter(str.isdigit, best)))
    numerical_values = []
    error_values = []

    for names in nm_best_list:
        numerical_value = int(''.join(filter(str.isdigit, names)))  # Extract numerical par
        numerical_values.append(numerical_value)
        # Perform subtraction
    for numbers in numerical_values:
        if (numerical_value_best == numbers):
            continue
        else:
            error_values.append(abs(numbers - numerical_value_best))
            
    if error_values:  # Check if error_values is not empty
        for values in error_values:
            if (values > 2):
                max_error = 2
            else:
                max_error = max(error_values)
    else:
        max_error = 2

    error_pl = str(max_error)
    add_on = " nm"
    error_best = ''.join([error_pl, add_on])
    add_PL = ' +- '
    plus_minus = ''.join([add_PL, error_best])
    final_value = ''.join([best, plus_minus])
    best_fit_image = '% s' %min_value_name
    
    # Initialize an empty list to store data
    data = []
    thickness = final_value
    material = "Silicon" # Right now, this is hardcoded data because we will be using the same material for all simulations for now
    measurements.extend(['Material', 'Thickness'])
    results.extend([material, thickness])

    # Create a list of dictionaries with measurement results
    for measurement, result in zip(measurements, results):
        data.append({'Simulation Measurements': measurement, 'Simulation Results': result})

    # Create a DataFrame from the list of dictionaries
    df = pd.DataFrame(data)

    # Update the table
    table.updateModel(TableModel(df))
    table.redraw()

    input_img_label.config(image = loaded_image)
    input_img_label.image = loaded_image
    
    image_path = best_fit_image
    if os.path.exists(best_fit_image):
        global output_img
        output_img = Image.open(best_fit_image)
        fig = Figure(figsize =  (3, 3))
        ax = fig.add_subplot(111)
        ax.imshow(output_img)
        ax.axis('off')

        # Removes the white space around the image
        fig.subplots_adjust(left = 0, right = 1, bottom = 0, top = 1)

        canvas = FigureCanvasTkAgg(fig, master = output_img_label)
        canvas.draw()
        canvas.get_tk_widget().pack()
        loaded_image = ImageTk.PhotoImage(output_img)
        output_img_label.config(image = loaded_image)
        output_img_label.image = loaded_image

    else:
        messagebox.showerror("Error", "No output image found.")



"""
    Saves the output image to a user-specified location. The user is prompted to select a location 
    and provide a name for the file.

    Raises:
    ------
    messagebox.showerror
        If there is no image to save.
"""
def save_image():
    global output_img

    if output_img is None:
        messagebox.showerror("Error", "No output image to save.")
        return
    
    file_path = filedialog.asksaveasfilename(title = "Please choose a location for the output image to be saved.", defaultextension = ".tif", filetypes = [("TIFF files", "*.tif")])
    if file_path:
        output_img.save(file_path)



def on_close():
    window.destroy()


# Initialize the main window
window = tk.Tk()
window.protocol("WM_DELETE_WINDOW", on_close)
window.grid_columnconfigure(0, weight = 1)
window.grid_rowconfigure(0, weight = 10)
window.grid_rowconfigure(1, weight = 1)
window.grid_rowconfigure(2, weight = 1)
window.title("Samsung Austin Semiconductor and Texas A&M University - TEM Sample Thickness Determination")
window.resizable(True, True)
window.configure(bg = 'white')

# Set the window icon
# windowIcon = Image.open('SamsungIcon.jpg')
# windowIcon = windowIcon.resize((48, 48), Image.LANCZOS)  # resize the image
# windowPhotoIcon =  ImageTk.PhotoImage(windowIcon)
# window.iconphoto(True, windowPhotoIcon)

# Set the size of the window to the screen size
window_width = window.winfo_screenwidth() - 50
window_height = window.winfo_screenheight() - 50

window.geometry("{0}x{1}+12+12".format(window_width, window_height))



def on_enter(e):
    e.widget['background'] = 'dark gray'



def on_leave(e):
    e.widget['background'] = 'light gray'



# Left frame for input image loading and outputting image
left_frame = tk.Frame(window)
left_frame.grid(row = 0, column = 0, sticky = 'nsew')
left_frame.grid_columnconfigure((0, 1), weight = 1)
left_frame.grid_rowconfigure((0, 1, 2), weight = 1)

input_img_label = tk.Label(left_frame)
input_img_label.grid(row = 0, column = 0, padx = 50, pady = 50, sticky = "nw")

output_img_label = tk.Label(left_frame)
output_img_label.grid(row = 0, column = 1, padx = 50, pady = 50, sticky = "ne")

load_button = tk.Button(left_frame, text = "Load Image", relief = "raised", fg = 'black', bg = 'light gray', height = 5, width = 40, font = 15, command = lambda: load_image(input_img_label))
load_button.bind("<Enter>", on_enter)
load_button.bind("<Leave>", on_leave)
load_button.grid(row = 2, column = 0, padx = 10, pady = 10, sticky = "sw")


###
# Later on, I will customize the buttons. As a reminder "bg" is for background color and "fg" is for text color
###

determine_thickness_button = tk.Button(left_frame, text = "Determine Thickness", relief = "raised", fg = 'black', bg = 'light gray', height = 5, width = 40, font = 15, command = output_image)
determine_thickness_button.bind("<Enter>", on_enter)
determine_thickness_button.bind("<Leave>", on_leave)
determine_thickness_button.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = "se")

save_button = tk.Button(left_frame, text = "Save Image", relief = "raised", fg = 'black', bg = 'light gray', height = 2, width = 15, font = 15, command = save_image)
save_button.bind("<Enter>", on_enter)
save_button.bind("<Leave>", on_leave)
save_button.grid(row = 1, column = 1, padx = 10, pady = 10, sticky = "se")


# Right frame for table view
right_frame = tk.Frame(window)
right_frame.grid(row = 0, column = 1, sticky = 'nsew')


data = {
    'Simulation Measurements': ['Accelerating Voltage', 'Zone Axis', 'Convergence Angle', 'Material', 'Thickness'],
    'Simulation Results': ['', '', '', '', ''],
}

df = pd.DataFrame(data)

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
