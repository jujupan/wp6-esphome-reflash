"""Print every state change from the plug over the ESPHome API."""
import asyncio, sys, time
from aioesphomeapi import APIClient

async def main(host, seconds):
    cli = APIClient(host, 6053, None)
    await cli.connect(login=True)
    ents, _ = await cli.list_entities_services()
    names = {e.key: e.name for e in ents}
    def on_state(s):
        print(f"{time.strftime('%H:%M:%S')}  {names.get(s.key, s.key)}: {getattr(s, 'state', s)}", flush=True)
    cli.subscribe_states(on_state)
    print(f"watching {host} for {seconds}s", flush=True)
    await asyncio.sleep(seconds)
    await cli.disconnect()

asyncio.run(main(sys.argv[1], float(sys.argv[2])))
