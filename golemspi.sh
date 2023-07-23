#!/bin/bash
#
# Function to clean up and exit the script
# cleanup() {
#     echo "Cleaning up..."
#     kill -INT "$command_pid"  # Kill the background process
#     wait "$command_pid"
#     rm $logfile
#     exit 1
# }


cleanup() {
    echo "Cleaning up..."
    kill -INT "$command_pid"  # Kill the background process
    sleep 5  # Allow some time for the process to terminate normally
    if kill -0 "$command_pid" > /dev/null 2>&1; then
        # If the process is still running, kill it with SIGKILL
        kill -KILL "$command_pid"
    fi
    wait "$command_pid"
    rm $logfile
    exit 1
}

# Set the logfile name based on today's date and time
logfile="/tmp/log_$(date +'%Y-%m-%d_%H-%M-%S').log"
touch "$logfile"

# Function to run the command in the background
run_in_background() {
    CMD="golemsp run $@"
    $CMD > "$logfile" 2>&1 &
    command_pid=$!
}

# Trap the SIGINT signal (Control-C) and call the cleanup function
trap cleanup SIGINT

# Run the command in the background
run_in_background "$@"

python3 ./golemspi.py "$logfile"

cleanup  # Call the cleanup function to ensure the background process is killed on normal exit
