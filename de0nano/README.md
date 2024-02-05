# tt03p5-solo-squash on a DE0-Nano FPGA dev board

This directory contains a Quartus Prime Lite project that can be used to synthesise and run the top-most `tt_um_algofoogle_solo_squash` design on a DE0-Nano FPGA dev board (using an Altera Cyclone IV).

The file [`tt_um_algofoogle_solo_squash_de0nano.v`](./tt_um_algofoogle_solo_squash_de0nano.v) is the wrapper that bridges the `tt_um_algofoogle_solo_squash` Verilog module with the hardware of the DE0-Nano. I've not yet made a schematic or provided other details about the hardware I've got attached to my DE0-Nano, so rely on this file to find out which GPIOs I'm using, etc.

You can also refer to the [testing guide](../doc/testing.md) which will give an overview of what external hardware you need.

What more would you like to know? Get in touch and tell me!

