import asyncio
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from pyvesync import VeSync

# Configuration
TARGET_DEVICE_NAME = "Cisco DeskPro"
POWER_THRESHOLD = 2.0  # Watts. Adjust this based on the actual 'off' power draw
RECOVERY_ATTEMPTS = 3
OFF_DURATION = 10  # Seconds to keep plug off
UPGRADE_WAIT_TIME = 300  # 5 minutes to wait if low power is detected

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def check_power(app, device):
    """Updates device state and returns the current power draw in Watts."""
    await device.update()
    # Power is stored in device.state.power
    power = getattr(device.state, 'power', None)
    return power

async def recover_device(app, device):
    """Attempts to recover the device by toggling power."""
    for attempt in range(1, RECOVERY_ATTEMPTS + 1):
        logger.info(f"Recovery attempt {attempt}/{RECOVERY_ATTEMPTS} for {device.device_name}...")
        
        # Toggle Off
        logger.info("Turning device OFF...")
        await device.turn_off()
        await asyncio.sleep(OFF_DURATION)
        
        # Toggle On
        logger.info("Turning device ON...")
        await device.turn_on()
        
        # Wait for device to boot up before checking power
        # Giving it 60 seconds to start drawing power
        logger.info("Waiting 60s for boot-up...")
        await asyncio.sleep(60)
        
        power = await check_power(app, device)
        logger.info(f"Power draw after recovery attempt {attempt}: {power}W")
        
        if power is not None and power > POWER_THRESHOLD:
            logger.info("Recovery successful! Device is drawing power.")
            return True
            
    logger.error("Failed to recover device after maximum attempts. It might be physically unplugged or broken.")
    return False

async def main():
    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    if not username or not password:
        logger.error("USERNAME or PASSWORD not found in .env file")
        return

    app = None
    try:
        app = VeSync(username, password, country_code='US')
        await app.login()
        await app.get_devices()
        
        # Find the target device
        device = next((d for d in app.devices if d.device_name == TARGET_DEVICE_NAME), None)
        
        if not device:
            logger.error(f"Device '{TARGET_DEVICE_NAME}' not found in account.")
            return

        # 1. Initial power check
        power = await check_power(app, device)
        logger.info(f"Current power draw for {TARGET_DEVICE_NAME}: {power}W")

        if power is not None and power > POWER_THRESHOLD:
            logger.info("Device is operating normally.")
            return

        # 2. Low power detected. Could be a crash OR an upgrade.
        logger.warning(f"Low power detected ({power}W). Waiting {UPGRADE_WAIT_TIME}s to rule out software upgrade...")
        await asyncio.sleep(UPGRADE_WAIT_TIME)
        
        # 3. Check again after wait period
        power = await check_power(app, device)
        logger.info(f"Power draw after wait: {power}W")
        
        if power is not None and power > POWER_THRESHOLD:
            logger.info("Power returned. Device was likely performing an upgrade.")
            return

        # 4. Still low power. Attempt recovery.
        logger.warning("Power still low. Starting recovery sequence...")
        success = await recover_device(app, device)
        
        if success:
            logger.info("System restored successfully.")
        else:
            logger.error("System restoration failed.")

    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
    finally:
        if app:
            await app.__aexit__(None, None, None)

if __name__ == "__main__":
    asyncio.run(main())
