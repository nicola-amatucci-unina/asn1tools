import unittest
from .utils import Asn1ToolsBaseTest
import asn1tools


class Asn1ToolsCheckConstraintsTest(Asn1ToolsBaseTest):

    maxDiff = None

    def assert_encode_decode_ok(self, foo, datas):
        for type_name, decoded in datas:
            encoded = foo.encode(type_name, decoded, check_constraints=True)
            foo.decode(type_name, encoded, check_constraints=True)

    def assert_encode_decode_bad(self, foo, datas):
        for type_name, decoded, message in datas:
            # Encode check.
            with self.assertRaises(asn1tools.ConstraintsError) as cm:
                foo.encode(type_name, decoded, check_constraints=True)

            self.assertEqual(str(cm.exception), message)

            # Decode check.
            encoded = foo.encode(type_name, decoded, check_constraints=False)

            with self.assertRaises(asn1tools.ConstraintsError) as cm:
                foo.decode(type_name, encoded, check_constraints=True)

            self.assertEqual(str(cm.exception), message)

    def test_all_codecs(self):
        codecs = [
            'ber',
            'der',
            'gser',
            'jer',
            'per',
            'uper',
            'xer'
        ]

        for codec in codecs:
            foo = asn1tools.compile_string(
                "Foo DEFINITIONS AUTOMATIC TAGS ::= "
                "BEGIN "
                "A ::= INTEGER "
                "END",
                codec)

            encoded = foo.encode('A', 0, check_constraints=True)

            if codec != 'gser':
                foo.decode('A', encoded, check_constraints=True)

    def test_integer(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= INTEGER "
            "B ::= INTEGER (5..99) "
            "C ::= INTEGER (-10..10) "
            "D ::= INTEGER (5..99, ...) "
            "E ::= INTEGER (1000..1000) "
            "F ::= SEQUENCE { "
            "  a INTEGER (4..4), "
            "  b INTEGER (40..40), "
            "  c INTEGER (400..400) "
            "} "
            "G ::= B (6..7) "
            "END")

        # Ok.
        datas = [
            ('A',  32768),
            ('A',      0),
            ('A', -32769),
            ('B',      5),
            ('B',      6),
            ('B',     99),
            ('C',    -10),
            ('C',     10),
            ('D',     99),
            ('E',   1000),
            ('F',   {'a': 4, 'b': 40, 'c': 400})
        ]

        self.assert_encode_decode_ok(foo, datas)

        # Not ok.
        datas = [
            ('B',
             4,
             'Expected an integer between 5 and 99, but got 4.'),
            ('B',
             100,
             'Expected an integer between 5 and 99, but got 100.'),
            ('C',
             -11,
             'Expected an integer between -10 and 10, but got -11.'),
            ('C',
             11,
             'Expected an integer between -10 and 10, but got 11.'),
            ('D',
             100,
             'Expected an integer between 5 and 99, but got 100.'),
            ('E',
             0,
             'Expected an integer between 1000 and 1000, but got 0.'),
            ('F',
             {'a': 4, 'b': 41, 'c': 400},
             'b: Expected an integer between 40 and 40, but got 41.')
        ]

        self.assert_encode_decode_bad(foo, datas)

    def test_bit_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= BIT STRING "
            "B ::= BIT STRING (SIZE (10)) "
            "END")

        # Ok.
        datas = [
            ('A',  (b'', 0)),
            ('B',  (b'\x01\x23', 10))
        ]

        self.assert_encode_decode_ok(foo, datas)

        # Not ok.
        datas = [
            ('B',
             (b'\x01\x23', 9),
             'Expected between 10 and 10 number of bits, but got 9.')
        ]

        self.assert_encode_decode_bad(foo, datas)

    def test_choice(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= CHOICE { a INTEGER (1..2) } "
            "END")

        # Ok.
        datas = [
            ('A',  ('a', 1))
        ]

        self.assert_encode_decode_ok(foo, datas)

        # Not ok.
        datas = [
            ('A',
             ('a', 3),
             'a: Expected an integer between 1 and 2, but got 3.')
        ]

        self.assert_encode_decode_bad(foo, datas)


if __name__ == '__main__':
    unittest.main()
