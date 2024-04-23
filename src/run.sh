#!/bin/bash
cd ./src && uvicorn main:app --reload --port 8004 --host 0.0.0.0 --env-file ../.env