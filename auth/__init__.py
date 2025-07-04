from flask import Blueprint

auth_bp = Blueprint('auth', __name__, template_folder='../templates')

# Ho dovuto importare le routes dopo aver definito il blueprint
# per testare il programma (senza per qualche ragione non funzionava)
# from . import routes  # noqa: E402, F401

# noqa = no quality assurance, per evitare errori di linting
# E402 = importazione dopo il codice di definizione del modulo
# F401 = importazione non utilizzata, ma necessaria per il funzionamento del modulo

r"""
segnalazione di errore:

werkzeug.routing.exceptions.BuildError
werkzeug.routing.exceptions.BuildError: Could not build url for endpoint 'auth.login'. Did you mean 'battle.begin_battle' instead?
..................

File "C:\Users\kc19k\OneDrive\Desktop\Documenti\GitHub\GDR\Gdr-flask\templates\menu.html", line 1, in top-level template code
{% extends "layout.html" %}
File "C:\Users\kc19k\OneDrive\Desktop\Documenti\GitHub\GDR\Gdr-flask\templates\layout.html", line 28, in top-level template code
{% block content %}{% endblock %}
File "C:\Users\kc19k\OneDrive\Desktop\Documenti\GitHub\GDR\Gdr-flask\templates\menu.html", line 28, in block 'content'
<a href="{{ url_for('auth.login') }}" class="btn btn-info btn-lg">Login</a>
File "C:\Users\kc19k\AppData\Local\Programs\Python\Python313\Lib\site-packages\flask\app.py", line 1121, in url_for
return self.handle_url_build_error(error, endpoint, values)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\kc19k\AppData\Local\Programs\Python\Python313\Lib\site-packages\flask\app.py", line 1110, in url_for
rv = url_adapter.build( # type: ignore[union-attr]

File "C:\Users\kc19k\AppData\Local\Programs\Python\Python313\Lib\site-packages\werkzeug\routing\map.py", line 924, in build
raise BuildError(endpoint, values, method, self)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
werkzeug.routing.exceptions.BuildError: Could not build url for endpoint 'auth.login'. Did you mean 'battle.begin_battle' instead?
"""
