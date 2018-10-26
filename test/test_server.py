#!usr/bin/env python3
import unittest
import subprocess


class TestServer(unittest.TestCase):
    server_process = None

    # def setUp(self):
    # server_process = subprocess.Popen("~/python/IRC_Client_Server/src/server.py")

    def test_true(self):
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
