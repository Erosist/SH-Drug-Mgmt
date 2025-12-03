from __future__ import annotations

from flask import current_app, request

from extensions import db
from models import AdminAuditLog


def _extract_request_ip() -> str:
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr or 'unknown'


def record_admin_action(
    admin,
    action: str,
    *,
    target_user_id: int | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    details: dict | None = None,
    commit: bool = False,
) -> None:
    """Persist a structured audit log for admin operations."""
    if not admin or not action:
        return

    log = AdminAuditLog(
        admin_id=admin.id,
        action=action,
        target_user_id=target_user_id,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id is not None else None,
        request_method=request.method,
        request_path=request.path,
        request_ip=_extract_request_ip(),
        details=details or {},
    )

    db.session.add(log)

    if commit:
        try:
            db.session.commit()
        except Exception as exc:  # pragma: no cover - safeguard
            db.session.rollback()
            current_app.logger.exception('Failed to commit admin audit log: %s', exc)
