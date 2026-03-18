from pathlib import Path

from sentinel.application.safety.approval_service import ApprovalService
from sentinel.infrastructure.persistence.db import DatabaseManager
from sentinel.infrastructure.persistence.repositories.approval_repository import SQLiteApprovalRepository
from sentinel.shared.time import Clock


def test_approval_lifecycle_exact_match_and_status_update(tmp_path: Path) -> None:
    db = DatabaseManager(tmp_path / "sentinel.db")
    db.initialize()
    repo = SQLiteApprovalRepository(db)
    service = ApprovalService(repo, Clock(), ttl_seconds=300)

    approval = service.create_pending("sess_1", "filesystem.writer", {"path": "/tmp/a", "content": "x"}, "preview")
    assert repo.get_by_token(approval.token) is not None

    updated = service.approve(approval.token)
    assert updated is not None
    assert updated.status.value == "approved"

    assert service.is_preapproved("sess_1", "filesystem.writer", {"path": "/tmp/a", "content": "x"}) is True
