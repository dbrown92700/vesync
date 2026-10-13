import asyncio
import os
from dotenv import load_dotenv
from pyvesync import VeSync

async def main():
    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    if not username or not password:
        print("Error: USERNAME or PASSWORD not found in .env file")
        return

    app = None
    try:
        app = VeSync(username, password, country_code='US')
        await app.login()
        
        await app.get_devices()
        devices = app.devices
        
        print(f"Found {len(devices)} devices:")
        for device in devices:
            # Using .device_name instead of .name
            print(f"- {device.device_name} (CID: {device.cid})")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if app:
            await app.__aexit__(None, None, None)

if __name__ == "__main__":
    asyncio.run(main())
