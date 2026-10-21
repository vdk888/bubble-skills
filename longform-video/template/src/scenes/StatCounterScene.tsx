import {AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {brand} from '../brand';
import {Enter, formatNumber} from '../parts';

export const StatCounterScene = ({scene}: {scene: any}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const rampEnd = 10 + Math.round(1.4 * fps);
  const ramp = interpolate(frame, [10, rampEnd], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const pulse = frame > rampEnd ? 1 + 0.012 * Math.sin((frame - rampEnd) / 9) : 1;
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', textAlign: 'center', paddingBottom: 120}}>
      <div style={{fontSize: 280, fontWeight: 900, letterSpacing: -14, color: brand.accent, transform: `scale(${pulse})`}}>
        {formatNumber(scene.value * ramp, scene.value)}
        {scene.suffix ?? ''}
      </div>
      <Enter delay={20}>
        <div style={{fontSize: 54, fontWeight: 800, letterSpacing: -1, lineHeight: 1.15, whiteSpace: 'pre-line'}}>
          {scene.label}
        </div>
      </Enter>
      {scene.source ? (
        <Enter delay={32}>
          <div style={{marginTop: 28, fontSize: 28, color: brand.muted}}>{scene.source}</div>
        </Enter>
      ) : null}
    </AbsoluteFill>
  );
};
