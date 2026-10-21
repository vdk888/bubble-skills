import script from '../script.json';
import timings from '../public/scene_timings.json';

export const FPS = 30;

// Audio drives timing: each scene lasts exactly as long as its voice clip,
// as measured by build_voice.py in public/scene_timings.json.
const seconds = new Map(timings.scenes.map((s) => [s.id, s.duration]));

let elapsed = 0;
export const plan = script.scenes.map((scene: any) => {
  const duration = seconds.get(scene.id);
  if (duration === undefined) {
    throw new Error(`No voice timing for scene "${scene.id}": run build_voice.py again.`);
  }
  const from = Math.round(elapsed * FPS);
  elapsed += duration;
  return {scene, frames: Math.round(elapsed * FPS) - from};
});

export const totalFrames = Math.round(elapsed * FPS);
