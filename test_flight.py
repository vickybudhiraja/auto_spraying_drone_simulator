import asyncio
from mavsdk import System

async def main():
    print("Creating System...")
    drone = System()

    print("Connecting on 14540...")
    await drone.connect(system_address="udpin://0.0.0.0:14540")
    print("connect() returned")

    print("Waiting for vehicle...")
    async for state in drone.core.connection_state():
        print("is_connected:", state.is_connected)
        if state.is_connected:
            break

    print("Arming...")
    await drone.action.arm()

    print("Taking off...")
    await drone.action.takeoff()
    await asyncio.sleep(8)

    print("Landing...")
    await drone.action.land()
    await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())