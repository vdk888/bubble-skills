import {AbsoluteFill} from 'remotion';
import {brand} from '../brand';
import {Enter} from '../parts';

const Column = ({side, delay, color}: {side: any; delay: number; color: string}) => (
  <Enter delay={delay} style={{flex: 1}}>
    <div style={{padding: '48px 56px', borderRadius: 24, background: brand.card}}>
      <div style={{marginBottom: 30, fontSize: 60, fontWeight: 900, letterSpacing: -2, color}}>{side?.label}</div>
      {(side?.items ?? []).map((item: string, i: number) => (
        <Enter key={item} delay={delay + 12 + i * 8}>
          <div style={{marginBottom: 18, fontSize: 42}}>{item}</div>
        </Enter>
      ))}
    </div>
  </Enter>
);

export const ComparisonScene = ({scene}: {scene: any}) => (
  <AbsoluteFill style={{flexDirection: 'row', alignItems: 'center', gap: 56, padding: '0 140px 140px'}}>
    <Column side={scene.left} delay={0} color={brand.muted} />
    <Column side={scene.right} delay={14} color={brand.accent} />
  </AbsoluteFill>
);
