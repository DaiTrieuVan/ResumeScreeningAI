from app.models.recruiter_enums import UploadItemStatus
from app.services.upload_batch_service import (
    can_transition,
    contact_digest,
    content_digest,
    file_digest,
)


def test_upload_item_state_machine_blocks_invalid_jump():
    assert can_transition(UploadItemStatus.QUEUED.value, UploadItemStatus.VALIDATING.value)
    assert not can_transition(UploadItemStatus.QUEUED.value, UploadItemStatus.COMPLETED.value)
    assert can_transition(UploadItemStatus.FAILED.value, UploadItemStatus.QUEUED.value)


def test_dedupe_fingerprints_are_stable_after_normalization():
    assert file_digest(b"same") == file_digest(b"same")
    assert content_digest("Python   FastAPI") == content_digest(" python fastapi ")
    assert contact_digest(" Candidate@Example.com ", "+84 912-345-678") == contact_digest(
        "candidate@example.com", "84912345678"
    )


def test_missing_contact_does_not_create_false_shared_fingerprint():
    assert contact_digest(None, None) is None
