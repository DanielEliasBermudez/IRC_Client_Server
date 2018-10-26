#!usr/bin/env python3
import unittest
import subprocess

# from src import server


class TestServer(unittest.TestCase):
    server_process = None

    # def setUp(self):
    #     server_process = subprocess.Popen()
    #     server.main()

    def test_true(self):
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
