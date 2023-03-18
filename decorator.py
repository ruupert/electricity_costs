import functools
import logging


class LogDecorator(object):
    def __init__(self):
        self.logger = logging.getLogger('electricity')
        
    def __call__(self, fn):
        @functools.wraps(fn)
        def decorated(*args, **kwargs):
            try:
                self.logger.debug("{0} - {1} - {2}".format(fn.__name__, args, kwargs))
                result = fn(*args, **kwargs)
                self.logger.debug(result)
                return result
            except Exception as e:
                self.logger.debug("Exception {0}".format(e))
                raise e
        return decorated
