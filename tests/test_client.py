import unittest

import microgear
from microgear.client import create


class TestCreate(unittest.TestCase):
    def setUp(self):
        self.gearkey = '1a2b3c4d5e6f7g8'
        self.gearsecret = 'A1B2C3d4e5f6G7H8i9j10k11L'
        self.appid = 'FooBar'
        self.gearalias = 'strecth'
        self.gearalias_more_than_16_characters = 'jessiestretchbuster'

    def connection(self):
        return 'Connected'

    def subscription(self, topic, message):
        return topic + ' ' + message

    def disconnect(self):
        return 'Disconnected'

    def test_create(self):
        """
        Test create client with `gearkey`, `gearsecret` and `appid` paremeters.
        """
        create(self.gearkey, self.gearsecret, self.appid)

        self.assertEqual(microgear.gearkey, self.gearkey)
        self.assertEqual(microgear.gearsecret, self.gearsecret)
        self.assertEqual(microgear.appid, self.appid)

    def test_create_with_gearalias(self):
        """
        Test create client with `alias` argument settings.
        """
        create(self.gearkey,
               self.gearsecret,
               self.appid,
               {'alias': self.gearalias}
        )

        self.assertEqual(microgear.gearalias, self.gearalias)

    def test_create_with_gearalias(self):
        """
        Test create client with `alias` argument settings more than 16
        characters..
        """
        create(
            self.gearkey,
            self.gearsecret,
            self.appid,
            {'alias': self.gearalias_more_than_16_characters}
        )

        self.assertNotEqual(
                microgear.gearalias,
                self.gearalias_more_than_16_characters
        )
        self.assertEqual(
                microgear.gearalias,
                self.gearalias_more_than_16_characters[0:16]
        )

    def test_on_connect(self):
        """
        Test create on_connect function.
        """
        microgear.on_connect = self.connection

        self.assertEqual(microgear.on_connect(), 'Connected')
        self.assertNotEqual(microgear.on_connect(), 'Disconnected')

    def test_on_message(self):
        """
        Test create on_connect function.
        """
        microgear.on_message = self.subscription

        self.assertEqual(microgear.on_message('topic', 'message'), 'topic message')
        self.assertEqual(microgear.on_message('', 'message'), ' message')
        self.assertEqual(microgear.on_message('topic', ''), 'topic ')

    def test_on_disconnect(self):
        """
        Test create on_connect function.
        """
        microgear.on_disconnect = self.disconnect

        self.assertEqual(microgear.on_disconnect(), 'Disconnected')
        self.assertNotEqual(microgear.on_disconnect(), 'Connected')

#if __name__ == '__main__':
#    unittest.main()
