Evaluating A Model README
1. Train the Model
Ensure the "SMSSpamCollection" dataset is located in the same directory as train.py
Run:
  python3 train.py

This is the training model and generates the saved model files found in this github.

2. Run Predictions
Place the teacher given new dataset in the same directory as my predict.py

Update predict.py:
  data = pd.read_csv( "YOUR_FILE_NAME", sep="\t", header=None, names=["label", "message"] )
If new dataset is in different format make sure to update the format settings too.
Run:
  python3 predict.py

predict.py loads the previously trained model and generates predictions without retraining pkl files. 
