"""Set one test switch (e.g. 'T GPIO1') to on/off and leave it there."""
import asyncio, sys
from aioesphomeapi import APIClient, SwitchInfo

async def main(host, name, on):
    cli = APIClient(host, 6053, None)
    await cli.connect(login=True)
    ents, _ = await cli.list_entities_services()
    sw = next(e for e in ents if isinstance(e, SwitchInfo) and e.name == name)
    cli.switch_command(sw.key, on)
    await asyncio.sleep(0.5)
    await cli.disconnect()
    print(f"{name} -> {'HIGH' if on else 'LOW'}")

asyncio.run(main(sys.argv[1], sys.argv[2], sys.argv[3] == "on"))
