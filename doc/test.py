from machine import Pin
from ttboard.mode import RPMode
from ttboard.demoboard import DemoBoard

# Used to show the state of the board's 8 uo_outs, and 8 bidir pins (treated also as outputs).
# Optionally also takes what they are *expected* to be, just for visual comparison.
def print_tt_outputs(b:DemoBoard, expect_out:int=None, expect_bidir:int=None):
    print(f'uo_out={b.output_byte:08b} bidir={b.bidir_byte:08b}', end='')
    if expect_out is None:
        print()
    else:
        print(f'; expected uo_out={expect_out:08b} bidir={expect_bidir:08b}')

# Get a handle to the base board: config.ini selects ASIC_ON_BOARD mode to configure
# our RP2040 GPIOs for proper cooperation with an attached TT chip:
tt = DemoBoard()

# Enable my tt03p5-solo-squash design:
##NOTE: This might not be needed given our config.ini
tt.shuttle.tt_um_algofoogle_solo_squash.enable()
print(f'Project {tt.shuttle.enabled.name} running ({tt.shuttle.enabled.repo})')

# Ensure we are *reading* from all of the ASIC's bidir pins:
for pin in tt.bidirs:
    pin.mode = Pin.IN

# Start with project clock low, and reset NOT asserted:
tt.project_clk(0)
tt.resetProject(False)

# Print initial state of all outputs:
print_tt_outputs(tt)

# Assert reset, pulse the clock 3 times, then release reset:
tt.resetProject(True)
for i in range(3):
    tt.clockProjectOnce()
tt.resetProject(False)

# Now show the state of all outputs again.
# Expected outputs are what the design should always assert while held in reset:
print_tt_outputs(tt, expect_out=0b11011110, expect_bidir=0b11111000)


"""
    TBC!
    TODO:
    -   Try running on upython/RP2040
    -   Can we make mapped pin names to suit actual pin names for our design?
    -   Test direct clocking and expected outputs
    -   Test running the design at full speed... IRQs to check expected conditions?
    -   Test LZC
"""
