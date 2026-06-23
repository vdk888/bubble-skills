#!/usr/bin/env python3
"""Generate all narration WAVs in one process (model loaded once).
Applies voice_style prefix from script.json (Voice Design) for emotional steering.
"""
import sys, time, json, os
from pathlib import Path

ROOT = Path(__file__).parent
script = json.loads((ROOT / 'script.json').read_text())
ref_path = str((ROOT / 'audio' / '_ref.wav').resolve())
voice_style = script.get('voice_style', '')

todo = []
for s in script['scenes']:
    out = ROOT / 'audio' / f"{s['id']}.wav"
    if out.exists() and out.stat().st_size > 10000:
        print(f"SKIP {s['id']} (exists)")
        continue
    text = s['narration']
    # Layer voice-design style with cloning per VoxCPM SKILL doc
    if voice_style:
        text = f"{voice_style}{text}"
    todo.append((s['id'], text, str(out.resolve())))

if not todo:
    print("All done.")
    sys.exit(0)

print(f"[batch] loading model... ({len(todo)} clips to generate)", flush=True)
import soundfile as sf
from voxcpm import VoxCPM
t0 = time.time()
model = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False)
print(f"[batch] model loaded in {time.time()-t0:.1f}s", flush=True)
sr = model.tts_model.sample_rate

for sid, text, out in todo:
    t = time.time()
    # Higher cfg + more steps for stronger style adherence
    wav = model.generate(text=text, reference_wav_path=ref_path, cfg_value=2.5, inference_timesteps=12)
    sf.write(out, wav, sr)
    print(f"[batch] {sid}: {len(wav)/sr:.2f}s in {time.time()-t:.1f}s", flush=True)

print("DONE")
