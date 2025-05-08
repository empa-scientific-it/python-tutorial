# Configuration file for ipython.
c = get_config()  # noqa # type: ignore

# Automatically load testsuite extension
c.InteractiveShellApp.extensions = ["tutorial.tests.testsuite"]
