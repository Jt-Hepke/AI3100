
import numpy
from datasets import load_dataset
from sklearn.feature_extraction.text import CountVectorizer

train = load_dataset("fancyzhx/yelp_polarity", split = "train")
train = train.shuffle(seed =0).select(range(50000)) #break off subset for training, and the same shuffle for training

y = numpy.array(train["label"]) #numpy array for the math | list of labels, 0 = negative, 1 = positive

# number of positive and negative reviews"
print("Positive:: ", (y == 1).sum(), "Netagtive: ", (y == 0).sum()) 

#from hints
vectorizer = CountVectorizer(stop_words= "english", max_features= 5000)
X = vectorizer.fit_transform(train["text"])
words = vectorizer.get_feature_names_out()

print("Matrix shape: ", X.shape)
print("First 10 words:", words[:10])