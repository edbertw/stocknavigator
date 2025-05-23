#!/bin/bash
cd mybackend
python3.11 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 manage.py collectstatic
