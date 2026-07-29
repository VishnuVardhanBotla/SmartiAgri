import pytest

from language import get_language, set_language, translate


@pytest.fixture
def app_context():
    from flask import Flask, g

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test'

    @app.before_request
    def _prepare_language():
        g.language = get_language()

    with app.test_request_context('/'):
        yield app


def test_language_helper_uses_default_and_selected_locale(app_context):
    assert get_language() == 'en'
    assert translate('nav.home') == 'Home'

    set_language('te')
    assert get_language() == 'te'
    assert translate('nav.home') == 'హోమ్'
