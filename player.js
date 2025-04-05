const A4_FREQUENCY = 440.0;
const A4_MIDI_NOTE = 69;
const NOTE_OFFSETS: { [key: string]: number } = {
    'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11
};

const songData = [
    ['B5', 0.2]
];

let isPlaying = false;

function getFrequencyFromName(noteName: string): number {
    if (!noteName || noteName.length < 2) {
        return 0;
    }

    let noteLetter = noteName.charAt(0);
    let accidentalOffset = 0;
    let octaveIndex = 1;

    if (noteName.length > 1) {
        let accidental = noteName.charAt(1);
        if (accidental === '#' || accidental === '♯') {
            accidentalOffset = 1;
            octaveIndex = 2;
        } else if (accidental === 'b' || accidental === '♭') {
            accidentalOffset = -1;
            octaveIndex = 2;
        }
    }

    let baseOffset = NOTE_OFFSETS[noteLetter];
    if (baseOffset === undefined) {
        return 0;
    }

    let octaveStr = noteName.slice(octaveIndex);
    let octave = parseInt(octaveStr);

    let midiNote = 12 * (octave + 1) + baseOffset + accidentalOffset;
    let semitonesFromA4 = midiNote - A4_MIDI_NOTE;
    let frequency = A4_FREQUENCY * Math.pow(2, semitonesFromA4 / 12.0);

    return frequency;
}

function playSongSequence() {
    if (isPlaying) {
        return;
    }
    isPlaying = true;
    light.showAnimation(light.theaterChaseAnimation, 500)

    for (let noteData of songData) {
        let noteName = noteData[0] as string;
        let durationSeconds = noteData[1] as number;
        let frequency = getFrequencyFromName(noteName);
        let durationMs = durationSeconds * 1000;

        if (frequency > 0 && durationMs > 0) {
            music.playTone(frequency, durationMs);
        } else if (durationMs > 0) {
            music.rest(durationMs);
        }
    }

    light.clear();
    isPlaying = false;
}

playSongSequence();

light.setAll(light.rgb(20, 20, 20));
