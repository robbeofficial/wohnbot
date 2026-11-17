import json
import os
import unittest
from unittest import mock

import wohnbot
from wohnbot import redis_sink

FLATS = [
    {'link': 'https://example.test/a', 'text': 'Wohnung A | Straße 1'},
    {'link': 'https://example.test/b', 'text': 'Wohnung B', 'extra': 7},
]
ENV = {'UPSTASH_REDIS_REST_URL': 'https://redis.test/', 'UPSTASH_REDIS_REST_TOKEN': 'secret'}


def fake_response(payload, status=200):
    response = mock.Mock(status_code=status)
    response.json.return_value = payload
    response.raise_for_status.side_effect = None if status < 400 else RuntimeError(f'HTTP {status}')
    return response


class RedisSinkTest(unittest.TestCase):
    def setUp(self):
        wohnbot.params['redis'] = {'enabled': True, 'key': 'k', 'maxlen': 50, 'timeout': 3}
        patcher = mock.patch.dict(os.environ, ENV)
        patcher.start()
        self.addCleanup(patcher.stop)
        sleeper = mock.patch('wohnbot.redis_sink.time.sleep')
        sleeper.start()
        self.addCleanup(sleeper.stop)

    def test_one_xadd_per_listing(self):
        commands = redis_sink.build_commands(FLATS, 'gewobag', key='k', maxlen=50)
        self.assertEqual(len(commands), 2)
        first = commands[0]
        self.assertEqual(first[:6], ['XADD', 'k', 'MAXLEN', '~', '50', '*'])
        fields = dict(zip(first[6::2], first[7::2]))
        self.assertEqual(fields['site'], 'gewobag')
        self.assertEqual(fields['link'], FLATS[0]['link'])
        self.assertEqual(json.loads(fields['data']), FLATS[0])

    @mock.patch('wohnbot.redis_sink.requests.post')
    def test_publish_sends_one_pipeline_request(self, post):
        post.return_value = fake_response([{'result': '1-0'}, {'result': '2-0'}])
        redis_sink.publish(FLATS, 'gewobag')
        self.assertEqual(post.call_count, 1)
        args, kwargs = post.call_args
        self.assertEqual(args[0], 'https://redis.test/pipeline')
        self.assertEqual(kwargs['headers'], {'Authorization': 'Bearer secret'})
        self.assertEqual(len(kwargs['json']), 2)

    @mock.patch('wohnbot.redis_sink.requests.post')
    def test_failure_is_retried_and_never_raises(self, post):
        post.side_effect = ConnectionError('down')
        redis_sink.publish(FLATS, 'gewobag')
        self.assertEqual(post.call_count, redis_sink.ATTEMPTS)

    @mock.patch('wohnbot.redis_sink.requests.post')
    def test_command_error_in_pipeline_counts_as_failure(self, post):
        post.return_value = fake_response([{'result': '1-0'}, {'error': 'ERR bad'}])
        redis_sink.publish(FLATS, 'gewobag')
        self.assertEqual(post.call_count, redis_sink.ATTEMPTS)

    @mock.patch('wohnbot.redis_sink.requests.post')
    def test_disabled_or_empty_sends_nothing(self, post):
        wohnbot.params['redis']['enabled'] = False
        redis_sink.publish(FLATS, 'gewobag')
        wohnbot.params['redis']['enabled'] = True
        redis_sink.publish([], 'gewobag')
        post.assert_not_called()

    @mock.patch('wohnbot.redis_sink.requests.post')
    def test_missing_credentials_sends_nothing(self, post):
        with mock.patch.dict(os.environ, {'UPSTASH_REDIS_REST_URL': '', 'UPSTASH_REDIS_REST_TOKEN': ''}):
            redis_sink.publish(FLATS, 'gewobag')
        post.assert_not_called()


if __name__ == '__main__':
    unittest.main()
