import mido
import argparse
import sys
import threading
import time
from os import system, name
from pynput import keyboard

# Global control flags
is_paused = False
is_stopped = False
pan_value = 0 # Default pan (center)
reverb_value = 0 # Default reverb (middle value)
level_value = 100  # Default volume (full)

# MIDI output port for control changes
outport = None

def clear():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')

def list_ports():
    """Lists available MIDI output ports."""
    ports = mido.get_output_names()
    if not ports:
        print("No MIDI output ports available.")
    else:
        print("Available MIDI outputs:")
        for port in ports:
            print(f"  - {port}")

def play_midi(file_path, port_name):
    """Plays a MIDI file through the selected output port with playback controls."""
    global is_paused, is_stopped, pan_value, reverb_value, level_value, outport

    try:
        global outport
        outport = mido.open_output(port_name)  # Open the output port

        try:
            mid = mido.MidiFile(file_path)
        except FileNotFoundError:
            print(f"Error: MIDI file '{file_path}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading MIDI file: {e}")
            sys.exit(2)

        clear()
        print("\n🎵 Now playing:", file_path)
        print("Controls: [SPACE] Pause/Resume  |  [Q] Quit  |  [P] Pan  |  [R] Reverb  |  [L] Level\n")

        # Send initial control change for pan, reverb, and level
        outport.send(mido.Message('control_change', control=10, value=pan_value))  # Pan
        outport.send(mido.Message('control_change', control=91, value=reverb_value))  # Reverb
        outport.send(mido.Message('control_change', control=7, value=level_value))  # Volume

        # Play MIDI file with control changes
        for msg in mid.play():
            while is_paused:
                time.sleep(0.1)  # Wait while paused
            
            if is_stopped:
                print("\n⏹ Playback stopped.")
                return

            outport.send(msg)  # Send MIDI message

        print("\n✅ Playback finished.")
        quit()
        
    except OSError as e:
        print(f"OS Error: {e}")
        sys.exit(4)
    except ValueError as e:
        print(f"Value Error: {e}")
        sys.exit(5)
    except Exception as e:
        print(f"Unexpected Error: {e}")
        sys.exit(6)

def control_listener():
    """Listens for keyboard inputs to control playback."""
    global is_paused, is_stopped, pan_value, reverb_value, level_value

    def on_press(key):
        global is_paused, is_stopped, pan_value, reverb_value, level_value

        try:
            if key == keyboard.Key.space:
                is_paused = not is_paused
                print("\n⏸ Paused" if is_paused else "\n▶ Resumed")

            elif key.char and key.char.lower() == "q":
                is_stopped = True
                print("\n⏹ Stopping playback...")
                return False  # Stop listener

            elif key.char and key.char.lower() == "p":  # Adjust pan (CC#10)
                pan_value = get_value_from_user("Pan (0-127): p")
                print(f"\n🔄 Pan set to {pan_value}")
                if outport:
                    outport.send(mido.Message('control_change', control=10, value=pan_value))

            elif key.char and key.char.lower() == "r":  # Adjust reverb (CC#91)
                reverb_value = get_value_from_user("Reverb (0-127): r")
                print(f"\n🔄 Reverb set to {reverb_value}")
                if outport:
                    outport.send(mido.Message('control_change', control=91, value=reverb_value))

            elif key.char and key.char.lower() == "l":  # Adjust level (CC#7)
                level_value = get_value_from_user("Level (0-127): l")
                print(f"\n🔄 Level set to {level_value}")
                if outport:
                    outport.send(mido.Message('control_change', control=7, value=level_value))

        except AttributeError:
            pass  # Ignore special keys

    def get_value_from_user(prompt):
        """Prompt the user for a value, ensuring it's within the valid range."""
        while True:
            sys.stdout.write(f"{prompt} ")  # Display prompt inline
            sys.stdout.flush()  # Ensure it's printed immediately
            try:
                value = int(input())  # Wait for user input
                if 0 <= value <= 127:
                    return value
                else:
                    print("Please enter a value between 0 and 127.")
            except ValueError:
                print("Invalid input. Please enter a valid integer.")

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def main():
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

    # Start keyboard control listener in a separate thread
    control_thread = threading.Thread(target=control_listener, daemon=True)
    control_thread.start()

    # Play MIDI file
    play_midi(args.file, args.port)

if __name__ == "__main__":
    main()
