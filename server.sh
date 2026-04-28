#!/bin/bash
sudo source venv/bin/activate
sudo uvicorn app.main:app --reload