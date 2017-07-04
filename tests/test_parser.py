import unittest

from apiaiassistant.parser import PayloadParser
from apiaiassistant.parser import GoogleAssistantParser

from tests import get_dummy_request


class PayloadParserTestCase(unittest.TestCase):
    def test_is_valid_not_implemented(self):
        parser = PayloadParser({})
        with self.assertRaises(NotImplementedError):
            parser.is_valid


class GoogleAssistantParserTestCase(unittest.TestCase):
    def setUp(self):
        self.request = get_dummy_request()

    def test_action(self):
        action = 'foobar'
        self.request['result']['action'] = action

        parser = GoogleAssistantParser(self.request)
        self.assertEqual(parser.action, action)

    def test_parameters(self):
        self.request['result']['parameters'] = {
            "given-name": "Zack",
            "given-name2": "Alberto",
            "given-name3": "Dom",
            "ordinal": "33rd",
            "number": "thirty-three",
            "other-ordinal": "thirty third",
            "number-list": ["2nd", "second"]
        }

        parser = GoogleAssistantParser(self.request)
        self.assertEqual(parser.get('given-name'), "Zack")
        self.assertEqual(
            parser.get('given-name', globbing=True),
            ["Zack", "Alberto", "Dom"])
        self.assertEqual(
            parser.get('ordinal', _type=parser.PARAM_TYPES.NUMBER), 33)
        self.assertEqual(
            parser.get('number', _type=parser.PARAM_TYPES.NUMBER), 33)
        self.assertEqual(
            parser.get('other-ordinal', _type=parser.PARAM_TYPES.NUMBER), 33)
        self.assertEqual(
            parser.get('number-list', _type=parser.PARAM_TYPES.NUMBER), [2, 2])

    def test_contexts(self):
        contexts = [
            {'name': 'c1', 'parameters': {'foo': 'bar'}, 'lifespan': 5},
            {'name': 'c2', 'parameters': {'bar': 'foo'}, 'lifespan': 5},
            {'name': 'c3', 'parameters': {'foobar': 42}, 'lifespan': 5},
        ]
        self.request['result']['contexts'] = contexts

        parser = GoogleAssistantParser(self.request)
        self.assertEqual(parser.get_contexts(), contexts)
        self.assertEqual(parser.get_contexts('c1'), {'foo': 'bar'})
        self.assertEqual(parser.get_contexts('c4'), {})

    def test_capabilities(self):
        self.request['originalRequest']['data']['surface']['capabilities'] = [
            {'name': 'actions.capability.AUDIO_OUTPUT'},
            {'name': 'actions.capability.SCREEN_OUTPUT'}
        ]
        parser = GoogleAssistantParser(self.request)
        self.assertTrue(parser.has_screen_capability())
        self.assertTrue(parser.has_audio_capability())

        self.request['originalRequest']['data']['surface']['capabilities'] = []
        parser = GoogleAssistantParser(self.request)
        self.assertFalse(parser.has_screen_capability())
        self.assertFalse(parser.has_audio_capability())

        self.request['originalRequest']['data'] = {}
        parser = GoogleAssistantParser(self.request)
        self.assertFalse(parser.has_screen_capability())
        self.assertFalse(parser.has_audio_capability())

    def test_user(self):
        user_name = 'foo'
        user_id = 'bar'
        self.request['originalRequest']['data']['user'] = {
            'userName': user_name,
            'userId': user_id
        }

        parser = GoogleAssistantParser(self.request)
        self.assertEqual(parser.user.name, user_name)
        self.assertEqual(parser.user.id, user_id)

        self.request['originalRequest']['data']['user']['userName'] = user_name[::-1]
        self.assertEqual(parser.user.name, user_name)


if __name__ == '__main__':
    unittest.main()
