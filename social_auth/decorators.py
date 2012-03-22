from django.core.urlresolvers import reverse
from django.utils.http import urlencode
from django.shortcuts import redirect
from social_auth.backends import get_backend
from social_auth.views import COMPLETE_URL_NAME

try:
    from functools import wraps
except ImportError:
    def wraps(wrapped, assigned=('__module__', '__name__', '__doc__'),
              updated=('__dict__',)):
        def inner(wrapper):
            for attr in assigned:
                setattr(wrapper, attr, getattr(wrapped, attr))
            for attr in updated:
                getattr(wrapper, attr).update(getattr(wrapped, attr, {}))
            return wrapper
        return inner

def social_login_required(backend_name=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    def decorator(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            login_url = reverse('socialauth_begin', args=(backend_name,))
            login_url += '?'+urlencode({ 'next': request.get_full_path() })

            try:
                access_token = request.session.get('social_auth_data')[backend_name]['access_token']
            except (TypeError, KeyError):
                return redirect(login_url)

            # If the token is invalid, redirect to login
            backend = get_backend(backend_name, request, login_url)
            if backend.token_is_valid(access_token):
                return function(request, *args, **kwargs)
            else:
                return redirect(login_url)

        return wrapper
    return decorator
