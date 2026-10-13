# VeSync Smart Plug Recovery Tool

This project provides a set of tools to monitor and automatically recover a smart plug (specifically the "Cisco DeskPro") when it stops drawing power, indicating a device crash.

## Installation

1. **Clone or move the project to your desired directory.**
2. **Create a virtual environment:**
   ```bash
   cd vesync
   python3 -m venv venv
   ```
3. **Activate the environment and install dependencies:**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Configure Credentials:**
   Create or edit the `.env` file in the `vesync` directory with your account details:
   ```env
   USERNAME=your_email@gmail.com
   PASSWORD=your_password
   ```

## Usage

### Manual Checks
To list all devices on your account:
```bash
source venv/bin/activate
python list_devices.py
```

To check the current power draw and history of the DeskPro:
```bash
source venv/bin/activate
python check_power_history.py
```

### Automatic Recovery
The `recover_deskpro.py` script checks if the power draw is below a threshold. If it is, it waits 5 minutes (to avoid interrupting firmware updates) and then attempts to toggle the power off and on up to 3 times to restore the device.

## Automation (Cronjob)

To run the recovery script automatically every hour, add the following entry to your crontab. 

1. Open the crontab editor:
   ```bash
   crontab -e
   ```

2. Add the following line (replace `/absolute/path/to/vesync` with the actual full path to your project folder):
   ```cron
   0 * * * * /absolute/path/to/vesync/venv/bin/python /absolute/path/to/vesync/recover_deskpro.py >> /absolute/path/to/vesync/recovery.log 2>&1
   ```

This will execute the script at the top of every hour and log all output to `recovery.log`.
