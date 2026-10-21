import {AbsoluteFill, useVideoConfig} from 'remotion';
import {brand} from '../brand';
import {Enter} from '../parts';

// One line at a time, spread over the scene; the last line in the accent colour.
export const KineticQuoteScene = ({scene}: {scene: any}) => {
  const {durationInFrames} = useVideoConfig();
  const lines: string[] = scene.lines ?? [];
  const step = Math.max(8, Math.floor((durationInFrames - 30) / Math.max(1, lines.length)));
  return (
    <AbsoluteFill style={{justifyContent: 'center', padding: '0 180px'}}>
      {lines.map((line, i) => (
        <Enter key={i} delay={6 + i * step} distance={70}>
          <div
            style={{
              fontSize: 96,
              fontWeight: 900,
              letterSpacing: -4,
              lineHeight: 1.1,
              color: i === lines.length - 1 ? brand.accent : brand.text,
            }}
          >
            {line}
          </div>
        </Enter>
      ))}
    </AbsoluteFill>
  );
};
