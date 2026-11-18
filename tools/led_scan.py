"""Drive each test GPIO low then high for a few seconds, one at a time."""
import asyncio, sys, time
from aioesphomeapi import APIClient, SwitchInfo

async def main(host, delay):
    cli = APIClient(host, 6053, None)
    await cli.connect(login=True)
    ents, _ = await cli.list_entities_services()
    sws = [e for e in ents if isinstance(e, SwitchInfo) and e.name.startswith("T ")]
    for s in sws: cli.switch_command(s.key, False)
    await asyncio.sleep(delay)
    for s in sws:
        for on in (True, False):
            print(f"{time.strftime('%H:%M:%S')}  {s.name[2:]} -> {'HIGH' if on else 'LOW'} (4 s)", flush=True)
            cli.switch_command(s.key, on); await asyncio.sleep(4)
        cli.switch_command(s.key, False); await asyncio.sleep(1)
    await cli.disconnect()

asyncio.run(main(sys.argv[1], float(sys.argv[2])))
