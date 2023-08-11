from flask import redirect, render_template, request, session
from functools import wraps

def login_requirede(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("cliente_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function