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
# variables for each layer
INPUT_SHAPE = (384, 384, 4)
FILTER1_SIZE = 32
FILTER2_SIZE = 64
FILTER3_SIZE = 128
FILTER_SHAPE = (4, 4)
POOL_SHAPE = (4, 4)
FULLY_CONNECT_NUM = 264
NUM_CLASSES = 120

# create model and add each convolution and pooling layer
model = Sequential()
# use 4 x 4 filters for convolution layer
# first convolution layer creates 32 filters
# strides=(1,1), padding="same" ensure zero-padding such that input and output sizes match
model.add(Conv2D(FILTER1_SIZE, FILTER_SHAPE, strides=(1, 1), padding="same", activation='relu', input_shape=INPUT_SHAPE))
model.add(MaxPooling2D(POOL_SHAPE))     # use 4 x 4 shape for pooling layer

# repeat for 64 filters
model.add(Conv2D(FILTER2_SIZE, FILTER_SHAPE, strides=(1, 1), padding="same", activation='relu'))
model.add(MaxPooling2D(POOL_SHAPE))

# repeat for 128 filters
model.add(Conv2D(FILTER3_SIZE, FILTER_SHAPE, strides=(1, 1), padding="same", activation='relu'))
model.add(MaxPooling2D(POOL_SHAPE))

# flattened neutral network for output
model.add(Flatten())    # flatten convolution layers
model.add(Dense(FULLY_CONNECT_NUM, activation='relu'))      # create hidden layer of size 264
model.add(Dense(NUM_CLASSES, activation='softmax'))         # output for each class (1-120nm)

EPOCHS = 60		# use 60 epochs

# show accuracy, precision, and recall for each epoch
METRICS = metrics=['accuracy',
               	Precision(name='precision'),
               	Recall(name='recall')]

# use cross entropy loss for biasing
model.compile(optimizer=keras.optimizers.Adam(),
          	loss=keras.losses.CategoricalCrossentropy(),
          	metrics = METRICS)

# train model to training dataset and validate with validation dataset
training_history = model.fit(ds_train,
                	epochs=EPOCHS, batch_size=BATCH_SIZE,
                	validation_data=ds_validation)

model.save("thicknessCNN.keras")    # save trained model

# create function to show matrics over the epochs for both training and validation metrics
def show_performance_curve(training_result, metric, metric_label):
	train_perf = training_result.history[str(metric)]					# get training metrics
	validation_perf = training_result.history['val_'+str(metric)]		# get validation metrics

	# plot both metrics on same plot
	plt.plot(train_perf, label=metric_label)
	plt.plot(validation_perf, label = 'val_'+str(metric))

	# plot details
	plt.xlabel('Epoch')
	plt.ylabel(metric_label)
	plt.legend(loc='upper left')

show_performance_curve(training_history, 'accuracy', 'accuracy')    # metrics plot for accuracy and validation accuracy
show_performance_curve(training_history, 'precision', 'precision')      # metrics plot for precision and validation precision

model.evaluate(ds_train, return_dict=True)      # evaluate metrics of final epoch for training dataset
model.evaluate(ds_validation, return_dict=True)     # evaluate metrics of final epoch for validation dataset
