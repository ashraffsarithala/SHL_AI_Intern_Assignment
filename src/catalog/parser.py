
"""
Catalog Parser.

Responsible for safely loading the raw SHL assessment catalog from disk.

The parser is the first stage of the catalog processing pipeline.
It performs only file loading and structural validation.

Pipeline:

catalog.json
      ↓
CatalogParser
      ↓
tuple[RawCatalogEntry, ...]
      ↓
CatalogNormalizer
      ↓
Assessment Models

This module intentionally does NOT:

- normalize values
- clean text
- validate business rules
- construct Assessment models
- generate metadata
- create embeddings
"""

from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path

from src.core.exceptions import CatalogParsingError
from src.core.types import RawCatalogEntry


class CatalogParser:
    """
    Loads the raw SHL catalog from disk.

    Responsibilities
    ----------------
    - Verify the catalog file exists.
    - Read the JSON file.
    - Validate the JSON structure.
    - Return immutable raw catalog entries.

    This class intentionally performs no normalization or business
    validation. Those responsibilities belong to later stages of the
    processing pipeline.
    """

    def __init__(self, catalog_path: Path) -> None:
        """
        Initialize the parser.

        Parameters
        ----------
        catalog_path:
            Path to the raw catalog JSON file.
        """
        self._catalog_path = catalog_path

    def _validate_file_exists(self) -> None:
        """
        Ensure the catalog file exists.

        Raises
        ------
        CatalogParsingError
            If the catalog file cannot be found.
        """
        if not self._catalog_path.exists():
            raise CatalogParsingError(
                f"Catalog file not found: {self._catalog_path}"
            )

        if not self._catalog_path.is_file():
            raise CatalogParsingError(
                f"Catalog path is not a file: {self._catalog_path}"
            )

    def _load_json(self) -> object:
        """
        Load the catalog JSON.

        Returns
        -------
        object
            Raw JSON object.

        Raises
        ------
        CatalogParsingError
            If the JSON cannot be parsed.
        """
        try:
            with self._catalog_path.open(
                mode="r",
                encoding="utf-8",
            ) as file:
                return json.load(file)

        except JSONDecodeError as exc:
            raise CatalogParsingError(
                "Invalid catalog JSON."
            ) from exc

        except OSError as exc:
            raise CatalogParsingError(
                f"Unable to read catalog file: {self._catalog_path}"
            ) from exc

    @staticmethod
    def _validate_root(
        data: object,
    ) -> list[RawCatalogEntry]:
        """
        Validate the top-level JSON structure.

        Parameters
        ----------
        data:
            Parsed JSON object.

        Returns
        -------
        list[RawCatalogEntry]

        Raises
        ------
        CatalogParsingError
            If the catalog structure is invalid.
        """
        if not isinstance(data, list):
            raise CatalogParsingError(
                "Catalog root must be a JSON array."
            )

        validated_entries: list[RawCatalogEntry] = []

        for index, entry in enumerate(data):

            if not isinstance(entry, dict):
                raise CatalogParsingError(
                    f"Catalog entry at index {index} is not an object."
                )

            validated_entries.append(entry)

        return validated_entries
        def parse(self) -> list[RawCatalogEntry]:
        
            self._validate_file_exists()

            raw_data = self._load_json()

            validated_entries = self._validate_root(raw_data)

            return validated_entries