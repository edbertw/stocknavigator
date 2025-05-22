#!/bin/bash
pip install -r requirements.txt
cd mybackend
python manage.py collectstatic
