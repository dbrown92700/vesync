import asyncio
import os
from dotenv import load_dotenv
from pyvesync import VeSync

async def main():
    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    app = None
    try:
        app = VeSync(username, password, country_code='US')
        await app.login()
        await app.get_devices()
        
        device = next((d for d in app.devices if d.device_name == "Cisco DeskPro"), None)
        
        if not device:
            print("Device 'Cisco Deskpro' not found.")
            return

        # 1. Pull current power draw
        await device.update()
        power = getattr(device.state, 'power', None)
        voltage = getattr(device.state, 'voltage', None)
        current = getattr(device.state, 'current', None)
        
        print(f"--- Current Status for {device.device_name} ---")
        print(f"Power:    {power} W")
        print(f"Voltage:  {voltage} V")
        print(f"Current:  {current} A")
        print("-" * 40)

        # 2. Check historical capabilities
        print("\n--- Historical Data Availability ---")
        if device.supports_energy:
            print("✅ Energy monitoring is supported.")
            
            # Pull different timeframes
            # These methods update the state object's history attributes
            await device.get_weekly_energy()
            await device.get_monthly_energy()
            await device.get_yearly_energy()
            
            print(f"Weekly History:   {device.state.weekly_history is not None}")
            print(f"Monthly History: {device.state.monthly_history is not None}")
            print(f"Yearly History:   {device.state.yearly_history is not None}")
            
            if device.state.weekly_history:
                print("\nSample of Weekly History (Raw object):")
                print(device.state.weekly_history)
        else:
            print("❌ Energy monitoring is NOT supported for this device.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if app:
            await app.__aexit__(None, None, None)

if __name__ == "__main__":
    asyncio.run(main())
