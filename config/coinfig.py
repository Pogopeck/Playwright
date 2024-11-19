import os

class TestConfig:
    # Environment settings
    BASE_URL = os.getenv('BASE_URL', 'http://your-application-url')
    ENVIRONMENT = os.getenv('TEST_ENV', 'staging')
    
    # Timeouts
    DEFAULT_TIMEOUT = 30000
    NAVIGATION_TIMEOUT = 60000
    
    # Screenshot settings
    SCREENSHOT_DIR = 'screenshots'
    
    # Report settings
    REPORT_DIR = 'reports'
    
    # Test data
    TEST_USER = os.getenv('TEST_USER', 'test_user')
    TEST_PASSWORD = os.getenv('TEST_PASSWORD', 'test_pass')
