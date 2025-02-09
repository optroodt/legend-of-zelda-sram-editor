# legend-of-zelda-sram-editor
While replaying The Legend Of Zelda on my [AVS](https://www.retrousb.com/product/avs/21?cp=true&sa=false&sbp=false&q=false&category_id=YXD2RSSKMUXTF4VBCVSGLDNN) and messing up the save state multiple times, I wondered if there was any software out there that lets you modify the save state.

I found [lozsrame](https://github.com/jdratlif/lozsrame), but it's written in C++, the binaries won't run on modern MacOS versions and you need to install a bunch of outdated dependencies in order to compile it yourself. After some hesitation I decided to bite the bullet and rewrite this to Python with no dependencies, foregoing the UI. 


## TODO's
The following things need to be addressed:
* The class operates on the first save game. It's currently hardcoded so it's not possible to change the other save games (except for the name).
* Type hints are probably missing in some cases.
* Valid save states must exist, you cannot create a valid `.sav` file out of thin air.
* I don't know what the `give` parameter is for.
* Things should be refactored, there is quite some duplication.

## How to use
This program requires Python 3.

You can either import this class into your own project. In that case you'll probably know how to use it.

If you're just interested in quickly generating a save file with certain options, modify the code at the end of the `sram.py` file. A valid, empty `empty.sav` file is provided. Once you've set the options you want, run:
```
python sram.py
```
and there will be a new file called `Legend of Zelda, The (U) (PRG 1).sav`. This file should be usable by your emulator or in my case the RetroUSB PowerPak.

Enjoy!

## Acknowledgement
This code is a translation to Python of [lozsrame](https://github.com/jdratlif/lozsrame).
