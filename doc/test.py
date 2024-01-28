from machine import Pin
from ttboard.mode import RPMode
from ttboard.demoboard import DemoBoard

# ========= Config =========
BASIC_TEST = False
FRAME_TEST = False

# Comment out as required, to disable those tests:
BASIC_TEST = True
FRAME_TEST = True


# ========= Helper functions =========

# print_tt_outputs():
# Show the state of the board's 8 uo_outs, and 8 bidir pins (treated also as outputs).
# Optionally also takes what they are *expected* to be, just for visual comparison.
def print_tt_outputs(tt:DemoBoard, expect_out:int=None, expect_bidir:int=None, prefix=''):
    print(f'{prefix} uo_out={tt.output_byte:08b} bidir={tt.bidir_byte:08b}', end='')
    if [expect_out,expect_bidir] != [None,None]:
        print('; expected', end='')
        if expect_out is not None:
            print(f' uo_out={expect_out:08b}', end='')
        if expect_bidir is not None:
            print(f' bidir={expect_bidir:08b}', end='')
    print()

# do_reset():
# Go through a reset sequence by asserting reset, pulsing clock 3 times,
# then releasing reset again:
def do_reset(tt):
    print('Resetting design...')
    tt.resetProject(True)
    for i in range(3):
        tt.clockProjectOnce()
    tt.resetProject(False)


# ========= Main test code =========

# Get a handle to the base board: config.ini selects ASIC_ON_BOARD mode to configure
# our RP2040 GPIOs for proper cooperation with an attached TT chip:
tt = DemoBoard()

# Enable my tt03p5-solo-squash design:
#NOTE: This might not be needed given our config.ini
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

# Reset the design:
do_reset(tt)

# Now show the state of all outputs again.
# Expected outputs are what the design should always assert while held in reset:
print_tt_outputs(tt, expect_out=0b11011110, expect_bidir=0b11111000, prefix='Post-reset state:')

if BASIC_TEST:
    print('BASIC_TEST: Running basic test of first 2 video lines...')
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
                if x&0b1111 == 0:
                    print('.', end='')
            else:
                print_tt_outputs(tt, expect_out, prefix=f'[{x},{y}] Error:')
            tt.clockProjectOnce()
    print('\nBASIC_TEST done\n')


if FRAME_TEST:
    do_reset(tt)

    # ...then we'll test the structure of a frame:
    print('FRAME_TEST: Running a test of the first frame...')
    # I'm lazy, so let's just count the total number of pixels we can predict
    # of each colour...
    color_counts = [0]*8 # 8 possible colours to count, with 3 bits.
    for y in range(525):
        print(f'Line {y}:')
        for x in range(800):
            # Increment the count bin for the current pixel colour:
            color = tt.output_byte & 0b111
            color_counts[color] += 1
            # Make sure vsync is asserted at the right times:
            expected_vsync = 0 if y>=480+10 and y<480+10+2 else 1 # (VSYNC is active low)
            actual_vsync = (tt.output_byte & 0b10000) >> 4
            if actual_vsync != expected_vsync:
                print_tt_outputs(tt, expect_out, prefix=f'[{x},{y}] VSYNC error:')
            tt.clockProjectOnce()

    # Expected results:
    # Green:
    #   + 28*28*20*2 - Top and bottom walls
    #   + 28*28*13 - RHS wall
    #   + 16*16 - Ball
    #   = 41808
    # Red:
    #   + 32*64 - Paddle
    #   = 2048
    # Yellow:
    #   + 640*4 - Top and bottom edges of each of top and bottom walls
    #   + 28*4*20*2 - Top and bottom walls, left and right edges of each block
    #   + (32*32-28*28)*13 - RHS wall block edges
    #   = 10160
    # Blue (varies):
    #   ~ 18.75%+/-1% of ((640-32)*(480-64)-32*64-16*16
    #   = 44485..49498
    # Cyan, Magenta, White: all 0
    color_names = [
        'Black',
        'Blue',
        'Green',
        'Cyan',
        'Red',
        'Magenta',
        'Yellow',
        'White'
    ]
    expected_counts = [
        None,                # Black; Irrelevant if the other counts are (about) right
        range(44485, 49499), # Blue
        41808,               # Green
        0,                   # Cyan
        2048,                # Red
        0,                   # Magenta
        10160,               # Yellow
        0                    # White
    ]

    print('Counted pixel colours:')
    print(f"{'Color':10s}{'Actual':>10s}{'Expected':>10s}")
    for i in range(len(expected_counts)):
        name = color_names[i]
        actual = color_counts[i]
        expected = expected_counts[i]
        if expected is None:
            continue
        print(f'{name:10s}{actual:>10d}', end='')
        if isinstance(expected,range):
            print(expected, end='')
            fail = actual not in expected
        else:
            print(f"{expected:>10d}", end='')
            fail = actual != expected
        if fail:
            print(' - ERROR')
        else:
            print()

    print('\FRAME_TEST done\n')


"""
    TBC!
    TODO:
    -   Try running on upython/RP2040
    -   Can we make mapped pin names to suit actual pin names for our design?
    -   Test running the design at full speed... IRQs to check expected conditions?
    -   Test LZC
"""
