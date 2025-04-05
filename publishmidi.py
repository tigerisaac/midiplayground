import mido
import librosa

def midi_to_note_list(midi_path, target_track_name=None):
    try:
        mid = mido.MidiFile(midi_path)
        notes = []
        tempo = 500000 
        ticks_per_beat = mid.ticks_per_beat if mid.ticks_per_beat else 480

        open_notes = {}
        current_time_ticks = 0

        track_index_to_process = 0
        if target_track_name:
            found = False
            for i, track in enumerate(mid.tracks):
                if track.name.strip().lower() == target_track_name.strip().lower():
                    track_index_to_process = i
                    found = True
                    break
            if not found:
                 pass
        elif len(mid.tracks) > 1:
            pass

        selected_track = mid.tracks[track_index_to_process]

        for msg in selected_track:
            current_time_ticks += msg.time

            if msg.is_meta and msg.type == 'set_tempo':
                tempo = msg.tempo

            elif msg.type == 'note_on' and msg.velocity > 0:
                key = (msg.channel, msg.note)
                open_notes[key] = current_time_ticks

            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                key = (msg.channel, msg.note)
                if key in open_notes:
                    start_tick = open_notes.pop(key)
                    end_tick = current_time_ticks
                    duration_ticks = end_tick - start_tick
                    seconds_per_tick = tempo / (ticks_per_beat * 1_000_000.0)
                    duration_seconds = duration_ticks * seconds_per_tick
                    note_name = librosa.midi_to_note(msg.note)
                    notes.append([note_name, round(duration_seconds, 3)])

        estimated_bpm = round(mido.tempo2bpm(tempo), 2)
        return notes, estimated_bpm

    except FileNotFoundError:
        return None, None
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return None, None

def write_output_file(output_path, note_list, tempo):
    try:
        with open(output_path, 'w') as f:
            if tempo is not None:
                f.write(f"# Estimated Tempo: {tempo:.2f} BPM\n")
            else:
                f.write("# Tempo estimation failed or unavailable\n")
            if note_list:
                 avg_dur = note_list[0][1]
                 f.write(f"# Format: [Note, Average Duration ({avg_dur:.3f}s)],\n")
            else:
                 f.write("# Format: [Note, Average Duration],\n")
            f.write("---\n")
            if not note_list:
                f.write("# No notes detected.\n")
            else:
                num_notes = len(note_list)
                for i, note_item in enumerate(note_list):
                    line = f"{note_item}"
                    if i < num_notes - 1:
                        line += ","
                    f.write(line + "\n")
    except IOError as e:
        pass

if __name__ == "__main__":
    midi_file = input("song name (the song must be in the directory):\n")
    midi_file = midi_file + ".mid"
    track_name = "Lead Guitar"

    note_list, bpm = midi_to_note_list(midi_file, target_track_name=track_name)

    if note_list is not None:
        if bpm:
             print(f"# Estimated Tempo: {bpm:.2f} BPM")

        if not note_list:
            print("No notes found in the processed track.")
        else:
            for i, item in enumerate(note_list[:10]):
                line = f"  {item}"
                if i < len(note_list) - 1 and i < 9:
                    line += ","
                print(line)
            if len(note_list) > 10:
                 print(f"  ... ({len(note_list) - 10} more notes)")
        
        out_path = midi_file.split("/")[1].split(".")[0] + ".txt"
        write_output_file(out_path, note_list, bpm)
    else:
        print("\nMIDI Processing failed.")
