from unittest import TestCase
from unittest.mock import patch, MagicMock

import logging as std_logging
import cyclotron_std.logging as logging

import reactivex as rx
from reactivex.subject import Subject


class LoggingestCase(TestCase):

    def test_create_driver(self):
        driver = logging.make_driver()
        request = Subject()
        sink = logging.Sink(request=request)
        source = driver.call(sink)

        self.assertIsNone(source)

    @patch('logging.getLogger')
    def test_log(self, mock_get_logger):
        logger = MagicMock(spec=std_logging.Logger)
        mock_get_logger.return_value = logger

        driver = logging.make_driver()
        request = Subject()
        sink = logging.Sink(request=request)
        driver.call(sink)

        request.on_next(logging.Log(logger='foo', level='DEBUG', message='foo msg'))
        mock_get_logger.assert_called_with('foo')
        logger.log.assert_called_with('DEBUG', 'foo msg')

    @patch('logging.StreamHandler')
    @patch('logging.getLogger')
    def test_set_level(self, mock_get_logger, mock_stream_handler):
        logger = MagicMock(spec=std_logging.Logger)
        stream_handler = MagicMock(spec=std_logging.Handler)
        mock_get_logger.return_value = logger
        mock_stream_handler.return_value = stream_handler

        driver = logging.make_driver()
        request = Subject()
        sink = logging.Sink(request=request)
        driver.call(sink)

        request.on_next(logging.SetLevel(logger='foo', level='DEBUG'))
        mock_get_logger.assert_called_with('foo')
        logger.setLevel.assert_called_with(std_logging.DEBUG)
        mock_stream_handler.assert_called_with()
        stream_handler.setLevel.assert_called_with(std_logging.DEBUG)
