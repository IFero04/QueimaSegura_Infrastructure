#!/bin/bash
if [ "$USE_DEV_MODE" = "true" ];
    then fastapi dev main.py --proxy-headers --host 0.0.0.0 --port 8000; 
    else fastapi run main.py --proxy-headers --port 8000;
fi

echo "Executed script at $(date)"
