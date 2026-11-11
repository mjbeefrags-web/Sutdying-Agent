from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.app.core.errors import AppError
from apps.api.app.core.rate_limit import enforce_rate_limit
from apps.api.app.db.models import AuditEvent, Course, Membership, Organization, User
from apps.api.app.db.session import get_db
from apps.api.app.domains.courses.schemas import (
    CourseCreate,
    CoursePatch,
    CourseRead,
    OrganizationRead,
)
from apps.api.app.domains.identity.dependencies import get_current_user, require_csrf

router = APIRouter(tags=["courses"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
Csrf = Annotated[None, Depends(require_csrf)]


def _organization_for_user(db: Session, organization_id: UUID, user_id: UUID) -> Organization:
    organization = db.scalar(
        select(Organization)
        .join(Membership, Membership.organization_id == Organization.id)
        .where(Organization.id == organization_id, Membership.user_id == user_id)
    )
    if organization is None:
        raise AppError(404, "not_found", "The requested resource was not found.")
    return organization


def _course_for_user(db: Session, course_id: UUID, user_id: UUID) -> Course:
    course = db.scalar(
        select(Course)
        .join(Membership, Membership.organization_id == Course.organization_id)
        .where(Course.id == course_id, Membership.user_id == user_id)
    )
    if course is None:
        raise AppError(404, "not_found", "The requested resource was not found.")
    return course


def _audit(
    db: Session,
    request: Request,
    action: str,
    course: Course,
    user: User,
) -> None:
    db.add(
        AuditEvent(
            actor_user_id=user.id,
            organization_id=course.organization_id,
            action=action,
            resource_type="course",
            resource_id=str(course.id),
            request_id=getattr(request.state, "request_id", ""),
            metadata_json={},
        )
    )


@router.get("/organizations", response_model=list[OrganizationRead])
def list_organizations(db: DbSession, user: CurrentUser) -> list[Organization]:
    return list(
        db.scalars(
            select(Organization)
            .join(Membership, Membership.organization_id == Organization.id)
            .where(Membership.user_id == user.id)
            .order_by(Organization.created_at)
        )
    )


@router.get("/organizations/{organization_id}/courses", response_model=list[CourseRead])
def list_courses(organization_id: UUID, db: DbSession, user: CurrentUser) -> list[Course]:
    _organization_for_user(db, organization_id, user.id)
    return list(
        db.scalars(
            select(Course)
            .where(
                Course.organization_id == organization_id,
                Course.archived_at.is_(None),
            )
            .order_by(Course.created_at.desc(), Course.id)
        )
    )


@router.post(
    "/organizations/{organization_id}/courses",
    response_model=CourseRead,
    status_code=status.HTTP_201_CREATED,
)
def create_course(
    organization_id: UUID,
    payload: CourseCreate,
    request: Request,
    db: DbSession,
    user: CurrentUser,
    _csrf: Csrf,
) -> Course:
    _organization_for_user(db, organization_id, user.id)
    enforce_rate_limit("courses:create", str(user.id), 50, 60 * 60)
    course = Course(
        organization_id=organization_id,
        created_by_user_id=user.id,
        name=payload.name.strip(),
        description=payload.description.strip() if payload.description else None,
    )
    if not course.name:
        raise AppError(422, "invalid_course_name", "Course name cannot be empty.")
    db.add(course)
    db.flush()
    _audit(db, request, "course.created", course, user)
    db.commit()
    db.refresh(course)
    return course


@router.get("/courses", response_model=list[CourseRead])
def list_all_courses(db: DbSession, user: CurrentUser) -> list[Course]:
    organization_ids = select(Membership.organization_id).where(Membership.user_id == user.id)
    return list(
        db.scalars(
            select(Course)
            .where(
                Course.organization_id.in_(organization_ids),
                Course.archived_at.is_(None),
            )
            .order_by(Course.created_at.desc(), Course.id)
        )
    )


@router.get("/courses/{course_id}", response_model=CourseRead)
def get_course(course_id: UUID, db: DbSession, user: CurrentUser) -> Course:
    return _course_for_user(db, course_id, user.id)


@router.patch("/courses/{course_id}", response_model=CourseRead)
def update_course(
    course_id: UUID,
    payload: CoursePatch,
    request: Request,
    db: DbSession,
    user: CurrentUser,
    _csrf: Csrf,
) -> Course:
    course = _course_for_user(db, course_id, user.id)
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise AppError(422, "empty_update", "Provide at least one course field.")
    if "name" in changes:
        if changes["name"] is None or not changes["name"].strip():
            raise AppError(422, "invalid_course_name", "Course name cannot be empty.")
        course.name = changes["name"].strip()
    if "description" in changes:
        course.description = (
            changes["description"].strip() if changes["description"] is not None else None
        )
    if "archived" in changes:
        if changes["archived"] is None:
            raise AppError(422, "invalid_archived_state", "Archived must be true or false.")
        course.archived_at = datetime.now(UTC) if changes["archived"] else None
    course.updated_at = datetime.now(UTC)
    _audit(db, request, "course.updated", course, user)
    db.commit()
    db.refresh(course)
    return course


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_course(
    course_id: UUID,
    request: Request,
    db: DbSession,
    user: CurrentUser,
    _csrf: Csrf,
) -> Response:
    course = _course_for_user(db, course_id, user.id)
    if course.archived_at is None:
        course.archived_at = datetime.now(UTC)
        course.updated_at = datetime.now(UTC)
        _audit(db, request, "course.archived", course, user)
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
