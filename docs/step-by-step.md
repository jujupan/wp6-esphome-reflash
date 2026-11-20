# Step by step: from a closed plug to a reflashed plug in the wall

This is the full procedure that was used on this unit. The solder points are
numbered as in the [diagram](solder-points.svg). The pins are in the
[README](../README.md#what-this-unit-actually-uses).

## Warnings: read these first

> **WARNING: Mains voltage can kill you.** Never connect the plug to the wall
> while the case is open or while a wire is attached. Remove the plug from the
> wall before you start, and keep it out until step 42.

> **WARNING: Use 3.3 V only.** 5 V can destroy the ESP8285. Set the adapter
> jumper to 3.3 V before you connect it.

> **CAUTION: Disconnect the USB cable before you move a wire.** Move one wire at
> a time.

> **CAUTION: Stop if a part becomes warm.** Disconnect the USB cable immediately.
> Do not continue until you find the cause.

> **CAUTION: Make a backup before you write.** Do not use `write-flash` or
> `erase-flash` until the original firmware is saved in two places.

## What you need

- A USB-to-serial adapter with a 3.3 V setting (this unit used one at
  `/dev/cu.usbserial-0001`)
- A soldering iron, thin wire, flux and solder wick
- A breadboard and jumper wires, plus one loose jumper for the RST tap
- Isopropyl alcohol and a small brush
- A laptop with this repo, and a 2.4 GHz Wi-Fi network

## A. Prepare the laptop

1. Install the tools:
   ```sh
   uv venv --python 3.13 .venv
   uv pip install --python .venv/bin/python esphome esptool pyserial aioesphomeapi
   ```
   Use Python 3.13. Python 3.15 cannot build `ruamel.yaml.clib`.
2. Copy the secrets template:
   ```sh
   cp secrets.example.yaml secrets.yaml
   ```
3. Open the file in vim: `vim secrets.yaml`.
4. Type `i` to start insert mode. Replace the three values with your own.
5. Push `Esc`, then type `:wq` and push `Enter` to save.
6. Build the firmware: `.venv/bin/esphome compile wp6-lamp.yaml`.
   Make sure that the build ends with `SUCCESS`.

## B. Open the plug

7. Make sure that the plug is not in the wall.
8. Push a thin, flat blade into the seam of the case and pry it open. This unit
   was opened with an offset spatula. A flathead screwdriver also works.
   Pry slowly around the seam. Do not push the blade deep into the case.
9. Find the parts. Refer to `docs/photos/board-overview.jpg`:
   - The T201 module stands vertically on the main board.
   - The GND, IO0 and RST pads are on the back of the module.
   - C19, LED1 and the button K1 are on the main board.

## C. Solder the wires

The module's edge joints are too tight to reach. Thus 3V3, TX and RX come from
the main board.

10. Solder a wire to the **C19 + pad** (point 1). This is 3V3.
11. Solder a wire to a **GND pad** on the module back (point 2).
12. Solder a wire to the **LED leg without the black sleeve** (point 3). This is
    the chip TX.
13. Find the K1 marking. The pair of K1 legs next to the marking is GND. Solder a
    wire to a leg of the **other pair** (point 4). This is the chip RX.
14. Solder a wire to the **IO0 pad** (point 5).
15. Do not solder RST (point 6). You only touch it.
16. Examine each joint. Make sure that no joint touches a different pad.

## D. Connect the adapter

17. Make sure that the USB cable is disconnected.
18. Set the adapter jumper to **3.3 V**.
19. Connect the wires on the breadboard:

    | Plug point | Adapter pin |
    |---|---|
    | 1: C19 + pad | 3V3 |
    | 2: GND pad | GND |
    | 3: bare LED leg | RXD |
    | 4: K1 leg, not GND | TXD |
    | 5: IO0 pad | not connected yet |

## E. Test the serial link

20. Connect the USB cable. Make sure that nothing becomes warm.
21. Start the listener:
    `.venv/bin/python tools/listen.py /dev/cu.usbserial-0001 74880 30`
22. While it listens, touch the loose jumper from GND to the **RST pad** for
    1 second. The boot message must appear. If it does not, disconnect USB and
    examine the RXD and GND wires.

    Do not replug USB to reset the chip. macOS opens the port too late and you
    miss the boot message.

## F. Enter flashing mode

23. Disconnect the USB cable.
24. Connect the IO0 wire to GND on the breadboard.
25. Connect the USB cable. Start `.venv/bin/python tools/bootmode.py /dev/cu.usbserial-0001`.
26. Tap RST to GND. Make sure that the output shows `boot mode:(1,7)`.
    `boot mode:(3,x)` means normal boot: examine the IO0 wire.
27. Read the chip ID. Use `--before no-reset --after no-reset` every time,
    because there are no DTR/RTS wires:
    ```sh
    PORT=/dev/cu.usbserial-0001
    .venv/bin/python -m esptool --port $PORT --before no-reset --after no-reset chip-id
    ```
    It must show an ESP8285 and its MAC address.

## G. Back up the original firmware

28. Read the flash two times. Tap RST before each read:
    ```sh
    mkdir -p backup
    .venv/bin/python -m esptool --port $PORT --before no-reset --after no-reset \
      read-flash 0 0x100000 backup/wp6-backup-1.bin
    .venv/bin/python -m esptool --port $PORT --before no-reset --after no-reset \
      read-flash 0 0x100000 backup/wp6-backup-2.bin
    shasum -a 256 backup/*.bin > backup/SHA256SUMS && cat backup/SHA256SUMS
    ```
    The two hashes must be the same. If they are different, read again.
29. Copy the backup to a second location that is not this laptop. Do not put it
    in git: it can contain your old Wi-Fi password and the Tuya device key.

## H. Write ESPHome

30. Make sure that the backup is in two places. Then tap RST and write:
    ```sh
    .venv/bin/python -m esptool --port $PORT --before no-reset --after no-reset \
      write-flash 0x0 .esphome/build/wp6-lamp/.pioenvs/wp6-lamp/firmware.bin
    ```
    Make sure that the output ends with `Hash of data verified`.

## I. Test on the bench

31. Disconnect the USB cable. Disconnect the IO0 wire from GND.
32. Connect the USB cable. The plug starts ESPHome and connects to Wi-Fi.
    Do not connect it to the wall.
33. Watch the states: `.venv/bin/python tools/watch_states.py wp6-lamp.local 60`.
    Push the button 3 times. Each push must change `Power`.
34. Make sure that an update over Wi-Fi works: `.venv/bin/esphome run wp6-lamp.yaml`.
    Select the Wi-Fi (OTA) option, not the serial port. After this, you do not
    need the wires.

## J. Remove the wires and close the plug

35. Disconnect the USB cable. Disconnect all wires from the adapter.
36. Desolder all five wires from the plug. Do this before you close the case.
37. Clean the flux from each joint with isopropyl alcohol and a brush. Let it dry.
38. Examine the board. Make sure that there are no solder balls, wire strands or
    bridges between pads. Make sure that C19, the LED and K1 are not damaged.
39. Put the board back in the case. Make sure that no wire or tool stays inside.
40. Close the case fully.

## K. Put the plug in the wall

41. Make sure that the case is closed and that no wire is attached.
42. Connect the plug to the wall. Do not connect a load yet.
43. Push the button 4 times. The relay must click each time, and the red LED must
    show the Power state.
44. Wait 5 minutes. Then touch the case. If it is warm, disconnect the plug from
    the wall and do not use it.
45. Add the plug to Home Assistant. After the plug is in the wall, it shows in
    the **Devices** tab as a discovered ESPHome device (`wp6-lamp`). Select it
    and select **Configure**.
46. Connect the load. Make sure that Home Assistant can switch it.

## If you need the original firmware again

The backup restores the Tuya firmware. Do steps 7 to 27 again, then write
`backup/wp6-backup-1.bin` at `0x0` instead of the ESPHome firmware.
