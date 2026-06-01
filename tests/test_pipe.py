"""Regression test: piping output to a consumer that closes early must not
dump a BrokenPipeError traceback (e.g. `monolith bench | head -1`)."""

import os
import shutil
import subprocess
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@unittest.skipUnless(shutil.which("head"), "needs the `head` utility")
class BrokenPipeTests(unittest.TestCase):
    def test_bench_piped_to_head_has_no_traceback(self):
        env = {**os.environ, "PYTHONPATH": os.path.join(REPO_ROOT, "src")}
        producer = subprocess.Popen(
            [sys.executable, "-m", "monolith", "bench"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=REPO_ROOT,
            env=env,
        )
        # `head -n 1` reads one line then closes the pipe.
        subprocess.run(["head", "-n", "1"], stdin=producer.stdout, capture_output=True)
        producer.stdout.close()
        _, err = producer.communicate(timeout=30)
        stderr = err.decode("utf-8", "replace")
        self.assertNotIn("BrokenPipeError", stderr)
        self.assertNotIn("Traceback", stderr)


if __name__ == "__main__":
    unittest.main()
