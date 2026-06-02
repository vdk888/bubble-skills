// Decode Ogg/Opus (Telegram voice note) -> 16 kHz mono 16-bit PCM WAV
// Usage: node oga2wav.mjs <input.oga> <output.wav>
import { readFileSync, writeFileSync } from "node:fs";
import { OggOpusDecoder } from "ogg-opus-decoder";

const [inPath, outPath] = process.argv.slice(2);
if (!inPath || !outPath) { console.error("usage: node oga2wav.mjs <in.oga> <out.wav>"); process.exit(1); }

const decoder = new OggOpusDecoder();
await decoder.ready;
const { channelData, samplesDecoded, sampleRate } = await decoder.decodeFile(readFileSync(inPath));
decoder.free();
if (!samplesDecoded) { console.error("no samples decoded"); process.exit(2); }

// Downmix to mono
const ch = channelData.length;
const mono = new Float32Array(samplesDecoded);
for (let i = 0; i < samplesDecoded; i++) {
  let s = 0;
  for (let c = 0; c < ch; c++) s += channelData[c][i];
  mono[i] = s / ch;
}

// Resample sampleRate -> 16000 (linear interpolation; fine for speech)
const target = 16000;
const ratio = sampleRate / target;
const outLen = Math.floor(samplesDecoded / ratio);
const res = new Float32Array(outLen);
for (let i = 0; i < outLen; i++) {
  const pos = i * ratio;
  const i0 = Math.floor(pos);
  const i1 = Math.min(i0 + 1, samplesDecoded - 1);
  const frac = pos - i0;
  res[i] = mono[i0] * (1 - frac) + mono[i1] * frac;
}

// Write 16-bit PCM mono WAV
const dataBytes = outLen * 2;
const buf = Buffer.alloc(44 + dataBytes);
buf.write("RIFF", 0); buf.writeUInt32LE(36 + dataBytes, 4); buf.write("WAVE", 8);
buf.write("fmt ", 12); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20);
buf.writeUInt16LE(1, 22); buf.writeUInt32LE(target, 24);
buf.writeUInt32LE(target * 2, 28); buf.writeUInt16LE(2, 32); buf.writeUInt16LE(16, 34);
buf.write("data", 36); buf.writeUInt32LE(dataBytes, 40);
for (let i = 0; i < outLen; i++) {
  let v = Math.max(-1, Math.min(1, res[i]));
  buf.writeInt16LE((v < 0 ? v * 0x8000 : v * 0x7fff) | 0, 44 + i * 2);
}
writeFileSync(outPath, buf);
console.error(`decoded ${samplesDecoded} samp @${sampleRate}Hz -> ${outLen} samp @${target}Hz (${(outLen/target).toFixed(1)}s) -> ${outPath}`);
