import random
import datetime

LOG_LEVELS = ["INFO", "INFO", "INFO", "DEBUG", "DEBUG", "WARNING", "ERROR"]
SERVICES = ["AuthService", "PaymentGateway", "DataProcessor", "APIServer", "FrontendRouter", "DBConnection"]
MESSAGES = {
    "INFO": [
        "User {id} logged in successfully.",
        "Request processed in {ms}ms.",
        "Data fetch complete for resource: {resource}.",
        "Starting background job: {job_name}.",
        "Configuration loaded from environment.",
    ],
    "DEBUG": [
        "Cache miss for key: {key}.",
        "Payload received: {payload}",
        "Checking permissions for user: {id}",
        "Variable value: {var} = {value}",
    ],
    "WARNING": [
        "API response time degradation detected: {ms}ms.",
        "Database connection pool nearing capacity.",
        "Deprecated function {func} called.",
        "Configuration key '{key}' not found, using default.",
    ],
    "ERROR": [
        "Failed to connect to database: Connection timed out.",
        "Unhandled exception in {service}: {exception}.",
        "Payment failed for user {id}, reason: Insufficient funds.",
        "Could not resolve dependency: {dependency}.",
    ],
}

def generate_log_line(timestamp):
    """Generates a single, realistic log line for a given timestamp."""
    level = random.choice(LOG_LEVELS)
    service = random.choice(SERVICES)

    message_template = random.choice(MESSAGES[level])
    message = message_template.format(
        id=random.randint(100, 999),
        ms=random.randint(10, 500),
        resource=f"/api/v2/items/{random.randint(1, 100)}",
        job_name=random.choice(["CacheClear", "ReportGenerator"]),
        key=f"user:profile:{random.randint(100, 999)}",
        payload="'{...}'",
        var="is_admin",
        value=random.choice(["true", "false"]),
        func="getUserProfile_v1()",
        service=service,
        exception=random.choice(["NullPointerException", "IllegalArgumentException"]),
        dependency="com.example.library:1.2.3"
    )

    timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    return f"{timestamp_str} [{level}] [{service}] - {message}"

def main():
    """Generates a log file with 1500 lines spanning the last two weeks."""
    total_lines = 1500
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(days=14)
    interval_seconds = (end_time - start_time).total_seconds() / total_lines
    interval = datetime.timedelta(seconds=interval_seconds)

    with open("sample_logs.log", "w") as f:
        current_time = start_time
        for _ in range(total_lines):
            f.write(generate_log_line(current_time) + "\n")
            current_time += interval

    print("Successfully generated 'sample_logs.log' with 1500 lines covering the last two weeks.")

if __name__ == "__main__":
    main()
