from django.test import TestCase


class TestStringMethods(TestCase):
    def test_length(self):
        self.assertEqual(len('Yatube'), 6)

    def test_show_msg(self):
        # действительно ли первый аргумент — True?
        self.assertTrue(True, msg="Важная проверка на истинность")
