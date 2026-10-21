import {AbsoluteFill} from 'remotion';
import {brand} from '../brand';
import {Enter} from '../parts';

export const OutroScene = ({scene}: {scene: any}) => (
  <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', textAlign: 'center'}}>
    <Enter distance={60}>
      <div style={{fontSize: 124, fontWeight: 900, letterSpacing: -5}}>{scene.title}</div>
    </Enter>
    {scene.subtitle ? (
      <Enter delay={14}>
        <div style={{marginTop: 24, fontSize: 48, color: brand.muted}}>{scene.subtitle}</div>
      </Enter>
    ) : null}
    {scene.url ? (
      <Enter delay={28}>
        <div style={{marginTop: 52, fontSize: 42, fontWeight: 700, color: brand.accent}}>{scene.url}</div>
      </Enter>
    ) : null}
  </AbsoluteFill>
);
