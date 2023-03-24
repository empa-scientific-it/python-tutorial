# pylint: disable=missing-docstring, unused-argument, wrong-import-position, invalid-name
from tests.testsuite import SubmissionTest


class Exercise1Test(SubmissionTest):
    def setUp(self) -> None:
        super().setUp()
        self.input = 0
        self.output = 1

    def test_one(self):
        self.assertEqual(
            self.fun(self.input), self.output, msg=f"Expected result is {self.output}"
        )

    def test_two(self):
        with self.assertRaises(TypeError):
            self.fun()
