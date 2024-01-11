![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/wokwi_test/badge.svg) [![License is Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

> Note: this is an experimental repo for Tiny Tapeout 03p5 (3.5).
> It is essentially a fork of the experimental template:
> [tt03p5-submission-template](https://github.com/TinyTapeout/tt03p5-submission-template).
> Please talk to the Tiny Tapeout team before using it!

# "Solo Squash" TT03p5 submission

![Solo Squash silicon layout and simulation](./doc/solo_squash_tt03p5_header.png)

This is a minimalistic VGA "game" implemented in Verilog as a 1x1 "tile" submission to the experimental
Tiny Tapeout 03p5 Caravel project, destined to be made into an ASIC via the chipIgnite 2306Q shuttle.

The design itself is digital logic that implements a 640x480 VGA driver that allows one person to play
a super simple Pong-like game of bouncing a ball off a paddle and around 3 walls.

**A much more detailed run-down of the design is found in the [`solo_squash` repo](https://github.com/algofoogle/solo_squash).**

For more info about my previous Tiny Tapeout submission attempt, including a discussion of a bit of the
testing and local build process, see: [`anton1-tt03`](https://github.com/algofoogle/anton1-tt03)

**NOTE:** There is an extra feature in this design which is just an experiment: I've included a
leading zero counter with a 24-bit input that comes from the concatention of these internal
signals of the solo_squash module: `{offset[3:0],v,h}` -- It outputs the count
(from 0 to 24) on `uio_out[4:0]`, and also sets `uio_out[5]` if the count is 24
(i.e. "all zeroes" signal).


## How it works

### What is Solo Squash?

A 25MHz clock drives a simple 640x480 VGA generator, and in turn generates a simple "game"
that displays a bouncing ball within a playfield of 3 walls, with the 4th side open except
for a lone paddle that you as the player control. Pong? What's that?
Sounds too new-fangled for me!


### What's the objective of the game?

Keep the ball bouncing in the playfield for as long as you can. Sometimes it's harder than it sounds!
There is no score, and no other objective. It's educational, and offers mild thrills,
just like Edna.

One button moves the paddle up, the other down, at a constant rate.

Bounces off the walls produce a simple tone, and off the paddle produce a slightly different tone.
Letting the ball escape will humiliatingly drone on for a bit before the ball returns to play.

A hint: Let the drifting blue background pattern be your guide for where the ball will
ultimately end up as it bounces around.


### How does the design work?

Tones produced on `speaker` are derived from divisions (bits) of the vertical scan register.

Rendering of the walls, ball, and paddle are done using registers (more-so than combo logic)
that turn the VGA red/green channels on and off at the right times as the VGA beam marches on.
The blue background pattern is done with bitwise logic from the horizontal and vertical scan
counters, with another counter to create the drifting effect by applying an offset.

Detecting when a bounce happens is done by detecting if any pixel we're rendering coexists
in the ball and wall (or paddle). Long tone and ball return is actually just an accidental
side effect of counters rolling over, but that's good enough for me!


## How to test

### Testing the ASIC

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

That's enough to get started. From power-on, a display should be visible with a 'paddle' at the left screen edge, 3 'walls' on the other screen edges, a bouncing ball (or one that appears at least within a few seconds), and a scrolling patterned blue background.

NOTE: It's not necessary to assert reset, but without it you might find that the paddle 'overflows' and fills the full height of the left edge.

#### Additional stuff to test:

1.  There is a speaker output on `uo_out[5]`. It plays two different tones. Try connecting a speaker (or piezo) and 1k&ohm; resistor in series to GND. Optionally try amplifying the output.
2.  Assuming all `ui_in` inputs are *weakly pulled low* by default, you can assert a high signal on `ui_in[2]` ("down") or `ui_in[3]` ("up") to cause the paddle to move. Use pushbuttons, or just switches will do.
3.  Holding a high on `ui_in[0]` ("pause") will freeze all animation, and holding a high on `ui_in[1]` ("new_game") will revert the game to its starting state while the background scrolling animation continues.

NOTE: Debouncing is not required on these inputs; they have 2xDFF sync internally.

#### Advanced testing:

1.  `uo_out[6]` is `col0` and is a single pulse (one clock period wide) that occurs every 800 clocks -- i.e. it is asserted during the first pixel of every line.
2.  `uo_out[7]` is `row0` and is a single pulse (800 clocks wide) that occurs every 420,000 clocks -- i.e. it is asserted during the first line of every frame.
3.  You could trigger an oscilloscope on the rising edge of `row0` and see the single clock pulse occurring on `col0` at the same time.
4.  `bidir[6]` is `debug1` and by default it outputs the *un*registered green signal. Likewise, `bidir[7]` (`debug2`) is unregistered red. You could swap out one or both of `uo_out[2:1]` for these and you should see that they change 1 pixel ahead of their respective registered versions.
5.  If `ui_in[4]` is *high*, then the outputs of `bidir[7]` and `[6]` change to unregistered blue and the "visible" flag respectively.

#### Diagnosing issues:

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


### Testing by Verilator simulation

For more info on this, see [Visual simulation with Verilator](https://github.com/algofoogle/solo_squash#visual-simulation-with-verilator).


# What is Tiny Tapeout?

TinyTapeout is an educational project that aims to make it easier and cheaper than ever to get your digital designs manufactured on a real chip!

Go to https://tinytapeout.com for instructions!

## Resources

* [FAQ](https://tinytapeout.com/faq/)
* [Digital design lessons](https://tinytapeout.com/digital_design/)
* [Learn how semiconductors work](https://tinytapeout.com/siliwiz/)
* [Join the community](https://discord.gg/rPK2nSjxy8)

## What next?

* Share your GDS on Twitter, tag it [#tinytapeout](https://twitter.com/hashtag/tinytapeout?src=hashtag_click) and [link me](https://twitter.com/matthewvenn)!
