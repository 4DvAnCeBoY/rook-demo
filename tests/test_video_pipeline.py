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
    def test_speech_led_edit_does_not_pad_to_old_running_time(self):
        plan={'id':'assurance','voice':{'voiceId':'voice'},'pacing':'speech-led','durationSeconds':360,
              'scenes':[{'duration':40,'narration':'First.'},{'duration':40,'narration':'Second.'}]}
        records=[{'duration':3.4,'audio':'first.mp3','cues':[]},{'duration':7.9,'audio':'second.mp3','cues':[]}]
        with tempfile.TemporaryDirectory() as tmp, patch.object(narration,'synthesize',side_effect=records):
            result=narration.narrate(plan,Path(tmp)/'output',Path(tmp)/'cache')
        self.assertLess(result['durationSeconds'],11.4)
        for scene in result['scenes']:
            self.assertGreaterEqual(scene['duration'],scene['speech']['duration'])
            self.assertLess(scene['duration']-scene['speech']['duration'],1/24)
            self.assertAlmostEqual(scene['duration']*24,round(scene['duration']*24))

    @unittest.skipUnless(shutil.which('ffmpeg'), 'FFmpeg required for audio timing regression')
    def test_normalized_mp3_starts_without_added_silence_and_matches_scene_duration(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'speech.mp3';output=Path(tmp)/'scene.wav'
            subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i',
                            'sine=frequency=600:duration=5:sample_rate=44100',
                            '-c:a','libmp3lame',str(source)],check=True)
            renderer.render_scene_audio(source,5,output)
            with wave.open(str(output)) as wav:
                self.assertEqual(wav.getnframes(),5*48000)
                self.assertEqual(wav.getframerate(),48000)
                self.assertNotEqual(wav.readframes(2400),bytes(2400*2))
                self.assertNotEqual(wav.readframes(48000),bytes(48000*2))
                wav.setpos(5*48000-2400)
                self.assertNotEqual(wav.readframes(2400),bytes(2400*2))

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
        self.assertAlmostEqual(cues[0][0], 1.2)
        self.assertAlmostEqual(cues[1][0], 10)
        self.assertAlmostEqual(cues[1][1], 12.5)
        self.assertLess(cues[0][1], cues[1][0])

if __name__ == '__main__':
    unittest.main()
