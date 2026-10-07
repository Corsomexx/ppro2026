#!/usr/bin/env bash
echo "Spouštím server půjčovny Hory a voda (Uvicorn / FastAPI)..."
python -m uvicorn src.main:app --reload --port 8000
