import type {CSSProperties, ReactNode} from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {brand} from './brand';

// Fades and rises into place, `delay` frames after the scene starts.
export const Enter = ({
  delay = 0,
  distance = 40,
  style,
  children,
}: {
  delay?: number;
  distance?: number;
  style?: CSSProperties;
  children: ReactNode;
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - delay, fps, config: {damping: 14, stiffness: 90}});
  const y = interpolate(s, [0, 1], [distance, 0]);
  return <div style={{...style, opacity: s, transform: `translateY(${y}px)`}}>{children}</div>;
};

// Shows `value` with as many decimals as `like` has (74.5 -> one decimal).
export const formatNumber = (value: number, like: number) => {
  const decimals = (String(like).split('.')[1] ?? '').length;
  return value.toLocaleString(brand.locale, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};

export const Backdrop = () => (
  <AbsoluteFill
    style={{
      backgroundColor: brand.background,
      backgroundImage: `radial-gradient(circle at 15% 10%, ${brand.accent}33, transparent 50%), radial-gradient(rgba(255, 255, 255, 0.06) 1.5px, transparent 1.5px)`,
      backgroundSize: '100% 100%, 36px 36px',
    }}
  />
);

export const Watermark = () =>
  brand.name ? (
    <div
      style={{
        position: 'absolute',
        top: 44,
        right: 56,
        padding: '10px 22px',
        borderRadius: 999,
        background: 'rgba(0, 0, 0, 0.35)',
        fontSize: 26,
        fontWeight: 800,
      }}
    >
      {brand.name}
    </div>
  ) : null;

// Burned-in captions: the narration in chunks of 7 words, spread over the
// spoken part of the clip (build_voice.py adds 0.3 s before, 0.5 s after).
export const Subtitles = ({text}: {text: string}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const words = (text ?? '').split(/\s+/).filter(Boolean);
  const start = 0.3 * fps;
  const end = durationInFrames - 0.5 * fps;
  const progress = (frame - start) / Math.max(1, end - start);
  if (words.length === 0 || progress < 0 || progress >= 1) {
    return null;
  }
  const first = Math.floor(Math.floor(progress * words.length) / 7) * 7;
  return (
    <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 64}}>
      <div
        style={{
          maxWidth: 1500,
          padding: '14px 30px',
          borderRadius: 16,
          background: 'rgba(0, 0, 0, 0.62)',
          fontSize: 42,
          fontWeight: 600,
          lineHeight: 1.3,
          textAlign: 'center',
        }}
      >
        {words.slice(first, first + 7).join(' ')}
      </div>
    </AbsoluteFill>
  );
};
