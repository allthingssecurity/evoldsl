import {Composition} from 'remotion';
import {EvolDSLVideo} from './EvolDSLVideo';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="EvolDSLVideo"
        component={EvolDSLVideo}
        durationInFrames={5400} // 3 minutes at 30fps
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{}}
      />
    </>
  );
};