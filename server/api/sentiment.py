from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from nltk.corpus import stopwords 
from collections import Counter
import string
import re
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import train_test_split
import numpy as np
import finnhub
from dotenv import load_dotenv
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

model_path = os.path.join(os.path.dirname(__file__), "api/sentiment_rnn.pt")
model = torch.jit.load(model_path, map_location=torch.device('cpu'))

# Load the dataset
csv_path = os.path.join(os.path.dirname(__file__), "api/data.csv")  # Relative to the script
data = pd.read_csv(csv_path)
#print(data.head())

from string import punctuation
def remove_punc(text):
    text = text.lower()
    return ("".join(i for i in text if i not in punctuation))

data["review"] = data["review"].apply(remove_punc)
print(data.head())
X = data["review"].values
y = data["sentiment"].values
X_train,X_test,y_train,y_test = train_test_split(X,y,stratify=y)
#print(X_train.shape)
#print(X_test.shape)

def process(string):
    string = re.sub(r"[^\w\s]", '', string)
    string = re.sub(r"\d", '', string)
    string = re.sub(r"\s+", '', string)
    return string

def tokenize(X_train,y_train,X_test,y_test):
    words = []
    stop_words = set(stopwords.words('english')) 
    for x in X_train:
        for word in x.split():
            word = process(word)
            if word not in stop_words and word != '':
                words.append(word)
                
    counts = Counter(words)
    vocab = sorted(counts, key=counts.get, reverse=True)[:1000]
    vocab_to_int = {word: ii for ii, word in enumerate(vocab,1)}
    new_X_train = []
    new_X_test = []
    for s in X_train:
            new_X_train.append([vocab_to_int[process(word)] for word in s.split() 
                                     if process(word) in vocab_to_int.keys()])
    for s in X_test:
            new_X_test.append([vocab_to_int[process(word)] for word in s.split() 
                                    if process(word) in vocab_to_int.keys()])
            
    new_y_train = [1 if label =='positive' else 0 for label in y_train]  
    new_y_test = [1 if label =='positive' else 0 for label in y_test]
    return new_X_train, new_y_train,new_X_test, new_y_test, vocab_to_int

X_train,y_train,X_test,y_test,vocab_to_int = tokenize(X_train,y_train,X_test,y_test)

def padding(sentence, seqLength):
    #determine shape
    features = np.zeros((len(sentence), seqLength), dtype=int)
    for i, row in enumerate(sentence):
        if len(row) != 0:
            features[i, -len(row):] = np.array(row)[:seqLength]
    return features

def init_hidden(batch_size, device='cpu'):
    hidden_dim = 256 
    num_layers = 2    
    
    return (
        torch.zeros(num_layers, batch_size, hidden_dim).to(device),
        torch.zeros(num_layers, batch_size, hidden_dim).to(device)
    )
    
def tokenize_review(test_review):
    test_review = test_review.lower()
    test_text = ''.join([i for i in test_review if i not in punctuation])
    test_words = test_text.split()
    test_ints = []
    test_ints.append([vocab_to_int.get(word, 0) for word in test_words])
    return test_ints

def predict(net, test_review, sequence_length=500):
    model.eval()
    test_ints = tokenize_review(test_review)
    seq_length=sequence_length
    features = padding(test_ints, seq_length)
    feature_tensor = torch.from_numpy(features)
    batch_size = feature_tensor.size(0)
    h = init_hidden(batch_size)
    with torch.no_grad():
        output, h= model(feature_tensor,h)
    #print('Prediction value: {:.6f}'.format(output.item()))
    if(output.item() > 0.5):
        return f"Positive market sentiment detected! With probability of: {output.item()}"
    else:
        return f"Negative market sentiment detected! With probability of: {(1 - output.item())}"
        
@csrf_exempt
@api_view(['POST'])
def sen_display(request):
    try:
        load_dotenv()

        stock_symbol = request.data.get('stock_symbol')
        
        current_date = datetime.today()
        start_date = current_date - relativedelta(days=1)
        finnhub_client = finnhub.Client(api_key=os.getenv("FINNHUB_API_KEY"))
        ALL_NEWS = finnhub_client.company_news(stock_symbol, _from=start_date.strftime('%Y-%m-%d'), to=current_date.strftime('%Y-%m-%d'))
        
        all_text = []
        for news in ALL_NEWS:
            text = news['headline'] + "--->" + news['summary']
            all_text.append(text)
            
        output = ""
        count = 1
        for text in all_text:
            output += f"Company News (Past Day) #{count} : " + f"{text}\n" + f"{predict(model, text, 500)}\n\n"
            count += 1
        
        return Response({'response': output}, status=200)
    
    except Exception as e:
        return Response({'error': str(e)}, status=500)