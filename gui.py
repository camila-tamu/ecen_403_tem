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
    Date: April 23, 2024

    This script creates a GUI application using tkinter for loading images and displaying simulation data in a table.
"""



""" 
    Global Variables Dictionary to access throughout multiple functions in the script.

    This was done because a dictionary is much more organized, flexible, and easier to 
    access than multiple global variables.
"""
globalVariables = {
    'loadedImage': None,
    'filePath': None,
    'measurements': None,
    'results': None,
    'voltageValue': None,
    'axisValue': None,
    'angleValue': None,
    'outputImg': None,
    'updateOutputImage': None
}



"""
    Converts an image file to TIFF format.

    This function opens an image file, converts it to TIFF format, and saves the new image. 
    The new image has the same name as the original file but with a '.tif' extension.

    Parameters:
    ----------
    filePath : str
        The path to the image file to be converted.

    Returns:
    -------
    new_filePath : str
        The path to the newly created TIFF image.    
"""
def convert_to_tif(filePath):
    img = Image.open(filePath)
    new_filePath = filePath.rsplit('.', 1)[0] + '.tif'
    img.save(new_filePath, 'TIFF')

    return new_filePath



"""
    Clears the canvas of any images. Opens a file dialog for the user to select an image file. 
    The selected image is displayed in the provided label. Also creates a new window for user to input 
    parameters: Accelerating Voltage, Zone Axis, and Convergence Angle. The input values are added to
    the table when the user clicks the Submit button.

    Parameters:
    ----------
    input_img_label : tk.Label
        The label in which the selected image will be displayed.

    outputImg_label : tk.Label
        The label in which the output image will be displayed.

    globalVariables : dict
        A dictionary containing various global variables.

    Returns:
    -------
    None

"""
def load_image(input_img_label, outputImg_label, globalVariables):
    for widget in input_img_label.winfo_children(): # Clear the canvas
        widget.destroy()

    for widget in outputImg_label.winfo_children(): # Clear the canvas
        widget.destroy()

    globalVariables['updateOutputImage'] = False
    globalVariables['outputImg'] = None
    globalVariables['loadedImage'] = None
    outputImg_label.config(image = '')  # Clear the output image label

    determine_thickness_button.config(state = 'normal')

    empty_image = tk.PhotoImage()
    input_img_label.config(image = empty_image)
    input_img_label.image = empty_image
    outputImg_label.config(image = empty_image)
    outputImg_label.image = empty_image

    globalVariables['filePath'] = filedialog.askopenfilename(title = "Please select the experimental image (.tif format).", filetypes = [("Image files", "*.png *.jpg *.jpeg *.tif *.tiff")])

    if not globalVariables['filePath']:
        return
    if globalVariables['filePath']:
        if globalVariables['filePath'].lower().endswith('.tif') or globalVariables['filePath'].lower().endswith('.tiff'):
            tif_filePath = globalVariables['filePath']
        else:
            tif_filePath = convert_to_tif(globalVariables['filePath'])

        img = Image.open(tif_filePath)
        fig = Figure(figsize =  (3, 3))
        ax = fig.add_subplot(111)
        ax.imshow(img, cmap = 'gray')
        ax.axis('off')

        # Removes the white space around the image
        fig.subplots_adjust(left = 0, right = 1, bottom = 0, top = 1)

        canvas = FigureCanvasTkAgg(fig, master = input_img_label)
        canvas.draw()
        canvas.get_tk_widget().pack()
        globalVariables['loadedImage'] = ImageTk.PhotoImage(img)
        input_img_label.config(image = globalVariables['loadedImage'])
        input_img_label.image = globalVariables['loadedImage']

    create_input_window(window, table, df, input_img_label)



"""
    This function clears the text in a tkinter Entry widget if the current text is the default text.

    Parameters:
    ----------
    event : tkinter.event
        The event object that triggered this function. This is typically a mouse click or key press event.

    entry : tkinter.Entry
        The Entry widget to clear.

    default_text : str
        The default text to compare with the current text in the Entry widget.

    Returns:
    -------
    None
"""
def clear_entry(event, entry, default_text):
    if entry.get() == default_text:
        entry.delete(0, tk.END)



"""
    This function fills a tkinter Entry widget with the default text if the current text is empty.

    Parameters:
    ----------
    event : tkinter.Event
        The event object that triggered this function. This is typically a mouse click or key press event.

    entry : tkinter.Entry
        The Entry widget to fill.

    default_text : str
        The default text to insert into the Entry widget.

    Returns:
    -------
    None
"""
def fill_entry(event, entry, default_text):
    if entry.get() == '':
        entry.insert(0, default_text)



"""
    This function creates a new window for user input with labels, entry fields for each parameter, and a submit button.

    Parameters:
    ----------
    window : tkinter.Tk
        The main application window.

    table: 
        The table to be used within the TableView.

    df : pandas.DataFrame 
        The DataFrame to be used to show the values from the user inputs.

    input_img_label : tkinter.Label 
        The label to display the input image.

    Returns:
    -------
    None
"""
def create_input_window(window, table, df, input_img_label):
    # Create a new window for user input
    input_window = tk.Toplevel(window)
    input_window.grab_set() # This prevents user from interacting with the main window
    input_window.title("Input Parameters")
    input_window.geometry("400x400+350+300")
    input_window.protocol("WM_DELETE_WINDOW", on_input_close)

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
        axis_entry, angle_entry, globalVariables, input_window, table, df, input_img_label, voltage_default_text, axis_default_text, angle_default_text))

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

    globalVariables : dict
        A dictionary containing various global variables.

    input_window : tk.Toplevel
        The window that contains the entry fields.

    table : Table
        The table to be updated.

    df : pd.DataFrame
        The DataFrame that contains the data for the table.

    Returns:
    -------
    None
"""
def retrieve_input(voltage_entry, axis_entry, angle_entry, globalVariables, input_window, table, df, input_img_label, 
    voltage_default_text = "Enter voltage in kV", axis_default_text = "Enter zone axis in format [hkl]", angle_default_text = "Enter angle in mrad"):

    globalVariables['voltageValue'] = voltage_entry.get()
    globalVariables['axisValue'] = axis_entry.get()
    globalVariables['angleValue'] = angle_entry.get()
    
    # Validate the user inputs
    if ((globalVariables['voltageValue'] == "") or (globalVariables['axisValue'] == "") or (globalVariables['angleValue'] == "") 
        or (globalVariables['voltageValue'] == voltage_default_text) or (globalVariables['axisValue'] == axis_default_text) 
        or (globalVariables['angleValue'] == angle_default_text)):

        empty_image = tk.PhotoImage()
        globalVariables['loadedImage'] = empty_image
        input_img_label.config(image = globalVariables['loadedImage'])
        input_img_label.image = globalVariables['loadedImage']
        messagebox.showerror("Error", "Please input all parameters.")
        input_window.destroy()
        create_input_window(window, table, df, input_img_label)
    else:
        # Check if the 'Simulation Measurements' titles exist in the DataFrame
        globalVariables['measurements'] = ['Accelerating Voltage', 'Zone Axis', 'Convergence Angle']
        globalVariables['results'] = [str(globalVariables['voltageValue']) + ' kV', '[' + str(globalVariables['axisValue']) + ']', 
            str(globalVariables['angleValue']) + ' mrad']

        for i, measurement in enumerate(globalVariables['measurements']):
            if measurement in df['Simulation Measurements'].values:
                # Overwrite the existing values
                df.loc[df['Simulation Measurements'] == measurement, 'Simulation Results'] = globalVariables['results'][i]
            else:
                # Append the new values
                df = df.append({'Simulation Measurements': measurement, 'Simulation Results': globalVariables['results'][i]}, ignore_index = True)

        # Update the table
        table.updateModel(TableModel(df))
        table.redraw()

        input_img_label.config(image = globalVariables['loadedImage'])
        input_img_label.image = globalVariables['loadedImage']

        input_window.destroy()



"""
    This function is used to output the image from the database that matches the input image being processed. 
    The image is then displayed onto the GUI next to the input image. Since this function does a lot, I have
    provided a step-by-step explaination below:

        The function performs the following steps:
        1. Checks if an image has been loaded. If not, an error message is displayed.
        2. Reads the image from the file path specified in the global variables.
        3. Displays the image in a new figure with black borders and no axis.
        4. Saves the figure in the user's Downloads folder.
        5. Processes the saved image using the pre_process_image function from the Database module.
        6. Asks the user to select a directory where the simulations are located.
        7. Iterates over all images in the selected directory and gets the best image for each one using the get_best_image function from the Database module.
        8. Finds the image with the minimum error and all images with the same error.
        9. Extracts the numerical part from the names of the images with the same error and constructs a string with the format 'number nm'.
        10. Calculates the maximum error among the images with the same error.
        11. Constructs a string with the format 'best +- error nm'.
        12. Updates the measurements and results in the global variables with the material and thickness.
        13. Updates the table in the GUI with the new measurements and results.
        14. Displays the input image and the best fit image in the GUI.

    Parameters:
    ----------
    globalVariables : dict
        A dictionary containing global variables.

    Returns:
    -------
    None
"""
def output_image(globalVariables):
    globalVariables['updateOutputImage'] = True

    if globalVariables['loadedImage'] is None:
        messagebox.showerror("Error", "No image has been loaded.")
        return
    
    # Load the TIFF file
    image = mpimg.imread(globalVariables['filePath'])
    plt.figure(facecolor = 'black')
    
    # Create a new figure and display the image with black borders
    plt.imshow(image, cmap = 'gray')
        
    # Remove axis
    plt.axis('off')
    
    # Getting the path to the user's Downloads folder
    downloads_folder = os.path.expanduser("~/Downloads")

    # Save the figure
    bright_output_filename = os.path.join(downloads_folder, "Bright_Exp.tif")
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
    globalVariables['measurements'].extend(['Material', 'Thickness'])
    globalVariables['results'].extend([material, thickness])

    # Create a list of dictionaries with measurement results
    for measurement, result in zip(globalVariables['measurements'], globalVariables['results']):
        data.append({'Simulation Measurements': measurement, 'Simulation Results': result})

    # Create a DataFrame from the list of dictionaries
    df = pd.DataFrame(data)

    # Update the table
    table.updateModel(TableModel(df))
    table.redraw()

    input_img_label.config(image = globalVariables['loadedImage'])
    input_img_label.image = globalVariables['loadedImage']
    if globalVariables['updateOutputImage'] == True:
        if os.path.exists(best_fit_image):
            globalVariables['outputImg'] = Image.open(best_fit_image)
            fig = Figure(figsize =  (3, 3))
            ax = fig.add_subplot(111)
            ax.imshow(globalVariables['outputImg'])
            ax.axis('off')

            # Removes the white space around the image
            fig.subplots_adjust(left = 0, right = 1, bottom = 0, top = 1)

            canvas = FigureCanvasTkAgg(fig, master = outputImg_label)
            canvas.draw()
            canvas.get_tk_widget().pack()
            globalVariables['loadedImage'] = ImageTk.PhotoImage(globalVariables['outputImg'])
            outputImg_label.config(image = globalVariables['loadedImage'])
            outputImg_label.image = globalVariables['loadedImage']
            globalVariables['updateOutputImage'] = False
        else:
            messagebox.showerror("Error", "No output image found.")

    determine_thickness_button.config(state = 'disabled')    



"""
    This function saves the output image to a user-specified location. The user is prompted to select a location 
    and provide a name for the file.

    Parameters:
    ----------
    globalVariables : dict
        A dictionary containing various global variables.

    Returns:
    -------
    None
"""
def save_image(globalVariables):
    if globalVariables['outputImg'] is None:
        messagebox.showerror("Error", "No output image to save.")
        return
    
    filePath = filedialog.asksaveasfilename(title = "Please choose a location for the output image to be saved.", defaultextension = ".tif", 
        filetypes = [("TIFF files", "*.tif")])

    if filePath:
        globalVariables['outputImg'].save(filePath)



"""
    This function is used to close the GUI window.

    Parameters:
    ----------
    None

    Returns:
    -------
    None
"""
def on_window_close():
    window.quit()
    window.destroy()



"""
    This function is used to close the Input Parameters window.

    Parameters:
    ----------
    None

    Returns:
    -------
    None
"""
def on_input_close():
    messagebox.showerror("Error", "Please input all parameters.")
    create_input_window(window, table, df, input_img_label)



# Initialize the main window
window = tk.Tk()
window.protocol("WM_DELETE_WINDOW", on_window_close)
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



"""
    This function is used to change the background color of a widget to 'dark gray' when the mouse pointer enters the widget.

    Parameters:
    ----------
    e : Event
        An event object that contains information about the event. The widget that triggered the event can be accessed through the 'widget' attribute.

    Returns:
    -------
    None
"""
def on_enter(e):
    e.widget['background'] = 'dark gray'



"""
    This function is used to change the background color of a widget to 'light gray' when the mouse pointer leaves the widget.

    Parameters:
    ----------
    e : Event
        An event object that contains information about the event. The widget that triggered the event can be accessed through the 'widget' attribute.

    Returns:
    -------
    None
"""
def on_leave(e):
    e.widget['background'] = 'light gray'



# Left frame for input image loading and outputting image
left_frame = tk.Frame(window)
left_frame.grid(row = 0, column = 0, sticky = 'nsew')
left_frame.grid_columnconfigure((0, 1), weight = 1)
left_frame.grid_rowconfigure((0, 1, 2), weight = 1)

input_img_label = tk.Label(left_frame)
input_img_label.grid(row = 0, column = 0, padx = 50, pady = 50, sticky = "nw")

outputImg_label = tk.Label(left_frame)
outputImg_label.grid(row = 0, column = 1, padx = 50, pady = 50, sticky = "ne")

load_button = tk.Button(left_frame, text = "Load Image", relief = "raised", fg = 'black', bg = 'light gray', height = 5, width = 40, font = 15, 
    command = lambda: load_image(input_img_label, outputImg_label, globalVariables))

load_button.bind("<Enter>", on_enter)
load_button.bind("<Leave>", on_leave)
load_button.grid(row = 2, column = 0, padx = 10, pady = 10, sticky = "sw")

determine_thickness_button = tk.Button(left_frame, text = "Determine Thickness", relief = "raised", fg = 'black', bg = 'light gray', height = 5, 
    width = 40, font = 15, command = lambda: output_image(globalVariables))

determine_thickness_button.bind("<Enter>", on_enter)
determine_thickness_button.bind("<Leave>", on_leave)
determine_thickness_button.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = "se")

save_button = tk.Button(left_frame, text = "Save Image", relief = "raised", fg = 'black', bg = 'light gray', height = 2, width = 15, font = 15, 
    command =  lambda: save_image(globalVariables))

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
