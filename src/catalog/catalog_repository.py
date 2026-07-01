"""
Catalog Repository.

Provides an in-memory repository of normalized SHL assessments.

The repository is the single source of truth for Assessment domain
objects after catalog loading.

Responsibilities
----------------
- Store normalized Assessment objects.
- Build lookup indexes.
- Prevent duplicate assessment IDs.
- Provide fast O(1) lookup operations.

This module intentionally does NOT:

- parse JSON
- normalize catalog entries
- build embeddings
- perform retrieval
- rank recommendations
"""

from __future__ import annotations

from src.core.exceptions import CatalogError
from src.models.assessment import Assessment


class CatalogRepository:
    """
    In-memory repository for Assessment objects.

    The repository owns the normalized catalog and exposes efficient
    lookup operations for downstream components.
    """

    def __init__(
        self,
        assessments: list[Assessment],
    ) -> None:
        """
        Initialize the repository.

        Parameters
        ----------
        assessments
            Normalized assessment models.

        Raises
        ------
        CatalogError
            If duplicate entity IDs or duplicate names are found.
        """

        self._assessments = list(assessments)

        self._by_id: dict[str, Assessment] = {}

        self._by_name: dict[str, Assessment] = {}

        self._build_indexes()

    # ---------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------

    def _build_indexes(self) -> None:
        """
        Build lookup dictionaries.

        Raises
        ------
        CatalogError
            If duplicate assessment IDs or names exist.
        """

        for assessment in self._assessments:

            entity_id = assessment.entity_id

            if entity_id in self._by_id:
                raise CatalogError(
                    f"Duplicate assessment entity_id: {entity_id}"
                )

            self._by_id[entity_id] = assessment

            normalized_name = self._normalize_name(
                assessment.name
            )

            if normalized_name in self._by_name:
                raise CatalogError(
                    f"Duplicate assessment name: "
                    f"{assessment.name}"
                )

            self._by_name[
                normalized_name
            ] = assessment

    @staticmethod
    def _normalize_name(
        name: str,
    ) -> str:
        """
        Normalize assessment names for
        case-insensitive lookup.
        """

        return " ".join(
            name.strip().lower().split()
        )
        # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def get_all(self) -> list[Assessment]:
        """
        Return all assessments.

        Returns
        -------
        list[Assessment]
            A shallow copy of the stored assessments.
        """

        return list(self._assessments)

    def get_by_entity_id(
        self,
        entity_id: str,
    ) -> Assessment | None:
        """
        Retrieve an assessment by its unique entity ID.

        Parameters
        ----------
        entity_id:
            SHL assessment identifier.

        Returns
        -------
        Assessment | None
            Matching assessment if found, otherwise None.
        """

        return self._by_id.get(entity_id)

    def get_by_name(
        self,
        name: str,
    ) -> Assessment | None:
        """
        Retrieve an assessment by name.

        Lookup is case-insensitive and ignores repeated whitespace.

        Parameters
        ----------
        name:
            Assessment name.

        Returns
        -------
        Assessment | None
            Matching assessment if found, otherwise None.
        """

        normalized_name = self._normalize_name(name)

        return self._by_name.get(normalized_name)

    def contains(
        self,
        entity_id: str,
    ) -> bool:
        """
        Determine whether an assessment exists.

        Parameters
        ----------
        entity_id:
            SHL assessment identifier.

        Returns
        -------
        bool
            True if the assessment exists.
        """

        return entity_id in self._by_id

    def __len__(self) -> int:
        """
        Return the total number of assessments.
        """

        return len(self._assessments)

    def __iter__(self):
        """
        Iterate over assessments in catalog order.
        """

        return iter(self._assessments)