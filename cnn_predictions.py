# imports
import matplotlib.pyplot as plt
import os
import pathlib                                                                  # to find database of augmented data for CNN training
import numpy as np
import tensorflow as tf                                                         # tensorflow library to create CNN
import tensorflow_io as tfio                                                    # tensorflow_io library for TIFF image support
from tensorflow import keras                                                    # imports for keras functions to create CNN model
from tensorflow.keras.utils import to_categorical
from tensorflow.keras import Sequential, layers
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.metrics import Precision, Recall
from PIL import Image                                                           # for TIFF formatting
from skimage import transform                                                   # for image loading and pre-processing

# get path for image database for CNN training
dir = pathlib.Path("*sat*.tif")
filePaths = tf.io.gfile.glob(str("*sat*.tif"))
ds_train = tf.data.Dataset.from_tensor_slices(filePaths)    # create tensor dataset from image database

BATCH_SIZE = 60     # use batch of 60

# function to process each image in the dataset
# outputs decoded image and corresponding binary vector label
def process_path(filePath):
    # decode TIFF image file so it's in a form the CNN can use
    img = tf.io.read_file(filePath)
    img = tfio.experimental.image.decode_tiff(img)

    # get class from file name
    className = tf.strings.split(filePath, " nm")[0]
    className = tf.strings.regex_replace(className, './', '')

    # possible classes from 1-120nm
    classNames = []
    for i in range(1, 121):
        classNames.append(str(i))

    # use one-hot encoding to create a binary vector for the class
    # vector length is number of classes (120)--point is 1 for class match, 0 otherwise
    labels = tf.one_hot(tf.argmax(tf.cast(tf.equal(classNames, className), tf.int32)), depth=len(classNames))

    return img, labels      # return decoded image and binary vector label for TIFF image

# create training dataset
ds_train = ds_train.map(process_path, num_parallel_calls=tf.data.experimental.AUTOTUNE)

# shuffle for randomization
ds_size = ds_train.cardinality().numpy()
ds_train = ds_train.shuffle(buffer_size=ds_size)

# divide into training and validation datasets using a 70:30 ratio
num_samples = int(0.3 * ds_size)
ds_validation = ds_train.take(num_samples)

# divide into batches using batch size
ds_train = ds_train.skip(num_samples).batch(BATCH_SIZE).prefetch(buffer_size=tf.data.experimental.AUTOTUNE)
ds_validation = ds_validation.batch(BATCH_SIZE).prefetch(buffer_size=tf.data.experimental.AUTOTUNE)

# loop through each training batch to confirm correct batching and classes
for batch_images, batch_class_names in ds_train:
    print("Batch shape:", batch_images.shape)
    print("Batch class names:", batch_class_names)

# CNN model
newModel = tf.keras.models.load_model('thicknessCNN_afterTraining_sat_60epoch_acc-76_predFresh-96_4-15s.keras')     # load trained model
newModel.summary()      # show model architecture

newModel.evaluate(ds_train, return_dict=True)       # evaluate metrics of final epoch for training dataset using loaded model
newModel.evaluate(ds_validation, return_dict=True)      # evaluate metrics of final epoch for validation dataset using loaded model

# create array of class names (1-120nm)
classNames = []
for i in range(1, 121):
    classNames.append(str(i))

# function to load individual TIFF image file
def loadImg(filename):
   np_image = Image.open(filename)                          # open file
   np_image = np.array(np_image).astype('float32')/255      # normalize
   np_image = transform.resize(np_image, (384, 384, 4))     # resize to match model input size
   np_image = np.expand_dims(np_image, axis=0)
   return np_image      # return image

numCorrect = 0;     # use to check CNN prediction accuracy

# loop through each 0-tilt simulation image for 1-120nm
for i in range(1, 121):
    image5 = loadImg(str(i) + ' nm.tif')        # load image
    prediction5 = newModel.predict(image5)      # use CNN to make prediction

    # post-process prediction to get class
    predicted_class_index5 = np.argmax(prediction5, axis=1)[0]
    predicted_class_name5 = classNames[predicted_class_index5]

    # compare expected and predicted class
    print("Expected class:", i, "nm")
    print("Predicted class:", predicted_class_name5, "nm")

    # prediction deemed correct if within +-4nm of expected class
    if (abs(i - int(predicted_class_name5)) <= 4):
        numCorrect += 1

print(numCorrect/120*100)   # find accuracy percentage

predCorr = 0;   # use to check CNN prediction accuracy for SAS images

# image 1
image3 = loadImg('exp_img1.tif')            # load post-processed image from data processing subsystem
prediction3 = newModel.predict(image3)      # use CNN to make prediction

# post-process prediction to get class
predicted_class_index3 = np.argmax(prediction3, axis=1)[0]
predicted_class_name3 = classNames[predicted_class_index3]

# compare expected and predicted class
print("Expected class:", 17, "nm")      # expected class gotten from data processing subsystem
print("Predicted class:", predicted_class_name3, "nm")

# prediction deemed correct if within +-4nm of expected class
if (abs(17 - int(predicted_class_name3)) <= 4):
    predCorr += 1

# repeat for each image provided by SAS and after processing from data processing subsystem
# image 2
image4 = loadImg('exp_img2.tif')
prediction4 = newModel.predict(image4)

predicted_class_index4 = np.argmax(prediction4, axis=1)[0]
predicted_class_name4 = classNames[predicted_class_index4]

print("Expected class:", 49, "nm")
print("Predicted class:", predicted_class_name4, "nm")

if (abs(49 - int(predicted_class_name4)) <= 4):
    predCorr += 1

# image 3
image6 = loadImg('exp_img3.tif')
prediction6 = newModel.predict(image6)

predicted_class_index6 = np.argmax(prediction6, axis=1)[0]
predicted_class_name6 = classNames[predicted_class_index6]

print("Expected class:", 12, "nm")
print("Predicted class:", predicted_class_name6, "nm")

if (abs(12 - int(predicted_class_name6)) <= 4):
    predCorr += 1

# image 4
image7 = loadImg('exp_img4.tif')
prediction7 = newModel.predict(image7)

predicted_class_index7 = np.argmax(prediction7, axis=1)[0]
predicted_class_name7 = classNames[predicted_class_index7]

print("Expected class:", 39, "nm")
print("Predicted class:", predicted_class_name7, "nm")

if (abs(39 - int(predicted_class_name7)) <= 4):
    predCorr += 1

# image 5
image8 = loadImg('exp_img5.tif')
prediction8 = newModel.predict(image8)

predicted_class_index8 = np.argmax(prediction8, axis=1)[0]
predicted_class_name8 = classNames[predicted_class_index8]

print("Expected class:", 48, "nm")
print("Predicted class:", predicted_class_name8, "nm")

if (abs(48 - int(predicted_class_name8)) <= 4):
    predCorr += 1

# image 6
image9 = loadImg('exp_img6.tif')
prediction9 = newModel.predict(image9)

predicted_class_index9 = np.argmax(prediction9, axis=1)[0]
predicted_class_name9 = classNames[predicted_class_index9]

print("Expected class:", 18, "nm")
print("Predicted class:", predicted_class_name9, "nm")

if (abs(18 - int(predicted_class_name9)) <= 4):
    predCorr += 1

# image 7
image10 = loadImg('exp_img7.tif')
prediction10 = newModel.predict(image10)

predicted_class_index10 = np.argmax(prediction10, axis=1)[0]
predicted_class_name10 = classNames[predicted_class_index10]

print("Expected class:", 14, "nm")
print("Predicted class:", predicted_class_name10, "nm")

if (abs(14 - int(predicted_class_name10)) <= 4):
    predCorr += 1

# image 8
image11 = loadImg('exp_img8.tif')
prediction11 = newModel.predict(image11)

predicted_class_index11 = np.argmax(prediction11, axis=1)[0]
predicted_class_name11 = classNames[predicted_class_index11]

print("Expected class:", 14, "nm")
print("Predicted class:", predicted_class_name11, "nm")

if (abs(14 - int(predicted_class_name11)) <= 4):
    predCorr += 1

print(predCorr/8*100)   # find accuracy percentage for SAS images
