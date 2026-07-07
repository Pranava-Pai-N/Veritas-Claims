#!/bin/bash

# Kill all the background tasks
trap 'kill $(jobs -p)' EXIT

echo "Starting backend python server" 
uvicorn main:app --reload &


echo "Starting streamlit frontend"
cd frontend/pages && streamlit run dashboard.py  &

wait