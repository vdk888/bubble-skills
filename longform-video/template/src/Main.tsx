import type {ReactNode} from 'react';
import {AbsoluteFill, Html5Audio, Series, interpolate, staticFile, useCurrentFrame} from 'remotion';
import script from '../script.json';
import {Backdrop, Subtitles, Watermark} from './parts';
import {brand} from './brand';
import {plan} from './timeline';
import {BarChartScene} from './scenes/BarChartScene';
import {BrollScene} from './scenes/BrollScene';
import {ComparisonScene} from './scenes/ComparisonScene';
import {KineticQuoteScene} from './scenes/KineticQuoteScene';
import {OutroScene} from './scenes/OutroScene';
import {ScenarioScene} from './scenes/ScenarioScene';
import {StatCounterScene} from './scenes/StatCounterScene';
import {TitleScene} from './scenes/TitleScene';

// script.json "type" -> component. Add a scene type here and in scenes/.
const SCENES: Record<string, (props: {scene: any}) => ReactNode> = {
  title: TitleScene,
  'stat-counter': StatCounterScene,
  'kinetic-quote': KineticQuoteScene,
  'bar-chart': BarChartScene,
  comparison: ComparisonScene,
  scenario: ScenarioScene,
  outro: OutroScene,
  broll: BrollScene,
};

// These scenes already show their words on screen, so no subtitles.
const NO_SUBTITLES = new Set(['title', 'kinetic-quote', 'outro']);

const FadeIn = ({children}: {children: ReactNode}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 10], [0, 1], {extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity}}>{children}</AbsoluteFill>;
};

export const Main = () => {
  const music = (script as any).music;
  return (
    <AbsoluteFill style={{fontFamily: brand.font, color: brand.text}}>
      <Backdrop />
      <Series>
        {plan.map(({scene, frames}) => {
          const Scene = SCENES[scene.type];
          if (!Scene) {
            throw new Error(`Unknown scene type "${scene.type}" in scene "${scene.id}".`);
          }
          return (
            <Series.Sequence key={scene.id} name={scene.id} durationInFrames={frames}>
              <FadeIn>
                <Scene scene={scene} />
                {NO_SUBTITLES.has(scene.type) ? null : <Subtitles text={scene.narration} />}
              </FadeIn>
            </Series.Sequence>
          );
        })}
      </Series>
      <Watermark />
      <Html5Audio src={staticFile('voice.wav')} />
      {music ? <Html5Audio src={staticFile(music)} volume={0.12} loop /> : null}
    </AbsoluteFill>
  );
};
