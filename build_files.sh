#!/bin/bash
python3.11 -m venv venv
source venv/bin/activate
cd mybackend
pip3 install -r requirements.txt
python3 manage.py collectstatic --noinput 
