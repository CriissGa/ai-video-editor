import copy
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from edit_effects import effect_expressions, validate_events
from prepare_captions import generate_captions


def evaluate(expression, at):
    # Solo expresiones producidas por el generador, sin entradas ejecutables del plan.
    return eval(expression, {'__builtins__': {}}, {'time': at, 'iif': lambda c, a, b: a if c else b,
        'min': min, 'max': max, 'sin': math.sin, 'Point': lambda x, y: (x, y)})


class EffectsTests(unittest.TestCase):
    def setUp(self):
        self.zoom = {'type': 'punch_zoom', 'in_seconds': 1, 'out_seconds': 2, 'amount': 1.2}
        self.shake = {'type': 'shake', 'in_seconds': 1.2, 'out_seconds': 1.5, 'amount': 0.01}

    def test_validation_limits_and_overlap(self):
        validate_events([self.zoom, self.shake], 30, 90)
        for changes in [{'amount': float('nan')}, {'amount': 2}, {'out_seconds': 10},
                        {'type': 'unknown'}, {'out_seconds': 1.01}, {'in_seconds': -0.001}]:
            event = dict(self.zoom, **changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                validate_events([event], 30, 90)
        with self.assertRaises(ValueError):
            validate_events([self.zoom, copy.deepcopy(self.zoom)], 30, 90)
        with self.assertRaises(ValueError):
            validate_events([dict(self.shake, out_seconds=2)], 30, 90)

    def test_zoom_ramp_and_exact_end(self):
        zoom, center, samples = effect_expressions([self.zoom], 30, 0, 90, 0, 1.0)
        self.assertEqual(evaluate(zoom, 29), 1)
        self.assertLess(evaluate(zoom, 30), 1.2)
        self.assertAlmostEqual(evaluate(zoom, 40), 1.2)
        self.assertLess(evaluate(zoom, 59), 1.2)
        self.assertEqual(evaluate(zoom, 60), 1)
        self.assertEqual(evaluate(center, 40), (0.5, 0.5))
        self.assertEqual(samples[0]['frame'], 45)

    def test_shake_displacement_and_reset(self):
        zoom, center, _ = effect_expressions([self.shake], 30, 0, 90, 0, 1.0)
        self.assertNotEqual(evaluate(center, 40), (0.5, 0.5))
        self.assertGreater(evaluate(zoom, 40), 1)
        self.assertEqual(evaluate(center, 45), (0.5, 0.5))
        self.assertEqual(evaluate(zoom, 45), 1)

    def test_mapping_to_clip_local_time(self):
        zoom, _, _ = effect_expressions([self.zoom], 30, 30, 60, 10, 1.0)
        self.assertAlmostEqual(evaluate(zoom, 20), 1.2)
        self.assertEqual(evaluate(zoom, 40), 1)
        zoom, center, samples = effect_expressions([self.zoom], 30, 90, 30, 0, 1.0)
        self.assertEqual(samples, [])
        self.assertEqual(evaluate(zoom, 0), 1)
        self.assertEqual(evaluate(center, 0), (0.5, 0.5))

    def test_preserve_mixed_language_and_spoken_grammar(self):
        plan = {'timeline': {'fps': 30}, 'segments': [{'in_seconds': 0, 'out_seconds': 2}]}
        transcript = {'fps': 30, 'source_frames': 60, 'words': [
            {'start_frame': 0, 'end_frame': 10, 'text': 'Yo'},
            {'start_frame': 10, 'end_frame': 20, 'text': 'speak'},
            {'start_frame': 20, 'end_frame': 30, 'text': 'bien.'}]}
        captions = generate_captions(plan, transcript, 'bold-yellow-v2')
        self.assertEqual(captions[0]['text'], 'YO SPEAK BIEN.')


if __name__ == '__main__':
    unittest.main()
