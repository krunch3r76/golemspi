#!/bin/bash


cleanup() {
    echo "Cleaning up..."
    if kill -0 "$command_pid" > /dev/null 2>&1; then
        # Send the interrupt signal to command_pid and its child processes
        pkill -INT -P "$command_pid"
        for i in $(seq 1 10); do  # wait up to 10 seconds
            # Check if the process and any of its child processes are still running
            if ! (kill -0 "$command_pid" > /dev/null 2>&1 || pgrep -P "$command_pid" > /dev/null 2>&1); then
                break  # exit the loop when process is no longer running
            fi
            sleep 1  # wait for 1 second between checks
        done
        # If the process or its child processes are still running, kill them
        if kill -0 "$command_pid" > /dev/null 2>&1 || pgrep -P "$command_pid" > /dev/null 2>&1; then
            pkill -KILL -P "$command_pid"
            kill -KILL "$command_pid"
        fi
    fi
    rm $logfile
    stty sane
    sleep 3
    exit 1
}

# Set the logfile name based on today's date and time
logfile="/tmp/log_$(date +'%Y-%m-%d_%H-%M-%S').log"
touch "$logfile"

# Function to run the command in the background
run_in_background() {
    CMD="golemsp run $@"

    # $CMD > "$logfile" 2>&1 &
    $CMD 2>&1 | tee -a "$logfile" 2>/dev/null
    command_pid=$!
}

# Trap the SIGINT signal (Control-C) and call the cleanup function
trap cleanup SIGINT

# Run the command in the background
run_in_background "$@"
sleep 0.01
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
python3 $script_dir/golemspi.py "$logfile"

cleanup  # Call the cleanup function to ensure the background process is killed on normal exit
