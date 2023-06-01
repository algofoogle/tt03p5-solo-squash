![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/wokwi_test/badge.svg)

> Note: this is an experimental repo for Tiny Tapeout 03p5 (3.5).
> It is essentially a fork of the experimental template:
> [tt03p5-submission-template](https://github.com/TinyTapeout/tt03p5-submission-template).
> Please talk to the Tiny Tapeout team before using it!

# "Solo Squash" TT03p5 submission

This is a minimalistic VGA "game" implemented in Verilog as a single "tile" submission to the experimental
Tiny Tapeout 03p5 Caravel project, destined to be made into an ASIC via the chipIgnite 2306Q shuttle.

The design itself is digital logic that implements a 640x480 VGA driver that allows one person to play
a super simple Pong-like game of bouncing a ball off a paddle and around 3 walls.

A much more detailed run-down of the design is found in the [`solo_squash` repo](https://github.com/algofoogle/solo_squash).

For more info about my previous Tiny Tapeout submission attempt, including a discussion of a bit of the
testing and local build process, see: [`anton1-tt03`](https://github.com/algofoogle/anton1-tt03)


# What is Tiny Tapeout?

TinyTapeout is an educational project that aims to make it easier and cheaper than ever to get your digital designs manufactured on a real chip!

Go to https://tinytapeout.com for instructions!

## How to change the Wokwi project

Edit the [info.yaml](info.yaml) and change the wokwi_id to match your project.


## How to enable the GitHub actions to build the ASIC files

Please see the instructions for:

* [Enabling GitHub Actions](https://tinytapeout.com/faq/#when-i-commit-my-change-the-gds-action-isnt-running)
* [Enabling GitHub Pages](https://tinytapeout.com/faq/#my-github-action-is-failing-on-the-pages-part)

## How does it work?

When you edit the info.yaml to choose a different ID, the [GitHub Action](.github/workflows/gds.yaml) will fetch the digital netlist of your design from Wokwi.

After that, the action uses the open source ASIC tool called [OpenLane](https://www.zerotoasiccourse.com/terminology/openlane/) to build the files needed to fabricate an ASIC.

## Resources

* [FAQ](https://tinytapeout.com/faq/)
* [Digital design lessons](https://tinytapeout.com/digital_design/)
* [Learn how semiconductors work](https://tinytapeout.com/siliwiz/)
* [Join the community](https://discord.gg/rPK2nSjxy8)

## What next?

* Share your GDS on Twitter, tag it [#tinytapeout](https://twitter.com/hashtag/tinytapeout?src=hashtag_click) and [link me](https://twitter.com/matthewvenn)!
