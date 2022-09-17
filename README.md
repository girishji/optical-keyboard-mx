# Optical Keyboard using Gateron MX Optical Switches


Optical keyboard PCB based on Gateron MX optical switches (KiCad project).

Keyboard matrix uses column-to-row scanning approach. The IR
(infra-red) led's in each column is connected to a GPIO pin configured as
output. A column is powered by setting the pin HIGH.
Each row is connected to a GPIO pin configured as input so that voltage drop
across the load register of PT (Phototransistor) can be read.

QMK code is in a [PR](https://github.com/qmk/qmk_firmware/pull/17852). In the
qmk tree you could find it in keyboards/opticalkb/rev1 folder.

This is not a high-performance keyboard since IR's are provided with very
minimal current (way below the suggested operating value). This is done so as
to keep the design simple. A single GPIO pin of STM32F4 (set as output)
can provide 20 ma. Each IR is supplied with ~3.6 ma. The total current for 5
rows (IRs) falls within the allowable maximum current per pin. Yet it achieves
a scan rate of 400 hz. Since there is no debounce delay the latency (before USB
transit) is 2.5 ms. Compared to mechanical keyboards (with 5 ms debounce delay)
this keyboard achieves respectable performance. It is possible to push scanning
rate much higher, but it requires a different matrix design and additional switching
components to increase current to IR. 

Follow the [blog](https://girishji.github.io/) for more keyboard designs in the future.

### BUILD

It takes minimal effort to put together this keyboard. When you order from
jlcpcb have them assemble only 2 (out of 5) pcbs with SMD components (choose
green FR4). The other pcb's can be used as base plates. The two pcb's (one
with SMD assembly and one without) are soldered together using a special type
of tin-coated standoff. The switch plate is then screwed at the top. There is
also a wrist rest. You can eliminate the wrist area completely by editing the
edge-cuts layer of main pcb. All pcb's are 1.6 mm thickness.

All the part numbers (of jlcpcb) are embedded in the symbols so you can generate BOM.

Switch plate is in `switch-plate` folder. Wrist support is in `wrist-support` folder.

### PARTS

- SMTSO-M2-3.5ET standoff (17 pcs)
- M2x4mm screws (17 pcs)
- Blackpill STM32F401 MCU

For wrist support:

- M2x4mm screws (8 pcs)
- SMTSO-M2-10ET standoff (8)

### PICS

![front side](https://i.imgur.com/WgVoHNz.jpg)
![back side](https://i.imgur.com/aYTM2Oq.jpg)
![PCB](https://i.imgur.com/2z5SLGM.png)
![Switch plate](https://i.imgur.com/m8c4q6x.png)
![Wrist rest](https://i.imgur.com/8WCkxZB.png)


