from tests.testsuite import SubmissionTest

class Exercise1Test(SubmissionTest):
    def setUp(self) -> None:
        super().setUp()

    def test_one(self):
        self.assertEqual(self.fun(self.input), 1, msg="f(2) should return 1")

    def test_two(self):
        with self.assertRaises(TypeError):
            self.fun()

