"""Three mock applications used for a full pipeline run."""

from underwriting.schemas import RawApplication

MOCK_APPLICATIONS: tuple[RawApplication, ...] = (
    RawApplication(
        applicant_id="APP-1001",
        full_name="Maya Chen",
        age=34,
        product="Home",
        coverage_amount=300_000,
        stated_claims=0,
        notes="Primary residence, new roof",
    ),
    RawApplication(
        applicant_id="APP-1002",
        full_name="Leon Ruiz",
        age=62,
        product="Auto",
        coverage_amount=150_000,
        stated_claims=3,
        notes="Three at-fault accidents in five years",
    ),
    RawApplication(
        applicant_id="APP-1003",
        full_name="Priya Shah",
        age=41,
        product="Home",
        coverage_amount=900_000,
        stated_claims=1,
        notes="Coastal property, one water claim",
    ),
)
