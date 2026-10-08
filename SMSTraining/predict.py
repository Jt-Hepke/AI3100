import joblib # bring in our saved trained models
import pandas #loading in test file
from sklearn.metrics import confusion_matrix # making matrix

model = joblib.load("project.pkl") #load model
vectorizer = joblib.load("vectorizer.pkl") # load saved vectorizer numbers

data = pandas.read_csv (
    "testData", #input the test data file name
    sep= "\t", #if test file is the same format
    header=None, #if test file is the same format
    names=["label", "message"]

)

messages = data["message"] #read the message from text file
labels = data["label"] #read col label for the correct answers to compare to

X = vectorizer.transform(messages) #convert each message into the number versus using the trained high numbers from training
predictions = model.predict(X) #use the trained model to make predictions on test file messages

tn, fp, fn, tp = confusion_matrix(labels, predictions).ravel() #get values from matrix

#calculating hardcoded
accuracy1 = (tp + tn) / (tp + tn + fp + fn)
precision1 = tp / (tp + fp)
recall1 = tp / (tp + fn)
f1 = (precision1 * recall1) / (precision1 + recall1) * 2
specificity = tn / (tn + fp)

#Outputing
print("Accuracy: ", accuracy1)
print("Precision: ", precision1)
print("Recall: ", recall1)
print("F1 Score: ", f1)
print("Specificity: ", specificity)
print("Confusion Matrix below:")
print(confusion_matrix(labels, predictions))
print("If you wanna see all the predictions for the test file they will be below to compare:")
print(predictions)
