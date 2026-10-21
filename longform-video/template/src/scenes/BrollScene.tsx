import {AbsoluteFill, OffthreadVideo, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {brand} from '../brand';
import {Enter} from '../parts';

// Full-bleed b-roll from public/broll/<scene id>.mp4, slow Ken Burns zoom,
// and the scene's subtitle as a chapter banner.
export const BrollScene = ({scene}: {scene: any}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const zoom = 1.02 + (frame / durationInFrames) * 0.04;
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{transform: `scale(${zoom})`}}>
        <OffthreadVideo
          src={staticFile(`broll/${scene.id}.mp4`)}
          muted
          style={{width: '100%', height: '100%', objectFit: 'cover'}}
        />
      </AbsoluteFill>
      <AbsoluteFill
        style={{
          background:
            'linear-gradient(180deg, rgba(0,0,0,0.45) 0%, rgba(0,0,0,0) 30%, rgba(0,0,0,0) 65%, rgba(0,0,0,0.55) 100%)',
        }}
      />
      {scene.subtitle ? (
        <Enter delay={8} style={{position: 'absolute', top: 96, left: 120}}>
          <div
            style={{
              padding: '18px 34px',
              borderRadius: 14,
              background: brand.accent,
              fontSize: 58,
              fontWeight: 800,
              letterSpacing: -1.5,
            }}
          >
            {scene.subtitle}
          </div>
        </Enter>
      ) : null}
    </AbsoluteFill>
  );
};
