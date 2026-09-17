"""Checks for narration timing and concurrent cache use; no external requests."""
import base64
import concurrent.futures
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest
import wave
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
def module(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / file)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded

narration = module('narration', 'narrate-video.py')
renderer = module('renderer', 'render-video.py')

class NarrationTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('ffmpeg'), 'FFmpeg required for audio timing regression')
    def test_normalized_mp3_preserves_opening_silence_and_scene_duration(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'speech.mp3';output=Path(tmp)/'scene.wav'
            subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i',
                            'sine=frequency=600:duration=5:sample_rate=44100',
                            '-c:a','libmp3lame',str(source)],check=True)
            renderer.render_scene_audio(source,7,output)
            with wave.open(str(output)) as wav:
                self.assertEqual(wav.getnframes(),7*48000)
                self.assertEqual(wav.getframerate(),48000)
                self.assertEqual(wav.readframes(16800),bytes(16800*2))
                self.assertNotEqual(wav.readframes(48000),bytes(48000*2))

    def test_concurrent_renders_share_one_audio_and_timing_pair(self):
        class Response:
            def __enter__(self):
                time.sleep(.04)
                return self
            def __exit__(self, *args):
                pass
            def read(self):
                return json.dumps({
                    'audio_base64': base64.b64encode(b'test audio').decode(),
                    'alignment': {'characters': list('Hello.'),
                                  'character_start_times_seconds': [0, .1, .2, .3, .4, .5],
                                  'character_end_times_seconds': [.1, .2, .3, .4, .5, .6]},
                }).encode()
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'ELEVENLABS_API_KEY': 'test-key'}):
            with patch.object(narration.urllib.request, 'urlopen', side_effect=lambda *a, **k: Response()) as request:
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                    records = list(pool.map(lambda _: narration.synthesize('Hello.', 'voice', Path(tmp)), range(2)))
                self.assertEqual(request.call_count, 1)
            self.assertEqual(records[0], records[1])
            self.assertEqual(Path(records[0]['audio']).read_bytes(), b'test audio')
            self.assertNotIn('test-key', json.dumps(records))

    def test_subtitle_timing_follows_speech_across_scene_boundaries(self):
        cues = renderer.captions([
            {'duration': 10, 'speech': {'cues': [[1.2, 3.4, 'First statement.']]}},
            {'duration': 8, 'speech': {'cues': [[0, 2.5, 'Second statement.']]}},
        ])
        self.assertAlmostEqual(cues[0][0], 1.55)
        self.assertAlmostEqual(cues[1][0], 10.35)
        self.assertAlmostEqual(cues[1][1], 12.85)
        self.assertLess(cues[0][1], cues[1][0])

if __name__ == '__main__':
    unittest.main()
