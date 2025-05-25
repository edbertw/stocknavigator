# Stock-Navigator

## What is it?
One stop full-stack containerized application for stock market enthusiasts to find out more information about their favourite stocks. Information range from non-technical to highly statistical metrics and interactive charts used to measure stock performance and future opportunities for prospective investors. Another feature includes curated stock price prediction using LSTM (Long Short Term Memory) RNN architecture with results displayed in a chart. We also improve service by integrating advanced AI technologies such as RAG to answer user queries based on a thorough web-scraped knowledge base.

## How to run?
1. Activate virtual environment available under mybackend directory
2. `pip3 install -r requirements.txt`
3. Navigate to `mybackend` directory and run `python manage.py runserver` to start production server (Already rendered with react components, so no need to start frontend server) 

Alternatively, if docker can be utilized and port is available
1. `docker build -t stocknavigator .`
2. `docker run -p 8000:8000 stocknavigator`

## Key Technologies
1. JavaScript (React.js)
2. HTML
3. CSS
4. Django & Django REST Framework
5. Pandas
6. NumPy
7. Plotly.js
8. TensorFlow
9. yFinance API
10. Docker
11. LangChain
12. HuggingFace
13. BeautifulSoup
14. Transformers
15. FAISS Vector DB
