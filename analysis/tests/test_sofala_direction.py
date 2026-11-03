"""Hand-built one-way case must flip exactly one decision between routing directions."""
import importlib.util
from pathlib import Path
import sys

ANALYSIS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ANALYSIS))
spec = importlib.util.spec_from_file_location('direction', ANALYSIS / 'run_sofala_direction.py')
direction = importlib.util.module_from_spec(spec)
spec.loader.exec_module(direction)


def test_direction_flip_and_one_way_share():
    assert direction.self_check()['decision_changes'] == 1
