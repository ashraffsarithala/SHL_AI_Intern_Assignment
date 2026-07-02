"""
Catalog Loader.

Coordinates the complete catalog loading pipeline.

Pipeline
--------
catalog.json
      ↓
CatalogParser
      ↓
CatalogNormalizer
      ↓
CatalogRepository

The CatalogLoader is the orchestration layer responsible for
building the in-memory catalog repository.

This module intentionally does NOT:

- perform retrieval
- generate embeddings
- rank recommendations
- communicate with the LLM
"""

from __future__ import annotations

from pathlib import Path

from src.catalog.catalog_repository import CatalogRepository
from src.catalog.normalizer import CatalogNormalizer
from src.catalog.parser import CatalogParser
from src.core.types import RawCatalogEntry
from src.models.assessment import Assessment


class CatalogLoader:
    """
    Coordinates loading of the SHL assessment catalog.

    This class wires together the parser, normalizer,
    and repository into a single reusable component.
    """

    def __init__(
        self,
        catalog_path: Path,
    ) -> None:
        """
        Initialize the loader.

        Parameters
        ----------
        catalog_path:
            Path to the raw catalog JSON file.
        """

        self._catalog_path = catalog_path

        self._parser = CatalogParser(
            catalog_path=self._catalog_path
        )

        self._normalizer = CatalogNormalizer()

    # ---------------------------------------------------------
    # Internal pipeline
    # ---------------------------------------------------------

    def _parse(self) -> list[RawCatalogEntry]:
        """
        Execute the parser stage.

        Returns
        -------
        list[RawCatalogEntry]
        """

        return self._parser.parse()

    def _normalize(
        self,
        raw_entries: list[RawCatalogEntry],
    ) -> list[Assessment]:
        """
        Execute the normalization stage.

        Parameters
        ----------
        raw_entries:
            Raw catalog entries returned by the parser.

        Returns
        -------
        list[Assessment]
        """

        return self._normalizer.normalize(raw_entries)

    @staticmethod
    def _create_repository(
        assessments: list[Assessment],
    ) -> CatalogRepository:
        """
        Build the catalog repository.

        Parameters
        ----------
        assessments:
            Normalized Assessment models.

        Returns
        -------
        CatalogRepository
        """

        return CatalogRepository(assessments)
    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def load(self) -> CatalogRepository:
        """
        Execute the complete catalog loading pipeline.

        Pipeline
        --------
        catalog.json
              ↓
        CatalogParser
              ↓
        CatalogNormalizer
              ↓
        CatalogRepository

        Returns
        -------
        CatalogRepository
            Repository containing all normalized assessments.
        """

        raw_entries = self._parse()

        assessments = self._normalize(raw_entries)

        repository = self._create_repository(
            assessments
        )

        return repository