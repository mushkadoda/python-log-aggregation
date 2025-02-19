import os
import re
import json
import asyncio
import aiofiles
from collections import Counter


# Directories with log files
LOG_DIR = "tmp/logs/"
PROCESSED_LOG_FILE = "static/processed_logs.json"
ANALYTICS_FILE = "static/sample_output.json"

# Regex pattern for parsing logs
LOG_PATTERN = re.compile(r"\[(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2})\] (?P<server>\S+) (?P<level>INFO|WARN|ERROR) (?P<message>.+)")

async def process_log_file(file_path, aggregated_logs, log_counter, user_activity, api_data):
    # Process a single log file asynchronously
    async with aiofiles.open(file_path, mode='r') as file:
        async for line in file:
            match = LOG_PATTERN.match(line.strip())
            if match:
                log_entry = match.groupdict()
                timestamp = f"{log_entry['date']} {log_entry['time']}"
                aggregated_logs.append(log_entry)

                # Count log levels
                log_counter[log_entry["level"]] += 1

                # Track user activity based on all "User" activity
                if "User" in log_entry["message"]:
                #  Alternative filter, track user only based on "logged in" and "logged out" events
                #  "logged in" in log_entry["message"] or "logged out" in log_entry["message"]:
                    user = re.search(r"User '(.+?)'", log_entry["message"])
                    if user:
                        username = user.group(1)
                        if username not in user_activity:
                            user_activity[username] = {"actions": 0, "last_seen": ""}
                        user_activity[username]["actions"] += 1
                        user_activity[username]["last_seen"] = timestamp

                # Count API errors
                if "API request failed" in log_entry["message"]:
                    api_data["failed"] += 1
                if "API request" in log_entry["message"]:
                    api_data["total"] += 1


async def aggregate_logs():
    # Aggregate logs from multiple files asynchronously
    aggregated_logs = []
    log_counter = Counter()
    user_activity = {}
    api_data = {"failed": 0, "total": 0}

    log_files = [os.path.join(LOG_DIR, f) for f in os.listdir(LOG_DIR) if f.endswith(".log")]

    # Process log files concurrently
    await asyncio.gather(*[process_log_file(file, aggregated_logs, log_counter, user_activity, api_data) for file in log_files])

    # Write logs to JSON file
    async with aiofiles.open(PROCESSED_LOG_FILE, mode='w') as file:
        await file.write(json.dumps(aggregated_logs, indent=4))

    # Calculate API error rate
    if api_data["total"] > 0:
        api_error_rate = (api_data["failed"] / api_data["total"] * 100)
    else:
        api_error_rate = 0

    # Analyze log data
    insights = {
        "log_count" : dict(log_counter),
        "user_activity": user_activity,
        "api_errors": {
            "failed": api_data["failed"],
            "total": api_data["total"],
            "error_rate": f'{round(api_error_rate, 2)}%'
        },
        "metatdata": {
            "total_logs": len(aggregated_logs),
            "total_files": len(log_files)
        }
    }

    # Write insights to JSON file
    async with aiofiles.open(ANALYTICS_FILE, mode='w') as file:
        await file.write(json.dumps(insights, indent=4))


# Run the async aggegation
if __name__ == "__main__":
    asyncio.run(aggregate_logs())
