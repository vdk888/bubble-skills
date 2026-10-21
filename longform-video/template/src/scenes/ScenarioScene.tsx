import {AbsoluteFill} from 'remotion';
import {brand} from '../brand';
import {Enter} from '../parts';

const Card = ({side, delay, color}: {side: any; delay: number; color: string}) => (
  <Enter delay={delay} style={{flex: 1}}>
    <div style={{padding: '44px 52px', borderRadius: 24, background: brand.card}}>
      <div style={{fontSize: 30, letterSpacing: 2, textTransform: 'uppercase', color: brand.muted}}>{side?.label}</div>
      <div style={{margin: '10px 0 14px', fontSize: 86, fontWeight: 900, letterSpacing: -3, color}}>{side?.value}</div>
      <div style={{fontSize: 34, color: brand.muted}}>{side?.detail}</div>
    </div>
  </Enter>
);

export const ScenarioScene = ({scene}: {scene: any}) => (
  <AbsoluteFill style={{justifyContent: 'center', padding: '0 140px 140px'}}>
    <Enter>
      <div style={{marginBottom: 50, fontSize: 62, fontWeight: 800, letterSpacing: -2}}>{scene.title}</div>
    </Enter>
    <div style={{display: 'flex', alignItems: 'center', gap: 40}}>
      <Card side={scene.before} delay={10} color={brand.text} />
      <Enter delay={24}>
        <div style={{fontSize: 90, color: brand.accent}}>→</div>
      </Enter>
      <Card side={scene.after} delay={32} color={brand.accent} />
    </div>
    {scene.punch ? (
      <Enter delay={56}>
        <div style={{marginTop: 50, fontSize: 48, fontStyle: 'italic'}}>{scene.punch}</div>
      </Enter>
    ) : null}
  </AbsoluteFill>
);
