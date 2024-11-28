"""
Limita o número máximo de requisições por IP por intervalo de tempo.

O limite padrão é de 30 requisições por minuto.
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["30/minute"])
"""O limitador de requisições. O limite padrão é de 30 requisições por minuto."""