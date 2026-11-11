
import numpy
from datasets import load_dataset
from sklearn.feature_extraction.text import CountVectorizer

train = load_dataset("fancyzhx/yelp_polarity", split = "train")
train = train.shuffle(seed =0).select(range(50000)) #break off subset for training, and the same shuffle for training

y = numpy.array(train["label"]) #numpy array for the math | list of labels, 0 = negative, 1 = positive

# number of positive and negative reviews"
print("Positive:: ", (y == 1).sum(), "Negative: ", (y == 0).sum()) 

#from hints
vectorizer = CountVectorizer(stop_words= "english", max_features= 5000)
X = vectorizer.fit_transform(train["text"])
words = vectorizer.get_feature_names_out()

print("Matrix shape: ", X.shape)
print("First 10 words:", words[:10])

V = len(words) #number of words

#fraction of positive and negitaive reviews
prior_pos = (y==1).mean()
prior_neg = (y == 0 ).mean()
print("P(positive): ", prior_pos, "P(negative: ", prior_neg)

#total times each word appears in a flatten list for both pos and neg
posCounter = numpy.asarray(X[y==1].sum(axis=0)).ravel()
negCounter = numpy.asarray(X[y==0].sum(axis=0)).ravel()

#P of word in class = word count in class +1 / total words in class + V
Pword_pos = (posCounter + 1) /(posCounter.sum() + V)
Pword_neg = (negCounter + 1) /(negCounter.sum() + V) #added + 1's to make sure the word probability isn't 0

print("First 5 words: ", words[:5])
print("P(word | positive): ", Pword_pos[:5])
print("P(word | negative): ", Pword_neg[:5])
print("Sums: ", Pword_pos.sum(), Pword_neg.sum()) #should add to 1