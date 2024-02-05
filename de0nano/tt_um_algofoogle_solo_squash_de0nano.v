// This wraps the Verilog code that targets TT03p5, so that its interface is through
// the external hardware that I've plugged into a DE0-Nano FPGA dev board.

/*
My implementation has a simple resistor-based RGB333 VGA DAC, but this design only
drives RGB111, so we repeat each MSB for the other colour channel bits. The DAC
is plugged into the low-numbered GPIO-1 header pins.

These are all the connections that I have on my GPIO-1 header right now, though not
all of them are specifically for this project (as noted)...

                        +-----+-----+                                 \
  (ROM pin 6) SCLK    40|io33 |io32 |39    (NC)                        |
                        +-----+-----+                                  |
              (NC)    38|io31 |io30 |37    io3 (ROM pin 7)             |
                        +-----+-----+                                  |
  (ROM pin 3)  io2    36|io29 |io28 |35    io0 (ROM pin 5) (MOSI)      |   RESERVED:
                        +-----+-----+                                   >  NOT USED BY THIS DESIGN
              (NC)    34|io27 |io26 |33    io1 (ROM pin 2) (MISO)      |   (SPI ROM module)
                        +-----+-----+                                  |
  (ROM pin 1)  /CS    32|io25 |io24 |31    (NC)                        |
                        +-----+-----+                                  |
  (ROM pin 4)  GND    30| GND |VCC3 |29    VCC3P3 (+3V3) (ROM pin 8)   |
                        +-----+-----+                                 /
              col0 O  28|io23 |io22 |27 O  row0 ---------------------------------------------------
                        +-----+-----+                                 \
             pause I  26|io21 |io20 |25 O  speaker                     |
                        +-----+-----+                                  |
          new_game I  24|io19 |io18 |23 O  lzc[4]                       >  Some buttons and speaker.
                        +-----+-----+                                  |   NOTE: down/up buttons
           lzc_all O  22|io17 |io16 |21 O  lzc[3]                      |   are in the block below.
                        +-----+-----+                                 /
              (NC)    20|io15 |io14 |19    (NC) ---------------------------------------------------
                        +-----+-----+                                 \
                G0 O  18|io13 |io12 |17 O  B0                          |
                        +-----+-----+                                  |
                G1 O  16|io11 |io10 |15 O  B1                          |
                        +-----+-----+                                  |
                G2 O  14| io9 | io8 |13 O  B2                          |
                        +-----+-----+                                  |
               GND -  12| GND |VCCS |11 +  VCC_SYS (+5V)               |
                        +-----+-----+                                  |
             HSYNC O  10| io7 | io6 |9  O  lzc[2]                       >  VGA RGB333 DAC module
                        +-----+-----+                                  |   with 3 of the spare
             VSYNC O   8| io5 | io4 |7  O  lzc[1]                      |   pass-thru IOs presenting
                        +-----+-----+                                  |   lzc[2:0] bits.
                R0 O   6| io3 | io2 |5  O  lzc[0]                      |   Also, down/up button inputs
                        +-----+-----+                                  |   are on IN0/1 respectively.
                R1 O   4| io1 | IN1 |3  I  up                          |
                        +-----+-----+                                  |
                R2 O   2| io0 | IN0 |1  I  down                        |
                        +-----+-----+     * PIN 1 of GPIO1 header.    /

NOTE: (Pass) pins are populated in the header as long pass-through pins so they can be used for other purposes.

The 4 buttons are active-high. They are pulled low by 22k resistors when open,
and pulled high by 100R when pressed. The buttons are labeled K1..K4 and are assigned as follows:
- K1 = down       => io17
- K2 = new_game   => io19
- K3 = pause      => io21
- K4 = up         => io20

The system clock is provided by the DE0-Nano's CLOCK_50 (50MHz) and is divided by 2 to make the typical
25MHz VGA clock.

The DE0-Nano's KEY[0] provides the reset signal.
*/

`default_nettype none
`timescale 1ns / 1ps


// Wrapper for the Tiny Tapeout 03p5 implementation of solo_squash, targeting DE0-Nano board:
module tt_um_algofoogle_solo_squash_de0nano(
  input           CLOCK_50, // Onboard 50MHz clock
  output  [7:0]   LED,      // 8 onboard LEDs
  input   [1:0]   KEY,      // 2 onboard pushbuttons
  input   [3:0]   SW,       // 4 onboard DIP switches
  inout   [33:0]  gpio1,    // GPIO1
  input   [1:0]   gpio1_IN  // GPIO1 input-only pins
);

  // K4..K1 external buttons board (K4 is top, K1 is bottom):
  wire [4:1] K = {gpio1_IN[1], gpio1[21], gpio1[19], gpio1_IN[0]};

  wire b;
  wire g;
  wire r;
  wire hsync;
  wire vsync;
  wire speaker;
  wire col0;
  wire row0;

  // Various button inputs:
  wire rst_n      = KEY[0]; // Active LOW pushbuttons..
  //wire extra_sel  = KEY[1]; //
  wire down_key   = K[1];   // Active HIGH pushbuttons....
  wire new_game   = K[2];   // 
  wire pause      = K[3];   // 
  wire up_key     = K[4];   // 
  //HACK: extra_sel is hard-wired to make uio_out[6] the 'visible' signal:
  wire extra_sel = 1'b1;

  //NOTE: These lines assert only the GPIO-1 pin that WOULD be the
  // SPI ROM /CS line to DISABLE it, and it leaves the others floating...
  // These lines are not required at all if there's nothing plugged
  // into those pins.
  assign gpio1[33:26] = 8'bzzzz_zzzz;
  assign gpio1[25]  = 1'b1; // Disable SPI ROM.

  // VGA outputs:
  assign gpio1[0]   = r;    // Red2.
  assign gpio1[1]   = r;    // Red1.
  assign gpio1[3]   = speaker & visible;  // Visualise speaker on Red0.

  assign gpio1[9]   = g;    // Green2.
  assign gpio1[11]  = g;    // Green1.
  assign gpio1[13]  = speaker & visible;  // Visualise speaker on Green0.

  assign gpio1[8]   = b;    // Blue2.
  assign gpio1[10]  = b;    // Blue1.
  assign gpio1[12]  = speaker & visible;  // Visualise speaker on Blue0.

  assign gpio1[7]   = hsync;
  assign gpio1[5]   = vsync;

  // Speaker output:
  assign gpio1[20]  = speaker;  // Speaker output.
  // assign LED[7]     = speaker;  // Also visualise speaker on LED7.

  // Other debug outputs:
  wire visible;
  wire unreg_blue;
  wire lzc_all;
  wire [4:0] lzc;
  assign gpio1[17]  = lzc_all;
  assign gpio1[18]  = lzc[4];
  assign gpio1[16]  = lzc[3];
  assign gpio1[6]   = lzc[2];
  assign gpio1[4]   = lzc[1];
  assign gpio1[2]   = lzc[0];
  assign gpio1[23]  = col0;
  assign gpio1[22]  = row0;

  //SMELL: This is a bad way to do clock dividing.
  // We could instead use the built-in FPGA clock divider.
  reg clock_25; // VGA pixel clock of 25MHz is good enough. 25.175MHz is ideal (640x480x59.94)
  always @(posedge CLOCK_50) clock_25 <= ~clock_25;

  tt_um_algofoogle_solo_squash dut(
    // --- TT 'system' inputs: ---
    .ena        (1'b1),
    .clk        (clock_25),
    .rst_n      (rst_n),

    // --- TT dedicated user inputs ---
    .ui_in({
      3'b000,     // ui_in[7:5] are unused by this design.
      extra_sel,  // ui_in[4]
      up_key,     // ui_in[3]
      down_key,   // ui_in[2]
      new_game,   // ui_in[1]
      pause       // ui_in[0]
    }),

    // --- TT dedicated user outputs ---
    .uo_out({
      row0,       // uo_out[7]
      col0,       // uo_out[6]
      speaker,    // uo_out[5]
      vsync,      // uo_out[4]
      hsync,      // uo_out[3]
      r,          // uo_out[2]
      g,          // uo_out[1]
      b           // uo_out[0]
    }),

    // --- TT bidirectional user IOs ---
    // Output path:
    .uio_out({
      unreg_blue, // uio_out[7]
      visible,    // uio_out[6]
      lzc_all,    // uio_out[5]
      lzc         // uio_out[4:0]
    }),
    // Input path is unused; just make it all low for now:
    .uio_in(8'b0000_0000),
    // IO direciton control:
    // Visualise uio_oe from the design, using the LEDs.
    //NOTE: DE0-Nano's LEDs are active HIGH.
    .uio_oe(LED)

  );


endmodule
