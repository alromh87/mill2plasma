[dxf2gcode](https://sourceforge.net/projects/dxf2gcode/) PostProcessor for plasma cutter.

Compatible with [GRBL](https://github.com/grbl/grbl)

## Usage:

1. Run your dxf design through dxf2gcode, using just one pass for z <= 0
2. Run `python mill2plasma.py <file_name>.ngc -c <cut_height> -p <pierce_height> -d <pierce_delay>`, change items between <> with needed values for your material, `<pierce_height>` should be between 150% and 200% times `<cut_height>`
  * A new file named `<file_name>_plasma.ngc` will be created
3. Prepare your CNC by referencing Z0 close above workpiece
4. Run modified G-code, before each cut:
  * Torch will be referenced
  * The pearcing will take place for specified seconds at set height
  * Cut will begin

## Principle of operation:

For plasma cutting it is important to have control of the distance between torch and workpiece, in order to accomplish this we can start by measuring material exact distance to torch using a probe sensor.

The postprocesor assumes there is a touch sensor connected to the Probe pin, it's also assumed that the plasma torch is activated through the Spindle Enable signal.

[More in detail background](http://technocratplasma.com/blog/torch-height-control-through-arc-voltage-sensing/) including a more advanced method of constant height control, by sensing the torch voltage.




