
"""
Catalog Normalizer.

Converts raw catalog entries loaded from catalog.json into validated
Assessment domain models.

Responsibilities
----------------
- Validate required fields.
- Normalize strings.
- Normalize lists.
- Normalize booleans.
- Construct Assessment objects.

This module intentionally does NOT:

- build embeddings
- generate metadata
- perform retrieval
- rank assessments
- filter recommendations
"""

from __future__ import annotations

from src.core.exceptions import CatalogNormalizationError
from src.core.types import RawCatalogEntry
from src.models.assessment import Assessment


class CatalogNormalizer:
    """
    Normalizes raw SHL catalog entries.

    The parser guarantees structural correctness of the JSON.

    The normalizer guarantees domain correctness before creating
    immutable Assessment objects.
    """

    REQUIRED_FIELDS = (
        "entity_id",
        "name",
        "link",
    )

    # ---------------------------------------------------------
    # Required field validation
    # ---------------------------------------------------------

    @staticmethod
    def _validate_required_fields(
        entry: RawCatalogEntry,
    ) -> None:
        """
        Ensure mandatory catalog fields exist.

        Raises
        ------
        CatalogNormalizationError
        """

        missing = [
            field
            for field in CatalogNormalizer.REQUIRED_FIELDS
            if not entry.get(field)
        ]

        if missing:
            raise CatalogNormalizationError(
                "Catalog entry missing required fields: "
                + ", ".join(missing)
            )

    # ---------------------------------------------------------
    # String normalization
    # ---------------------------------------------------------

    @staticmethod
    def _normalize_string(
        value: object,
    ) -> str:
        """
        Normalize a string field.

        Rules

        None
            -> ""

        strip whitespace

        collapse repeated whitespace
        """

        if value is None:
            return ""

        if not isinstance(value, str):
            value = str(value)

        return " ".join(value.strip().split())

    # ---------------------------------------------------------
    # Boolean normalization
    # ---------------------------------------------------------

    @staticmethod
    def _normalize_boolean(
        value: object,
    ) -> bool:
        """
        Convert common truthy/falsy values.

        Accepted truthy values

        yes
        true
        y
        1

        Accepted falsy values

        no
        false
        n
        0
        """

        if isinstance(value, bool):
            return value

        if value is None:
            return False

        if isinstance(value, (int, float)):
            return bool(value)

        normalized = (
            CatalogNormalizer._normalize_string(value)
            .lower()
        )

        truthy = {
            "yes",
            "true",
            "y",
            "1",
        }

        falsy = {
            "no",
            "false",
            "n",
            "0",
            "",
        }

        if normalized in truthy:
            return True

        if normalized in falsy:
            return False

        raise CatalogNormalizationError(
            f"Invalid boolean value: {value!r}"
        )

    # ---------------------------------------------------------
    # List normalization
    # ---------------------------------------------------------

    @staticmethod
    def _normalize_list(
        value: object,
    ) -> list[str]:
        """
        Normalize catalog list fields.

        Accepts

        None

        string

        comma separated string

        list

        Returns
        -------
        list[str]
        """

        if value is None:
            return []

        if isinstance(value, list):

            normalized = []

            for item in value:

                text = CatalogNormalizer._normalize_string(item)

                if text:
                    normalized.append(text)

            return normalized

        if isinstance(value, str):

            value = value.strip()

            if not value:
                return []

            if "," in value:

                return [
                    CatalogNormalizer._normalize_string(item)
                    for item in value.split(",")
                    if item.strip()
                ]

            return [
                CatalogNormalizer._normalize_string(value)
            ]

        return [
            CatalogNormalizer._normalize_string(value)
        ]
        # ---------------------------------------------------------
    # Assessment creation
    # ---------------------------------------------------------

    def _create_assessment(
        self,
        entry: RawCatalogEntry,
    ) -> Assessment:
        """
        Convert a normalized catalog entry into an Assessment model.

        Raises
        ------
        CatalogNormalizationError
            If the Assessment model cannot be created.
        """

        self._validate_required_fields(entry)

        try:
            return Assessment(
                entity_id=self._normalize_string(entry.get("entity_id")),
                name=self._normalize_string(entry.get("name")),
                link=self._normalize_string(entry.get("link")),
                job_levels=self._normalize_list(entry.get("job_levels")),
                languages=self._normalize_list(entry.get("languages")),
                duration=self._normalize_string(entry.get("duration")),
                remote=self._normalize_boolean(entry.get("remote")),
                adaptive=self._normalize_boolean(entry.get("adaptive")),
                description=self._normalize_string(
                    entry.get("description")
                ),
                keys=self._normalize_list(entry.get("keys")),
            )

        except Exception as exc:
            raise CatalogNormalizationError(
                "Failed to construct Assessment model."
            ) from exc

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def normalize(
        self,
        entries: list[RawCatalogEntry],
    ) -> list[Assessment]:
        """
        Normalize raw catalog entries.

        Parameters
        ----------
        entries
            Raw catalog entries returned by CatalogParser.

        Returns
        -------
        list[Assessment]

        Raises
        ------
        CatalogNormalizationError
            If normalization fails.
        """

        assessments: list[Assessment] = []

        for index, entry in enumerate(entries):

            try:
                assessment = self._create_assessment(entry)
                assessments.append(assessment)

            except CatalogNormalizationError as exc:
                raise CatalogNormalizationError(
                    f"Normalization failed for catalog entry "
                    f"at index {index}."
                ) from exc

        return assessments
