# NukedSCPlayer
NukedSCPlayer is an interface for [Nukeykt's](https://github.com/nukeykt) [Nuked-SC55](https://github.com/nukeykt/Nuked-SC55) MIDI emulator that allows users to play midi files through the commandline.

![image](https://github.com/user-attachments/assets/ea1584b7-88d6-4e3e-8e4d-5eb26b0c05eb)

## Requirements
NukedSCPlayer uses multiple python packages to work:

```
pip install mido
pip install pynput
pip install rtmidi
```
## How to use
To use NukedSCPlayer, type:
```
python3 scmid.py --file /path/to/file --port "PORT"
```
With `"PORT"` being Nuked-SC55's midi port (To find the port, type: `python3 scmid.py --list`.)

Example:
```
python3 scmid.py --file /home/pcbcat/Documents/SCMID/BETWEE.MID --port "Nuked SC55:Nuked SC55 128:0"
```

## Future Plans
- Make a GUI (GUI is already made, I just need to add the functions to it.)
![image](https://github.com/user-attachments/assets/97bc5e84-e25a-4d56-a93c-d91f335cd61c)

- Improve CLI
- Add more functions
- Figure out how to compile
- Add updater
