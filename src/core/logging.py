"""
Centralised logging configuration for the SHL Assessment Recommendation Agent.

This module exposes a single public function — :func:`get_logger` — that every
module in the project uses to obtain a pre-configured :class:`logging.Logger`::

    from src.core.logging import get_logger

    logger = get_logger(__name__)
    logger.info("Pipeline started.")

Design Decisions
----------------
1. **One formatter, one format** – Every handler (console or file) uses the same
   layout so that log output is consistent regardless of where it is viewed.
   The format includes *timestamp*, *level*, *logger name* (module path),
   *function name*, and *line number* — everything needed for debugging without
   external tooling.

2. **Root-logger setup happens once** – ``_configure_root_logger()`` is guarded
   by a module-level flag so that it runs at most once, even if ``get_logger``
   is called from dozens of modules.

3. **Console handler writes to stderr** – ``sys.stderr`` is the conventional
   destination for diagnostic output; ``sys.stdout`` is reserved for application
   data (e.g., JSON responses).

4. **File handler is opt-in** – ``enable_file_logging()`` can be called once
   during bootstrap (e.g., in ``src/main.py``) to add a file handler to *all*
   loggers that have already been created.  This avoids creating log files
   during unit tests or one-off scripts.

5. **Log level from config** – The root logger level is read from
   ``get_settings().LOG_LEVEL`` so that changing the ``.env`` value is all that
   is needed to switch between ``DEBUG`` and ``INFO``.
"""

from __future__ import annotations

import logging
import sys
import threading
from pathlib import Path
from typing import Final

from src.core.config import get_settings

# ---------------------------------------------------------------------------
#   Format constants
# ---------------------------------------------------------------------------
_LOG_FORMAT: Final[str] = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
)
_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"

# ---------------------------------------------------------------------------
#   Internal state
# ---------------------------------------------------------------------------
_root_configured: bool = False
_lock: threading.Lock = threading.Lock()


def _build_formatter() -> logging.Formatter:
    """Return a :class:`logging.Formatter` with the project-wide layout."""
    return logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT)


def _configure_root_logger() -> None:
    """Attach a stderr console handler to the root logger exactly once.

    The root logger level is set to the value of ``LOG_LEVEL`` from the
    application settings.  All child loggers inherit this level unless
    explicitly overridden.

    Thread-safe: a :class:`threading.Lock` ensures that concurrent calls
    from multiple uvicorn threads cannot attach duplicate handlers.
    """
    global _root_configured
    if _root_configured:
        return

    with _lock:
        # Double-checked locking: re-test inside the lock.
        if _root_configured:
            return

        settings = get_settings()
        root = logging.getLogger()
        root.setLevel(settings.LOG_LEVEL)

        console_handler = logging.StreamHandler(stream=sys.stderr)
        console_handler.setFormatter(_build_formatter())
        root.addHandler(console_handler)

        _root_configured = True


# ---------------------------------------------------------------------------
#   Public API
# ---------------------------------------------------------------------------
def get_logger(name: str) -> logging.Logger:
    """Return a configured :class:`logging.Logger` for the given module name.

    Parameters
    ----------
    name:
        Normally ``__name__``.  The resulting logger inherits the root level
        and console handler set up by :func:`_configure_root_logger`.

    Returns
    -------
    logging.Logger
        A ready-to-use logger instance.

    Example
    -------
    ::

        from src.core.logging import get_logger

        logger = get_logger(__name__)
        logger.info("Module loaded.")
    """
    _configure_root_logger()
    return logging.getLogger(name)


def enable_file_logging(log_file: str | Path = "logs/app.log") -> None:
    """Add a file handler to the root logger so all loggers write to disk.

    This function is idempotent — calling it more than once with the same path
    will **not** add duplicate handlers.

    Parameters
    ----------
    log_file:
        Path to the log file.  Parent directories are created automatically.
    """
    path = Path(log_file).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()

    # Guard against duplicate file handlers pointing to the same file.
    for existing in root.handlers:
        if (
            isinstance(existing, logging.FileHandler)
            and Path(existing.baseFilename).resolve() == path
        ):
            return

    file_handler = logging.FileHandler(path, encoding="utf-8")
    file_handler.setFormatter(_build_formatter())
    root.addHandler(file_handler)
