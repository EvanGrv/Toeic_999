#!/usr/bin/env python3
"""Build offline WAV speech assets with macOS voices; no API or credentials."""
import concurrent.futures
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import wave

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from server.content import GROUPS

VOICES = {'US': ['Samantha', 'Daniel'], 'UK': ['Daniel', 'Moira'], 'AU': ['Karen', 'Daniel']}
OUT = ROOT / 'public' / 'audio'

def render(group):
    path = OUT / f"{group['id']}.wav"
    if path.exists():
        with wave.open(str(path)) as wav:
            frames = wav.readframes(wav.getnframes())
            if any(frames):
                return group['id'], round(wav.getnframes() / wav.getframerate(), 2)
    voices = VOICES[group.get('accent', 'US')]
    segments = []
    if group['part'] == 1:
        segments.append(('Look at the photograph.', voices[0], 2))
    elif group.get('dialogue'):
        for i, line in enumerate(group['dialogue']):
            segments.append((re.sub(r'^(Nora|Ben|Amira): ', '', line), voices[i % len(voices)], .6))
    else:
        segments.append((group['transcript'], voices[0], 1))
    for item in group['questions']:
        if group['part'] in (3, 4):
            segments.append((item['stem'], voices[0], 2))
        elif group['part'] in (1, 2):
            for i, choice in enumerate(item['choices']):
                segments.append((f'{"ABCD"[i]}. {choice}', voices[0], 1))
    with tempfile.TemporaryDirectory() as tmp:
        frames = []
        for i, (text, voice, pause) in enumerate(segments):
            part = Path(tmp) / f'{i}.wav'
            result = subprocess.run(['say', '-v', voice, '-r', '158', '-o', str(part), '--file-format=WAVE', '--data-format=LEI16@22050', text], capture_output=True)
            if result.returncode:
                raise RuntimeError(f"Unable to synthesize {group['id']} ({voice})")
            with wave.open(str(part)) as wav:
                if wav.getnchannels() != 1 or wav.getsampwidth() != 2 or wav.getframerate() != 22050:
                    raise ValueError('Unexpected audio format')
                speech = wav.readframes(wav.getnframes())
                if not speech or not any(speech):
                    raise RuntimeError('Speech synthesis returned no speech. Run outside the restricted sandbox on macOS.')
                frames.append(speech)
            frames.append(b'\0\0' * int(22050 * pause))
        with wave.open(str(path), 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(22050)
            wav.writeframes(b''.join(frames))
    with wave.open(str(path)) as wav:
        return group['id'], round(wav.getnframes() / wav.getframerate(), 2)

if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    groups = [g for g in GROUPS if g['part'] < 5]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = dict(pool.map(render, groups))
    (OUT / 'manifest.json').write_text(json.dumps(results, indent=2))
    print(f'{len(results)} audio files · {sum(results.values()) / 60:.1f} minutes · {len(set(VOICES))} accent families')
