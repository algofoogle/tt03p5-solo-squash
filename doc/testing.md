# How to test tt03p5-solo-squash

## Testing by Verilator simulation

For more info on this, see [Visual simulation with Verilator](https://github.com/algofoogle/solo_squash#visual-simulation-with-verilator).


## Testing the ASIC

The ASIC was recently manufactured, and the Tiny Tapeout team will be doing a bring-up very soon.

If you want, see [pin descriptions](https://github.com/algofoogle/tt03p5-solo-squash/blob/163eb866e6f9eb7d51b215f075e0b5d8e652645a/info.yaml#L116-L145).

Here are the most essential things that you'll need to know for bring-up and testing:

1.  This design is free-running. You should be able to plug and play. Provide a clock near 25.175MHz. Anything from 21MHz to 30MHz might work.
2.  `ui_in[4:0]` should be pulled low by default. They are active-high inputs for game interaction.
3.  Initially, leave all the "bidirectional" pins disconnected -- they are set to always  be outputs in this design.
4.  Connect these uo_outs to a VGA driver (e.g. VGA DAC PMOD):
    *   `uo_out[0]` => Blue
    *   `uo_out[1]` => Green
    *   `uo_out[2]` => Red
    *   `uo_out[3]` => HSYNC
    *   `uo_out[4]` => VSYNC
    *   NOTE: This is simple 3-bit colour (i.e. RGB111). If you have an RGB222 driver, you could connect each *single* colour channel output to *both* bits of each colour channel input.

That's enough to get started. From power-on, a display should be visible with a 'paddle' at the left screen edge, 3 'walls' on the other screen edges, a bouncing ball (or one that appears at least within a few seconds), and a scrolling patterned blue background:

<img src="./new-game-screen.png" width="640" height="480" alt="Initial game screen" />

NOTE: It's not necessary to assert reset, but without it you might find that the paddle 'overflows' and fills the full height of the left edge.

### Additional stuff to test:

1.  There is a speaker output on `uo_out[5]`. It plays two different tones. Try connecting a speaker (or piezo) and 1k&ohm; resistor in series to GND. Optionally try amplifying the output.
2.  Assuming all `ui_in` inputs are *weakly pulled low* by default, you can assert a high signal on `ui_in[2]` ("down") or `ui_in[3]` ("up") to cause the paddle to move. Use pushbuttons, or just switches will do.
3.  Holding a high on `ui_in[0]` ("pause") will freeze all animation, and holding a high on `ui_in[1]` ("new_game") will revert the game to its starting state while the background scrolling animation continues.

NOTE: Debouncing is not required on these inputs; they have 2xDFF sync internally.

### Advanced testing:

1.  `uo_out[6]` is `col0` and is a single pulse (one clock period wide) that occurs every 800 clocks -- i.e. it is asserted during the first pixel of every line.
2.  `uo_out[7]` is `row0` and is a single pulse (800 clocks wide) that occurs every 420,000 clocks -- i.e. it is asserted during the first line of every frame.
3.  You could trigger an oscilloscope on the rising edge of `row0` and see the single clock pulse occurring on `col0` at the same time.
4.  `bidir[6]` is `debug1` and by default it outputs the *un*registered green signal. Likewise, `bidir[7]` (`debug2`) is unregistered red. You could swap out one or both of `uo_out[2:1]` for these and you should see that they change 1 pixel ahead of their respective registered versions.
5.  If `ui_in[4]` is *high*, then the outputs of `bidir[7]` and `[6]` change to unregistered blue and the "visible" flag respectively.

### Diagnosing issues:

If you get a display but the ball is not moving:
*   `ui_in[1]` (`new_game`) might be high if the background is moving.
*   `ui_in[0]` (`pause`) might be high if the background is NOT moving.

If you don't get a display at all, check:
*   ~31.5kHz (88% duty cycle) on `uo_out[3]` (HSYNC).
*   ~60Hz (99.6% duty cycle) on `uo_out[4]` (VSYNC).
*   Is there any signal on any of `uo_out[2:0]` (i.e. RGB)?
*   Are there any speaker tones or audio-frequency waveforms on `uo_out[5]`?
*   Does a different clock speed work? Try from 20MHz up to 32MHz.
*   Do the *un*registered outputs (`bidir[7:6]`) produce a video image?
*   Is there any activity on `bidir[5:0]`? These are part of a 'leading zero counter' test that behaves like a *mostly* logarithmic counter that rolls over every 16 frames.

Additionally, while held in reset, the design should assert the following outputs:
*   `uo_out[7:0]`: `11011110`
*   `bidir[7:0]`: `11111000`


## Testing the ASIC using tt3p5 MicroPython SDK

> This is based on: https://github.com/TinyTapeout/tt3p5-demo-fw/blob/main/upython/README.md

Below is my attempt at a MicroPython script that should work with the TT03p5 to test this design.

**This is not finished yet!**

```python
from machine import Pin
from ttdemoboard.demoboard import DemoBoard, RPMode

def print_board_outputs(b:DemoBoard, expect_out:int=None, expect_bidir:int=None):
    print(f'uo_out={b.output_byte:08b} bidir={b.bidir_byte:08b}', end='')
    if expect_out is None:
        print()
    else:
        print(f'; expected uo_out={expect_out:08b} bidir={expect_bidir:08b}')

# Get a handle to the base board. ASICONBOARD configures our
# RP2040 GPIOs for proper cooperation with an attached TT chip:
board = DemoBoard(RPMode.ASICONBOARD)

# Enable my tt03p5-solo-squash design:
board.shuttle.tt_um_algofoogle_solo_squash.enable()
print(f'Project {board.shuttle.enabled.name} running ({board.shuttle.enabled.repo})')

# Ensure we are *reading* from all of the ASIC's bidir pins:
for pin in board.bidirs:
    pin.mode = Pin.IN

# Start with project clock low, and reset NOT asserted:
board.project_clk(0)
board.project_nrst(1)

# Print initial state of all outputs:
print_board_outputs(board)

# Assert reset, toggle the clock 3 times, then release reset:
board.project_nrst(0)
for i in range(3):
    board.project_clk(1); board.project_clk(0)
board.project_nrst(1)

# Now show the state of all outputs again:
print_board_outputs(board, expect_out=0b11011110, expect_bidir=0b11111000)

"""
    TBC!
"""

# # play with the inputs
# board.in0(1)
# board.in7(1)
# # or as a byte
# board.input_byte = 0xAA

# # start automatic project clocking
# board.clockProjectPWM(2e6) # clocking projects @ 2MHz

# # observe some outputs
# if board.out2():
#     print("Aha!")

# print(f'Output is now {board.output_byte}')

# # play with bidir pins (careful)
# board.uio2.mode = Pin.OUT
# board.uio2(1) # set high

# # if you changed modes on pins, like bidir, and want 
# # to switch project, reset them to IN or just
# board.pins.reset() 
# # before you switch projects

```

