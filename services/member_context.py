"""
=============================================================================
FITNESS BUDDY – MEMBER CONTEXT HELPER
=============================================================================
Single source of truth for "which profile is currently active".

All routes call get_active_member() instead of using current_user directly
for data queries, so the same dashboard/chat/analytics code serves every
family profile without duplication.
=============================================================================
"""

from flask import session
from flask_login import current_user
from models.models import User


def get_active_member() -> User:
    """
    Return the currently active family member profile.

    The active member is stored in session["active_member_id"].
    It must belong to current_user (either current_user themselves, or a
    family member whose parent_id == current_user.id).

    Falls back to current_user if nothing is stored or the stored id is
    no longer valid.
    """
    mid = session.get("active_member_id")
    if mid and mid != current_user.id:
        member = User.query.filter_by(
            id=mid, parent_id=current_user.id
        ).first()
        if member:
            return member
    return current_user


def get_family_roster() -> list[User]:
    """
    Return [current_user] + all family members owned by current_user,
    for use in the profile selector dropdown.
    """
    members = User.query.filter_by(parent_id=current_user.id).all()
    return [current_user] + members


def set_active_member(member_id: int) -> bool:
    """
    Set the active member in session.  Returns True on success.
    Validates ownership before accepting.
    """
    if member_id == current_user.id:
        session["active_member_id"] = current_user.id
        return True
    member = User.query.filter_by(
        id=member_id, parent_id=current_user.id
    ).first()
    if member:
        session["active_member_id"] = member_id
        return True
    return False
