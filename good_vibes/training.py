from datasets import load_dataset

train = load_dataset("fancyzhx/yelp_polarity", split = "train")

print(train)
print("Label: ", train[0]["label"])
print("Text: ", train[0]["text"])