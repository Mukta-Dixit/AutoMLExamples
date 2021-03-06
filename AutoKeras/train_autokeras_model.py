from sklearn.model_selection import train_test_split
import autokeras as ak
import os
import pandas as pd
import numpy as np
from PIL import Image, ImageOps


# pandas dataframes for datasets with image paths
## read file names
image_dirs = [f for f in os.listdir("./data") if '.csv' not in f]

images = pd.DataFrame(columns=["filename", "filepath", "label"])

for dir in image_dirs:
   images = images.append(pd.DataFrame({
    "filename": os.listdir("./data/"+dir),
    "filepath": ["data/"+dir+"/"+ s for s in os.listdir("./data/"+dir) ],
    "label": dir
    }))

# extract file extensions
images["file_ext"] = images.apply(lambda x: os.path.splitext(x['filename'])[1], axis=1 )
images.head()

# need to get rid of bad file extensions
images["file_ext"].unique()
images = images.loc[ images['file_ext'].isin(['.jpg', '.png', '.jpeg', '.JPG', '.img']) ]
images["file_ext"].unique()


train, test = train_test_split(images, test_size=0.2 )

####################################
###### Prep Training Dataset #######
####################################

# get the file paths we want to load
files = np.array(train.filepath)
labels = np.array(train.label)
x_train = np.empty((len(files), 200, 200, 3), int)
y_train = []

# load each image and convert it to an ndarray
# append each array to a list
for i in range(0, len(files)):    
    print(str(i) + "/" + str(len(files)-1))
    x = Image.open(files[i])
    x2 = ImageOps.fit(x, (200,200), Image.ANTIALIAS)
    arr = np.array(x2)
    
    x_train[i] = arr
    
    y_train.append(labels[i])

y_train = np.array(y_train)

####################################
######### Prep Train Model #########
####################################
# instantiate a classifier and fit a network
clf = ak.ImageClassifier(verbose=True)


import datetime as dt
t = dt.datetime.now()
print("Starting time: " + str(t))
clf.fit(x_train, y_train, time_limit=7200)
print("End time: " + str(dt.datetime.now()))
print("Total time: " + str(dt.datetime.now() - t))


####################################
######## Prep Test Dataset #########
####################################

# get the file paths we want to load
files = np.array(test.filepath)
labels = np.array(test.label)
x_test = np.empty((len(files), 200, 200, 3), int)
y_test = []

# load each image and convert it to an ndarray
# append each array to a list
for i in range(0, len(files)):    
    print(str(i) + "/" + str(len(files)-1))
    x = Image.open(files[i])
    x2 = ImageOps.fit(x, (200,200), Image.ANTIALIAS)
    arr = np.array(x2)
    
    x_test[i] = arr
    
    y_test.append(labels[i])

y_test = np.array(y_test)

clf.final_fit(x_train, y_train, y_test, y_test, retrain=True)


# apply model
y_pred = clf.evaluate(x_test, y_test)
print(y_pred)


####################################
########## Export Model ############
####################################

os.makedirs('autokeras_model', exist_ok=True)

clf.export_autokeras_model('autokeras_model/autokeras_images_retrained.h5')
clf.export_keras_model('autokeras_model/keras_images_retrained.h5')
clf.load_searcher().load_best_model().produce_keras_model().save('autokeras_modelmodels/keras_model_1_image_retrained.h5')


clf.export_autokeras_model
