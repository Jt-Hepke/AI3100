import pandas as pd #working with table
from sklearn.feature_extraction.text import TfidfVectorizer #turn message into numbers
from sklearn.model_selection import train_test_split #split dataset into training and testing
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score #testing how well the model did
from sklearn.metrics import confusion_matrix #testing numbers
from sklearn.metrics import precision_score # presision score
from sklearn.metrics import recall_score #recall score
from sklearn.metrics import f1_score #f1 score


data = pd.read_csv( #read file name below and turn into table
    "SMSSpamCollection",
    sep="\t", #seperate varables below with tab
    header=None,
    names=["label", "message"]
)
#Look at data
print(data.head())
print(data.shape) # ( #number of rows, #of columns) (rows = # of messages)
print(data["label"].value_counts()) 


#print(X.shape) #'X' now stores translatated numbered message (# of messages, # of words found)
#y = data["label"] #answers trying to predict
#print(y.shape)

messages = data["message"]
labels = data["label"]

X_train_text, X_test_text, y_train, y_test = train_test_split(
    messages,
    labels,
    test_size=0.20, #keep 20% for testing
    random_state=42 #repeatable same split every compile
)

vectorizer = TfidfVectorizer() #translator
X_train = vectorizer.fit_transform(X_train_text) #Learn words from training messages, turn them into numbers
X_test = vectorizer.transform(X_test_text) # turn test messages into numbers using knowledge from training

print("Training message:" , X_train.shape)
print("Testing messages:", X_test.shape)

#machine learning model
model = LogisticRegression()
model.fit(X_train, y_train) #train model with training data
print("Model test complete")

#trained model predict with test messages
predictions = model.predict(X_test)

#show predictions
print("Predictions: ")
print(predictions[:10])

#find the accuracy
accuracy = accuracy_score(y_test, predictions)
print("Accuracy: ", accuracy)

cm = confusion_matrix(y_test, predictions)
print("Matrix: \n", cm ) #TN, FP, FN, TP
tn, fp, fn, tp = confusion_matrix(y_test, predictions).ravel() #pull from matrix, ravel flattens table

#calulating scores
precision = precision_score(y_test, predictions, pos_label="spam") 
recall = recall_score(y_test, predictions, pos_label="spam")
f1 = f1_score(y_test, predictions, pos_label="spam")
specificity = tn / (tn + fp)

print(precision)
print(recall)
print(specificity)
print(f1)