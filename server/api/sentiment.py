from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords 
from collections import Counter
import string
import re
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import train_test_split
import finnhub
from dotenv import load_dotenv
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

class SentimentAnalyzer:
    def __init__(self):
        self.model = None
        self.data = None
        self.vocab_to_int = None
        self.stop_words = set(stopwords.words('english'))
        self.initialize()
        
    def initialize(self):
        """Initialize the sentiment analyzer by loading model and data"""
        # Load model
        model_path = os.path.join(os.path.dirname(__file__), "artifacts/sentiment_rnn.pt")
        self.model = torch.jit.load(model_path, map_location=torch.device('cpu'))
        
        # Load and preprocess data
        csv_path = os.path.join(os.path.dirname(__file__), "artifacts/data.csv")
        self.data = pd.read_csv(csv_path)
        self.data["review"] = self.data["review"].apply(self.remove_punc)
        
        # Prepare training data
        X = self.data["review"].values
        y = self.data["sentiment"].values
        X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y)
        
        # Tokenize and build vocabulary
        self.X_train, self.y_train, self.X_test, self.y_test, self.vocab_to_int = self.tokenize(
            X_train, y_train, X_test, y_test
        )
    
    def remove_punc(self, text):
        """Remove punctuation from text"""
        text = text.lower()
        return "".join(i for i in text if i not in string.punctuation)
    
    def process_word(self, word):
        """Process individual words"""
        word = re.sub(r"[^\w\s]", '', word)
        word = re.sub(r"\d", '', word)
        word = re.sub(r"\s+", '', word)
        return word
    
    def tokenize(self, X_train, y_train, X_test, y_test):
        """Tokenize text and build vocabulary"""
        words = []
        for x in X_train:
            for word in x.split():
                word = self.process_word(word)
                if word not in self.stop_words and word != '':
                    words.append(word)
        
        counts = Counter(words)
        vocab = sorted(counts, key=counts.get, reverse=True)[:1000]
        vocab_to_int = {word: ii for ii, word in enumerate(vocab, 1)}
        
        new_X_train = []
        new_X_test = []
        
        for s in X_train:
            new_X_train.append([
                vocab_to_int[self.process_word(word)] for word in s.split() 
                if self.process_word(word) in vocab_to_int.keys()
            ])
        
        for s in X_test:
            new_X_test.append([
                vocab_to_int[self.process_word(word)] for word in s.split() 
                if self.process_word(word) in vocab_to_int.keys()
            ])
        
        new_y_train = [1 if label == 'positive' else 0 for label in y_train]
        new_y_test = [1 if label == 'positive' else 0 for label in y_test]
        
        return new_X_train, new_y_train, new_X_test, new_y_test, vocab_to_int
    
    def padding(self, sentence, seqLength):
        """Pad sequences to consistent length"""
        features = np.zeros((len(sentence), seqLength), dtype=int)
        for i, row in enumerate(sentence):
            if len(row) != 0:
                features[i, -len(row):] = np.array(row)[:seqLength]
        return features
    
    def init_hidden(self, batch_size, device='cpu'):
        """Initialize hidden state for RNN"""
        hidden_dim = 256 
        num_layers = 2    
        return (
            torch.zeros(num_layers, batch_size, hidden_dim).to(device),
            torch.zeros(num_layers, batch_size, hidden_dim).to(device)
        )
    
    def tokenize_review(self, test_review):
        """Tokenize a new review for prediction"""
        test_review = test_review.lower()
        test_text = ''.join([i for i in test_review if i not in string.punctuation])
        test_words = test_text.split()
        test_ints = []
        test_ints.append([self.vocab_to_int.get(word, 0) for word in test_words])
        return test_ints
    
    def predict_sentiment(self, test_review, sequence_length=500):
        """Predict sentiment for a single review"""
        self.model.eval()
        test_ints = self.tokenize_review(test_review)
        features = self.padding(test_ints, sequence_length)
        feature_tensor = torch.from_numpy(features)
        batch_size = feature_tensor.size(0)
        h = self.init_hidden(batch_size)
        
        with torch.no_grad():
            output, h = self.model(feature_tensor, h)
        
        if output.item() > 0.5:
            return "Positive", output.item()
        else:
            return "Negative", 1 - output.item()
    
    def analyze_company_news(self, stock_symbol):
        """Analyze sentiment for all news articles about a company"""
        load_dotenv()
        
        current_date = datetime.today()
        start_date = current_date - relativedelta(days=1)
        finnhub_client = finnhub.Client(api_key=os.getenv("FINNHUB_API_KEY"))
        
        try:
            all_news = finnhub_client.company_news(
                stock_symbol, 
                _from=start_date.strftime('%Y-%m-%d'), 
                to=current_date.strftime('%Y-%m-%d')
            )
        except Exception as e:
            raise ValueError("No news articles found for the given stock symbol")
        
        results = {
            'output': "",
            'count': 0,
            'pos_count': 0,
            'pos_score': 0,
            'neg_count': 0,
            'neg_score': 0
        }
        
        for i, news in enumerate(all_news, 1):
            text = news['headline'] + "--->" + news['summary']
            sentiment, score = self.predict_sentiment(text)
            
            results['count'] += 1
            if sentiment == "Positive":
                results['pos_count'] += 1
                results['pos_score'] += score
            else:
                results['neg_count'] += 1
                results['neg_score'] += score
                
            results['output'] += f"Company News (Past Day) #{i} : {text}\n{sentiment} market sentiment detected! With probability of: {score:.4f}\n\n"
        
        # Add summary
        if results['pos_score'] > results['neg_score']:
            overall_score = (results['pos_score'] - results['neg_score']) / results['count']
            results['output'] += (
                f"Overall Sentiment: Positive with score of {overall_score:.4f} "
                f"equivalent to {results['pos_count']} positive news and {results['neg_count']} negative news.\n"
            )
        elif results['neg_score'] > results['pos_score']:
            overall_score = (results['neg_score'] - results['pos_score']) / results['count']
            results['output'] += (
                f"Overall Sentiment: Negative with score of {overall_score:.4f} "
                f"equivalent to {results['neg_count']} negative news and {results['pos_count']} positive news.\n"
            )
        else:
            results['output'] += "Overall Sentiment: Neutral with equal positive and negative news.\n"
        
        results['output'] += f"Total News Articles Analyzed: {results['count']}\n"
        return results

# Initialize the sentiment analyzer
sentiment_analyzer = SentimentAnalyzer()

@csrf_exempt
@api_view(['POST'])
def sen_display(request):
    try:
        stock_symbol = request.data.get('stock_symbol')
        if not stock_symbol:
            return Response({'error': 'Stock symbol not provided'}, status=400)
        
        analysis_results = sentiment_analyzer.analyze_company_news(stock_symbol)
        return Response({'response': analysis_results['output']}, status=200)
    
    except ValueError as e:
        return Response({'response': str(e)}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)