# Import libaries
import mido
import argparse
import sys
import threading
import time
import os
from pynput import keyboard

# Global control flags
is_paused = False
is_stopped = False
pan_value = 0 # Default pan (center)
reverb_value = 0 # Default reverb (middle value)
level_value = 100  # Default volume (full)
file_name = None

# MIDI output port for control changes
outport = None

"""
W.I.P code for x11 and NT windowing systems

if os.name == "posix":  # Linux/macOS (only works for X11)
    try:
        from Xlib import display

        def is_terminal_focused():
            try:
                d = display.Display()
                w = d.get_input_focus().focus
                wm_class = w.get_wm_class()
                
                if wm_class:
                    terminal_classes = ["gnome-terminal", "x-terminal-emulator", "konsole", "xfce4-terminal", "lxterminal", "alacritty", "tilix"]
                    return any(term in wm_class for term in terminal_classes)
            except Exception:
                return False
            return False

    except ImportError:
        def is_terminal_focused():
            return True  # Assume always focused if Xlib is missing

elif os.name == "nt":  # Windows
    try:
        import pygetwindow as gw

        def is_terminal_focused():
            try:
                active_window = gw.getActiveWindow()
                if active_window:
                    return any(term in active_window.title.lower() for term in ["cmd", "powershell", "terminal", "command prompt"])
            except Exception:
                return False
            return False

    except ImportError:
        def is_terminal_focused():
            return True  # Assume always focused if pygetwindow is missing

else:
    def is_terminal_focused():
        return True  # Default for unsupported OS
"""

def clear():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

def list_ports():
    # Lists available MIDI output ports.
    ports = mido.get_output_names()
    if not ports:
        print("No MIDI output ports available.")
    else:
        print("Available MIDI outputs:")
        for port in ports:
            print(f"  - {port}")


def play_midi(file_path, port_name):
    # Plays a MIDI file through the selected output port with playback controls.
    global is_paused, is_stopped, pan_value, reverb_value, level_value, outport

    try:
        global outport
        outport = mido.open_output(port_name)  # Open the output port
        time.sleep(1.0)
        try:
            mid = mido.MidiFile(file_path)
        except FileNotFoundError:
            print(f"Error: MIDI file '{file_path}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading MIDI file: {e}")
            sys.exit(2)

        clear()
        print("\n🎵 Now playing:", file_name)
        print("Controls: [SPACE] Pause/Resume  |  [Q] Quit  |  [P] Pan  |  [R] Reverb  |  [L] Level\n")

        # Send initial control change for pan, reverb, and level
        outport.send(mido.Message('control_change', control=10, value=pan_value))  # Pan
        outport.send(mido.Message('control_change', control=91, value=reverb_value))  # Reverb
        outport.send(mido.Message('control_change', control=100, value=level_value))  # Volume

        # Play MIDI file with control changes
        for msg in mid.play():
            while is_paused:
                time.sleep(1.0)  # Wait while paused
            
            if is_stopped:
                clear()
                print("\n⏹ Playback stopped.\n")
                return

            outport.send(msg)  # Send MIDI message
        clear()
        print("\n✅ Playback finished.\n")
        sys.exit(0)
        
    except OSError as e:
        print(f"OS Error: {e}")
        sys.exit(4)
    except ValueError as e:
        print(f"Value Error: {e}")
        sys.exit(5)
    except Exception as e:
        print(f"Unexpected Error: {e}")
        sys.exit(6)

def stop_all_sounds():
    if outport:
        for channel in range(16):
            outport.send(mido.Message('control_change', channel=channel, control=120, value=0))  # All Sound Off
            outport.send(mido.Message('control_change', channel=channel, control=123, value=0))  # All Notes Off


def control_listener():
    # Listens for keyboard inputs to control playback.
    global is_paused, is_stopped, pan_value, reverb_value, level_value

    def on_press(key):
        global is_paused, is_stopped, pan_value, reverb_value, level_value

        #if not is_terminal_focused():
        #    return  # Ignore input if terminal is not focused
        
        try:
            if key == keyboard.Key.space:
                is_paused = not is_paused
                clear()
                print(f"\n🎵 Now playing:", file_name, "\nControls: [SPACE] Pause/Resume  |  [Q] Quit  |  [P] Pan  |  [R] Reverb  |  [L] Level\n", "\n⏸ Paused" if is_paused else "\n▶ Resumed")
                if is_paused: 
                    stop_all_sounds()
                else: print()
                
            elif key.char and key.char.lower() == "q":
                is_stopped = True
                print("\n⏹ Stopping...")
                stop_all_sounds()
                return False  # Stop listener
                quit()

            elif key.char and key.char.lower() == "p":  # Adjust pan (CC#10)
                clear()
                print("\n🎵 Now playing:", file_name)
                print("Controls: [SPACE] Pause/Resume  |  [Q] Quit  |  [P] Pan  |  [R] Reverb  |  [L] Level\n")
                pan_value = get_value_from_user("Pan (0-127): \b")
                clear()
                print("\n🎵 Now playing:", file_name)
                print("Controls: [SPACE] Pause/Resume  |  [Q] Quit  |  [P] Pan  |  [R] Reverb  |  [L] Level\n")
                print(f"🔄 Pan set to {pan_value}")
                if outport:
                    outport.send(mido.Message('control_change', control=10, value=pan_value))

            elif key.char and key.char.lower() == "r":  # Adjust reverb (CC#91)
                clear()
                print("\n🎵 Now playing:", file_name)
                print("Controls: [SPACE] Pause/Resume  |  [Q] Quit  |  [P] Pan  |  [R] Reverb  |  [L] Level\n")
                reverb_value = get_value_from_user("Reverb (0-127): \b")
                clear()
                print("\n🎵 Now playing:", file_name)
                print("Controls: [SPACE] Pause/Resume  |  [Q] Quit  |  [P] Pan  |  [R] Reverb  |  [L] Level\n")
                print(f"🔄 Reverb set to {reverb_value}")
                if outport:
                    outport.send(mido.Message('control_change', control=91, value=reverb_value))

            elif key.char and key.char.lower() == "l":  # Adjust level (CC#7)
                clear()
                print("\n🎵 Now playing:", file_name)
                print("Controls: [SPACE] Pause/Resume  |  [Q] Quit  |  [P] Pan  |  [R] Reverb  |  [L] Level\n")
                level_value = get_value_from_user("Level (0-127): \b")
                clear()
                print("\n🎵 Now playing:", file_name)
                print("Controls: [SPACE] Pause/Resume  |  [Q] Quit  |  [P] Pan  |  [R] Reverb  |  [L] Level\n")
                print(f"🔄 Level set to {level_value}")
                if outport:
                    outport.send(mido.Message('control_change', control=7, value=level_value))

        except AttributeError:
            pass  # Ignore special keys

    def get_value_from_user(prompt):
        # Prompt the user for a value, ensuring it's within the valid range.
        while True:
            try:
                value = int(input(prompt + " "))  # Print prompt and get input
                if 0 <= value <= 127:
                    return value
                else:
                    print("Please enter a value between 0 and 127.")
            except ValueError:
                print("Invalid input. Please enter a valid integer.")

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def main():
    global file_name
    parser = argparse.ArgumentParser(description="SCMID - A MIDI player for Nuked-SC55 with playback controls")
    
    parser.add_argument("--list", action="store_true", help="List available MIDI output ports")
    parser.add_argument("--port", type=str, help="Specify the MIDI output port")
    parser.add_argument("--file", type=str, help="Specify the MIDI file to play")

    args = parser.parse_args()

    if args.list:
        list_ports()
        sys.exit(0)

    if not args.port or not args.file:
        print("Error: Both --port and --file are required.")
        parser.print_help()
        sys.exit(1)

    file_name = args.file
    
    # Start keyboard control listener in a separate thread
    control_thread = threading.Thread(target=control_listener, daemon=True)
    control_thread.start()

    # Play MIDI file
    play_midi(args.file, args.port)

if __name__ == "__main__":
    main()
