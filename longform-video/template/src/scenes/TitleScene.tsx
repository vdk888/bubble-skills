import {AbsoluteFill} from 'remotion';
import {brand} from '../brand';
import {Enter} from '../parts';

export const TitleScene = ({scene}: {scene: any}) => (
  <AbsoluteFill style={{justifyContent: 'center', padding: '0 160px'}}>
    <Enter distance={60}>
      <div style={{fontSize: 124, fontWeight: 900, letterSpacing: -5, lineHeight: 1.02, whiteSpace: 'pre-line'}}>
        {scene.title}
      </div>
    </Enter>
    {scene.subtitle ? (
      <Enter delay={14}>
        <div style={{marginTop: 44, fontSize: 46, color: brand.muted}}>{scene.subtitle}</div>
      </Enter>
    ) : null}
  </AbsoluteFill>
);
