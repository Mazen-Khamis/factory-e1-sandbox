"""Acceptance test. In the experiment this file stands for the approved acceptance tests."""
import unittest

from calc import add


class AcceptanceAdd(unittest.TestCase):
    def test_add(self):
        print("ACCEPTANCE-TEST-VERSION: approved-v1")
        self.assertEqual(add(2, 3), 5)


if __name__ == "__main__":
    unittest.main()
