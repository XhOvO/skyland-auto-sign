import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
sys.modules['push'] = SimpleNamespace(push=lambda *args, **kwargs: None)
sys.modules['skyland'] = SimpleNamespace(start=lambda: (True, []))
import main


class TestRequestWithRetry(unittest.TestCase):
    @patch('main.time.sleep')
    def test_request_with_retry_retries_and_succeeds(self, mock_sleep):
        attempts = {'count': 0}

        def flaky(url, **kwargs):
            attempts['count'] += 1
            if attempts['count'] < 3:
                raise requests.exceptions.ConnectionError('timeout')
            return {'ok': True, 'url': url, 'timeout': kwargs.get('timeout')}

        result = main.request_with_retry(flaky, 'post', 'https://example.com')

        self.assertEqual(attempts['count'], 3)
        self.assertEqual(result['timeout'], main.request_timeout_seconds)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch('main.time.sleep')
    def test_request_with_retry_raises_after_max_retries(self, mock_sleep):
        def always_fail(url, **kwargs):
            raise requests.exceptions.Timeout('boom')

        with self.assertRaises(requests.exceptions.Timeout):
            main.request_with_retry(always_fail, 'get', 'https://example.com')

        self.assertEqual(mock_sleep.call_count, main.request_max_retries)


if __name__ == '__main__':
    unittest.main()
