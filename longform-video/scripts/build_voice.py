#!/usr/bin/env python3
"""Build a single voice.wav aligned to scene timings.

Philosophy: audio dictates timing, not the other way around.
- Every clip gets uniform speed (target_speed from script.json, default 1.1x)
- Each scene duration = final_audio_duration + per-scene buffer
- Writes scene_timings.json for Root.tsx to consume
"""
import json, subprocess, os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
script = json.load(open(os.path.join(ROOT, 'script.json')))
scenes = script['scenes']
target_speed = script.get('voice_speed', 1.1)
sr = 48000

def probe_dur(path):
    r = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1', path], capture_output=True, text=True)
    return float(r.stdout.strip())

# Mix A+B strategy:
#   - Natural variability kept inside a comfort band (WPM_LOW .. WPM_HIGH)
#   - Outliers normalized back to the nearest edge of the band (not to a single target)
#   - No global speed applied otherwise
WPM_LOW = 150
WPM_HIGH = 200

clips = []
timings = []  # [{ id, duration_seconds }]
for s in scenes:
    p = os.path.join(ROOT, 'audio', f"{s['id']}.wav")
    if not os.path.exists(p):
        print(f"MISSING {p}"); sys.exit(1)
    d_raw = probe_dur(p)
    words = len(s['narration'].split())
    wpm = words / d_raw * 60 if d_raw > 0 else 160
    # Decide speed factor
    if wpm > WPM_HIGH:
        # Too fast → slow down so wpm = WPM_HIGH
        speed = wpm / WPM_HIGH  # atempo > 1 speeds up; we want it slower → speed < 1
        speed = 1 / speed
    elif wpm < WPM_LOW:
        # Too slow → speed up so wpm = WPM_LOW
        speed = wpm / WPM_LOW  # wpm<WPM_LOW → speed<1 → atempo<1 slow... wait fix:
        # atempo=X: out_dur = in_dur/X. If we want to raise wpm we want shorter dur → atempo>1.
        speed = WPM_LOW / wpm
    else:
        speed = 1.0
    # Clamp speed to safety band
    speed = max(0.85, min(1.35, speed))
    d_after_speed = d_raw / speed
    lead_buffer = 0.3
    trail_buffer = 0.5
    scene_duration = lead_buffer + d_after_speed + trail_buffer
    out = os.path.join(ROOT, 'audio', f"_proc_{s['id']}.wav")
    # atempo only supports 0.5..2.0; we're already safe
    filter_chain = f"atempo={speed:.4f},adelay={int(lead_buffer*1000)}|{int(lead_buffer*1000)},apad=pad_dur={trail_buffer:.3f}"
    cmd = ['ffmpeg','-y','-i',p,'-af',filter_chain,'-t',f"{scene_duration:.3f}",'-ar',str(sr),'-ac','2',out]
    subprocess.run(cmd, capture_output=True, check=True)
    actual = probe_dur(out)
    final_wpm = words / d_after_speed * 60 if d_after_speed > 0 else 0
    clips.append(out)
    timings.append({'id': s['id'], 'duration': actual})
    flag = ' (normalized)' if speed != 1.0 else ''
    print(f"{s['id']:20s} raw_wpm={wpm:3.0f} speed={speed:.2f} final_wpm={final_wpm:3.0f} scene={actual:.2f}s{flag}")

# Concat
listfile = os.path.join(ROOT, 'audio', '_list.txt')
with open(listfile,'w') as f:
    for c in clips:
        f.write(f"file '{c}'\n")
out_wav = os.path.join(ROOT, 'public', 'voice.wav')
subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',listfile,'-c','copy',out_wav], check=True, capture_output=True)
total = probe_dur(out_wav)

# Write scene timings for Remotion
timings_path = os.path.join(ROOT, 'public', 'scene_timings.json')
with open(timings_path, 'w') as f:
    json.dump({'fps': 30, 'speed': target_speed, 'scenes': timings, 'total_seconds': total}, f, indent=2)

print(f"\nWrote {out_wav} ({total:.2f}s)")
print(f"Wrote {timings_path}")
