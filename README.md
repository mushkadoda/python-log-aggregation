# python-log-aggregation

## Prerequisites
Python3.9 or higher

## Usage
Put some log files in the folder
```
aggregator_app/tmp/logs
```
Or remove the `.sample` suffix from the existing files



in a terminal
```
Go to "python-log-aggregation/aggregator_app" direectory
```

Run the following commands:
```
python3 -m venv .
pip3 install -r requirements.txt
python3 -m flask run
```