"""Local reference rows the enrichment agent looks up by applicant id.

This table is a tool used inside enrichment. Other agents do not read it.
"""

from underwriting.schemas import ExternalRecord

REFERENCE_RECORDS: dict[str, ExternalRecord] = {
    "APP-1001": ExternalRecord(
        applicant_id="APP-1001",
        credit_band="excellent",
        prior_claims=0,
        property_risk="low",
    ),
    "APP-1002": ExternalRecord(
        applicant_id="APP-1002",
        credit_band="poor",
        prior_claims=4,
        property_risk="high",
    ),
    "APP-1003": ExternalRecord(
        applicant_id="APP-1003",
        credit_band="good",
        prior_claims=1,
        property_risk="moderate",
    ),
    "APP-TIMEOUT": ExternalRecord(
        applicant_id="APP-TIMEOUT",
        credit_band="fair",
        prior_claims=0,
        property_risk="moderate",
    ),
}


def lookup_external_record(applicant_id: str) -> ExternalRecord:
    """Return the reference row for one applicant."""
    try:
        return REFERENCE_RECORDS[applicant_id]
    except KeyError as exc:
        raise KeyError(f"no external record for {applicant_id}") from exc
