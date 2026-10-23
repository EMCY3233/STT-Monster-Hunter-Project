"""Compile and run the Vita agent's portable C logic on the host, if a C compiler exists.

Host results cover decision logic only; they are not physical validation on the console.
"""
import os
import shutil
import subprocess
import tempfile
import unittest

from stt_monitor.protocol import decode

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'vita-agent', 'src')
TEST = os.path.join(ROOT, 'tests', 'c', 'test_agent_logic.c')
COMPILER = next((c for c in ('cc', 'gcc', 'clang') if shutil.which(c)), None)


@unittest.skipUnless(COMPILER, 'no C compiler on this host')
class AgentLogicTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.binary = os.path.join(cls.tmp.name, 'test_agent_logic')
        sources = [TEST] + [os.path.join(SRC, n) for n in ('recovery.c', 'deadline_clock.c', 'telemetry.c')]
        subprocess.run([COMPILER, '-std=c99', '-Wall', '-Wextra', '-Werror', '-I', SRC,
                        '-o', cls.binary] + sources, check=True, capture_output=True, text=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_c_checks_pass(self):
        result = subprocess.run([self.binary], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_c_encoder_output_accepted_by_python_receiver(self):
        result = subprocess.run([self.binary, '--emit'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        packet = decode(result.stdout.strip().encode('utf-8'))
        self.assertEqual(packet['version'], 2)
        self.assertEqual(packet['source'], 'vita')
        self.assertEqual(packet['diagnostics']['send_ok'] + packet['diagnostics']['send_errors'],
                         packet['seq'])


if __name__ == '__main__':
    unittest.main()
