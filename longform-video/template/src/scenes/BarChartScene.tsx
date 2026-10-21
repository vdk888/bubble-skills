import {AbsoluteFill, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {brand} from '../brand';
import {Enter, formatNumber} from '../parts';

export const BarChartScene = ({scene}: {scene: any}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const rows: {label: string; value: number}[] = scene.data ?? [];
  const max = Math.max(...rows.map((r) => r.value), 1);
  return (
    <AbsoluteFill style={{justifyContent: 'center', padding: '0 160px 140px'}}>
      <Enter>
        <div style={{marginBottom: 56, fontSize: 66, fontWeight: 800, letterSpacing: -2}}>{scene.title}</div>
      </Enter>
      {rows.map((row, i) => {
        const grow = spring({frame: frame - 14 - i * 7, fps, config: {damping: 18, stiffness: 80}});
        return (
          <div key={row.label} style={{display: 'flex', alignItems: 'center', marginBottom: 26, fontSize: 38}}>
            <div style={{width: 420, paddingRight: 24, color: brand.muted}}>{row.label}</div>
            <div style={{flex: 1, height: 58, borderRadius: 10, background: brand.card}}>
              <div
                style={{
                  width: `${(row.value / max) * 100 * grow}%`,
                  height: '100%',
                  borderRadius: 10,
                  background: brand.accent,
                }}
              />
            </div>
            <div style={{width: 220, textAlign: 'right', fontWeight: 800}}>
              {formatNumber(row.value * grow, row.value)}
              {scene.suffix ?? ''}
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
