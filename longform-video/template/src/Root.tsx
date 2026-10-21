import {Composition} from 'remotion';
import {Main} from './Main';
import {FPS, totalFrames} from './timeline';

export const RemotionRoot = () => (
  <Composition
    id="Main"
    component={Main}
    durationInFrames={totalFrames}
    fps={FPS}
    width={1920}
    height={1080}
  />
);
