# tests/conftest.py
import pytest
from playwright.sync_api import Page
from config.config import TestConfig
from utils.helpers import TestHelpers
from utils.logger import TestLogger

@pytest.fixture(scope="session")
def config():
    return TestConfig()

@pytest.fixture(scope="session")
def logger():
    return TestLogger().logger

@pytest.fixture(scope="function")
def context_with_retry(browser):
    context.set_default_timeout(TestConfig.DEFAULT_TIMEOUT)
    yield context
    context.close()

@pytest.fixture(scope="function")
def page(context_with_retry):
    page = context_with_retry.new_page()
    yield page
    page.close()

@pytest.fixture(scope="function")
def helpers(page):
    return TestHelpers(page)
