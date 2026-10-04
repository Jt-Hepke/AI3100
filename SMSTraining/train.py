import pandas as pd #working with table
from sklearn.feature_extraction.text import TfidfVectorizer #turn message into numbers
from sklearn.model_selection import train_test_split #split dataset into training and testing

data = pd.read_csv( #read file name below and turn into table
    "SMSSpamCollection",
    sep="\t", #seperate varables below with tab
    header=None,
    names=["label", "message"]
)

print(data.head())
print(data.shape) # ( #number of rows, #of columns) (rows = # of messages)
print(data["label"].value_counts()) 

vectorizer = TfidfVectorizer() #translator
X = vectorizer.fit_transform(data["message"]) #turns messgae into numbers
print(X.shape) #'X' now stores translatated numbered message (# of messages, # of words found)
y = data["label"] #answers trying to predict
print(y.shape)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20, #keep 20% for testing
    random_state=42 #repeatable same split every compile
)