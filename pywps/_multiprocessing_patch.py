##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

"""
Add configurable multiprocessing start method for async processes (Python 3.8+ fix)
"""

import multiprocessing
import sys
import logging
from pywps import configuration

LOGGER = logging.getLogger("PYWPS")


def patch_multiprocessing_start_method():
    """Patch multiprocessing start method early, optionally using pywps.cfg config."""
    try:
        # Only set if not already initialized
        current = multiprocessing.get_start_method(allow_none=True)
        if current is not None:
            return  # already set by other lib or user

        # Check user-configured method
        method = None
        if configuration.has_config():
            # Allowed: fork, spawn, forkserver
            method = configuration.get_config_value(
                "processing", "multiprocessing_start_method", None
            )

        # If not configured, choose platform default
        if method is None:
            if sys.platform.startswith("linux"):
                method = "fork"
            elif sys.platform == "darwin":
                method = "forkserver"
            else:
                return  # unsupported platform, do nothing

        LOGGER.info(f"Using multiprocessing start method: {method}")
        multiprocessing.set_start_method(method)
    except RuntimeError:
        # Already set elsewhere (e.g., by gunicorn preloader) — safe to ignore
        pass
    except Exception as e:
        LOGGER.warning(f"Failed to patch multiprocessing start method: {e}")
