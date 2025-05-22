#!/bin/bash
python3.11 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cd mybackend
python3 manage.py collectstatic
