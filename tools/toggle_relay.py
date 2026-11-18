"""Turn the plug's Power switch on and off a few times over the ESPHome API."""
import asyncio, sys, time
from aioesphomeapi import APIClient, SwitchInfo

async def main(host, delay):
    cli = APIClient(host, 6053, None)
    await cli.connect(login=True)
    ents, _ = await cli.list_entities_services()
    sw = next(e for e in ents if isinstance(e, SwitchInfo))
    await asyncio.sleep(delay)
    for on in (True, False, True, False):
        print(f"{time.strftime('%H:%M:%S')}  Power -> {'ON' if on else 'OFF'}", flush=True)
        cli.switch_command(sw.key, on)
        await asyncio.sleep(4)
    await cli.disconnect()

asyncio.run(main(sys.argv[1], float(sys.argv[2])))
