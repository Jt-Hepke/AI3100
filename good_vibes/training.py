
import numpy
from datasets import load_dataset
from sklearn.feature_extraction.text import CountVectorizer

train = load_dataset("fancyzhx/yelp_polarity", split = "train")
train = train.map(lambda row: {"text": row["text"].replace("\\n", " ")})
#train = train.shuffle(seed =0).select(range(50000)) #break off subset for training, and the same shuffle for training

y = numpy.array(train["label"]) #numpy array for the math | list of labels, 0 = negative, 1 = positive

# number of positive and negative reviews"
print("Positive: ", (y == 1).sum(), "Negative: ", (y == 0).sum()) 

#from hints
vectorizer = CountVectorizer(stop_words= "english", max_features= 5000)
X = vectorizer.fit_transform(train["text"])
words = vectorizer.get_feature_names_out()

#print("Matrix shape: ", X.shape)
#print("First 10 words:", words[:10])

V = len(words) #number of words

#fraction of positive and negitaive reviews
prior_pos = (y==1).mean()
prior_neg = (y == 0 ).mean()
#print("P(positive): ", prior_pos, "P(negative: ", prior_neg)

#total times each word appears in a flatten list for both pos and neg
posCounter = numpy.asarray(X[y==1].sum(axis=0)).ravel()
negCounter = numpy.asarray(X[y==0].sum(axis=0)).ravel()

#P of word in class = word count in class +1 / total words in class + V
Pword_pos = (posCounter + 1) /(posCounter.sum() + V)
Pword_neg = (negCounter + 1) /(negCounter.sum() + V) #added + 1's to make sure the word probability isn't 0

#print("First 5 words: ", words[:5])
#print("P(word | positive): ", Pword_pos[:5])
#print("P(word | negative): ", Pword_neg[:5])
#print("Sums: ", Pword_pos.sum(), Pword_neg.sum()) #should add to 1

log_prior_pos = numpy.log(prior_pos)
log_prior_neg = numpy.log(prior_neg)
log_p_word_pos = numpy.log(Pword_pos)   # log of every word's P(word | positive)
log_p_word_neg = numpy.log(Pword_neg)   # log of every word's P(word | negative)

def predict(text):
    x = vectorizer.transform([text]).toarray().ravel() #use training make list of 5000 counts
    score_pos = log_prior_pos
    score_neg = log_prior_neg
    for i in range(len(x)):
        if x[i] > 0:
            score_pos = score_pos + x[i] * log_p_word_pos[i]
            score_neg = score_neg + x[i] * log_p_word_neg[i] # add how many times it appears * the probability of the word

    #probility that the text is positive
    biggest = max(score_pos, score_neg)
    exp_pos = numpy.exp(score_pos -biggest)
    exp_neg = numpy.exp(score_neg -biggest)
    prob_pos = exp_pos / (exp_pos + exp_neg)

    label = "positive" if prob_pos > 0.5 else "negative"
    return label, prob_pos


#tests
#tests = [ "The food was amazing and the staff were wonderful", "Terrible service, cold food, and a rude waiter","I love this place, great atmosphere"]
#for t in tests:
    label, prob = predict(t) #run function
    print(label, round(prob, 3), "|", t)




#top 10 words using bayes rule for one word
top_part = Pword_pos * prior_pos                  # numerator (for every word at once)
denominator = top_part + Pword_neg * prior_neg    # denominator
p_pos_given_word = top_part / denominator          # P(positive | word) for all 5000 words
p_neg_given_word = 1 - p_pos_given_word            # P(negative | word)

best_pos = numpy.argsort(-p_pos_given_word)[:10]
best_neg = numpy.argsort(-p_neg_given_word)[:10]

print("\nTop 10 positive words:")
for i in best_pos:
    print(words[i], round(p_pos_given_word[i], 3))

print("\nTop 10 negative words:")
for i in best_neg:
    print(words[i], round(p_neg_given_word[i], 3))


#influecer test
#list of 10 post from twitter
posts = [
    #1
    """I have my priorities straight!""",
    #2
    """What an epic UFC event!""",
    #3
    """Newest addition to the Helicopter Hanger.. A completely fake RC store to organize my RC addiction. My kids love it! What should we add?""",
    #4
    """Anyone wanna come hangout at my laundromat soon!? 😍""",
    #5
    """Help wanted, I cant make it much longer… how do people quit drinking forever!? Like I’m actually trying and it just gets harder and harder! I need advice. I love the energy and productivity I have but not drinking at all is so hard. How do you do it!?""",
    #6
    """What a return! 💪🏼 record length videos! Record views! Let’s keep the train rolling. This week I am experimenting with filming on my non gym days to see how my energy changes. So I’ll see you Wednesday, Friday and Sunday this week. Thank you so much. See you soon.""",
    #7
    """Hell yeah 💪🏼""",
    #8
    """May 1st. WE BACK 😘""",
    #9
    """Damnit dirty Mike!""",
    #10
    """May 1st""",
]

for p in posts:
    p = p.replace("\\n", " ")
    label, prob = predict(p)
    print("\n")
    print(label, round(prob, 3), "|", p)
    