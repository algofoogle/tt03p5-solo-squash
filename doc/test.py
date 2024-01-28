from machine import Pin
from ttboard.mode import RPMode
from ttboard.demoboard import DemoBoard

# Used to show the state of the board's 8 uo_outs, and 8 bidir pins (treated also as outputs).
# Optionally also takes what they are *expected* to be, just for visual comparison.
def print_tt_outputs(b:DemoBoard, expect_out:int=None, expect_bidir:int=None, prefix=''):
    print(f'{prefix} uo_out={b.output_byte:08b} bidir={b.bidir_byte:08b}', end='')
    if [expect_out,expect_bidir] != [None,None]:
        print('; expected', end='')
        if expect_out is not None:
            print(f' uo_out={expect_out:08b}', end='')
        if expect_bidir is not None:
            print(f' bidir={expect_bidir:08b}', end='')
    print()

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

# By default all inputs to the ASIC should be low:
tt.input_byte = 0

# Print initial state of all outputs; likely to be somewhat random:
print_tt_outputs(tt, prefix='Pre-reset state:')

# Assert reset, pulse the clock 3 times, then release reset:
tt.resetProject(True)
for i in range(3):
    tt.clockProjectOnce()
tt.resetProject(False)

# Now show the state of all outputs again.
# Expected outputs are what the design should always assert while held in reset:
print_tt_outputs(tt, expect_out=0b11011110, expect_bidir=0b11111000, prefix='Post-reset state:')

# Now, the design should render immediately from the first line of the visible
# display area, and the first two lines that it renders should be fully yellow...
#NOTE: RGB outs are registered (hence 'next_color' and 'color')
# but the rest are not (i.e. hsync, vsync, speaker, col0, row0).
next_color = 0b110 # Yellow
for y in range(2):
    print(f'Line {y}:')
    for x in range(800):
        # Make sure outputs match what we expect...
        color = next_color
        next_color = 0b110 if x<640 else 0 # Yellow
        hsync = 0 if x>=640+16 and x<640+16+96 else 1 # (HSYNC is active low)
        vsync = 0 if y>=480+10 and y<480+10+2 else 1 # (VSYNC is active low)
        speaker = 0 # Off
        col0 = 1 if x==0 else 0
        row0 = 1 if y==0 else 0
        expect_out = (row0<<7) | (col0<<6) | (speaker<<5) | (vsync<<4) | (hsync<<3) | color
        if tt.output_byte == expect_out:
            print('.', end='')
        else:
            print_tt_outputs(tt, expect_out, prefix=f'[{x},{y}] Error:')
        tt.clockProjectOnce()


"""
    TBC!
    TODO:
    -   Try running on upython/RP2040
    -   Change assertions to soft tests
    -   Can we make mapped pin names to suit actual pin names for our design?
    -   Test direct clocking and expected outputs
    -   Test running the design at full speed... IRQs to check expected conditions?
    -   Test LZC
"""
