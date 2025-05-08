from requests import get, post, Response, Timeout, RequestException
from typing import Callable
from flask import current_app
from yarl import URL
from functools import wraps

class HTTPClient:

    def __init__(self, url:str, timeout:int = None):
        self.url = URL(url)
        self.timeout = timeout or current_app.config.extention.http['timeout']
        self.logger = current_app.logger

    @staticmethod
    def _safe_request(method_name: str):
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(self, *args, **kwargs) -> Response | RequestException:
                url = args[0] if args else kwargs.get("url", "<неизвестно>")
                try:
                    response = func(self, *args, **kwargs)
                    if response.status_code >= 500:
                        msg = f"{method_name.upper()} {url} returned {response.status_code}"
                        self.logger.error(msg)
                        raise RequestException(msg)
                    elif response.status_code >= 400:
                        msg = f"{method_name.upper()} {url} returned {response.status_code}"
                        self.logger.warning(msg)
                        raise RequestException(msg)
                    return response
                except Timeout as e:
                    msg = f"Timeout on {method_name.upper()} {url}"
                    self.logger.warning(msg)
                    return RequestException(msg)
                except RequestException as e:
                    self.logger.error(f"{method_name.upper()} {url} failed: {e}")
                    return RequestException(str(e))
                except Exception as e:
                    msg = f"Unexpected error on {method_name.upper()} {url}: {e}"
                    self.logger.error(msg)
                    return RequestException(msg)
            return wrapper
        return decorator

    @_safe_request("get")
    def get(self, endpoint: str, **kwargs) -> Response:
        url = str(self.url / endpoint.lstrip("/"))
        return get(url, **kwargs)
    
    @_safe_request("post")
    def post(self, endpoint: str, **kwargs) -> Response:
        url = str(self.url / endpoint.lstrip("/"))
        return post(url, **kwargs)
        