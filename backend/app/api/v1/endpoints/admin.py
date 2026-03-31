from copy import deepcopy

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentAdmin, DBSession
from app.crud import crud_admin, crud_doc, crud_experiment, crud_user
from app.schemas.admin import (
    AdminAccountItem,
    AdminAccountPage,
    AdminAccountResetPasswordRequest,
    AdminAccountResetPasswordResponse,
    AdminAccountStatusUpdateResponse,
    AdminBatchResetPasswordRequest,
    AdminBatchStatusRequest,
    AdminBatchDeleteRequest,
    AdminUserBatchDeleteResponse,
    AdminUserBatchResetPasswordResponse,
    AdminUserBatchStatusUpdateResponse,
    AdminBatchDeleteFailedItem,
    AdminCreateAdminRequest,
    AdminCreateTeacherRequest,
    AdminOverviewRead,
    AdminResetPasswordRequest,
    AdminResetPasswordResponse,
    AdminSetUserRoleRequest,
    AdminUserItem,
    AdminUserDeleteResponse,
    AdminUserPage,
    AdminUserRoleUpdateResponse,
    AdminUserStatusUpdateResponse,
    AdminUpdateUserInfoRequest,
    AdminUpdateUserInfoResponse,
    AdminExperimentCreateRequest,
    AdminExperimentDeleteResponse,
    AdminExperimentItem,
    AdminExperimentPage,
    AdminExperimentStatusUpdateResponse,
    AdminExperimentUpdateRequest,
)
from app.schemas.doc import (
    AdminDocCreateRequest,
    AdminDocDeleteResponse,
    AdminDocItemRead,
    AdminDocUpdateRequest,
)

router = APIRouter(prefix="/admin", tags=["admin"])
ALLOWED_EXPERIMENT_INTERACTION_MODE = {"all", "native_editor", "guided_template"}
ALLOWED_EXPERIMENT_SORT_BY = {"updated_at", "created_at", "sort_order", "title", "slug", "open_at", "due_at"}
ALLOWED_EXPERIMENT_SORT_ORDER = {"asc", "desc"}


def _to_admin_experiment_item(item) -> AdminExperimentItem:
    return AdminExperimentItem(
        experiment_id=item.id,
        title=item.title,
        slug=item.slug,
        description=item.description,
        instruction_content=item.instruction_content,
        starter_code=item.starter_code,
        interaction_mode=item.interaction_mode,
        template_type=item.template_type,
        template_schema=item.template_schema,
        code_template=item.code_template,
        import_config=item.import_config,
        allow_edit_generated_code=bool(item.allow_edit_generated_code),
        sort_order=item.sort_order or 0,
        is_active=bool(item.is_active),
        is_published=bool(item.is_published),
        open_at=item.open_at,
        due_at=item.due_at,
        updated_at=item.updated_at,
        created_at=item.created_at,
    )


def _to_admin_doc_item(item) -> AdminDocItemRead:
    return AdminDocItemRead(
        id=item.id,
        title=item.title,
        slug=item.slug,
        content=item.content,
        summary=item.summary,
        category=item.category,
        sort_order=item.sort_order or 0,
        is_published=bool(item.is_published),
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _clean_doc_payload(payload: dict) -> dict:
    cleaned = payload.copy()
    if "title" in cleaned:
        value = (cleaned.get("title") or "").strip()
        if not value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="标题不能为空")
        cleaned["title"] = value
    if "slug" in cleaned:
        value = (cleaned.get("slug") or "").strip()
        if not value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="slug 不能为空")
        cleaned["slug"] = value
    if "content" in cleaned:
        value = (cleaned.get("content") or "").strip()
        if not value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="content 不能为空")
        cleaned["content"] = value
    if "summary" in cleaned and isinstance(cleaned.get("summary"), str):
        cleaned["summary"] = cleaned["summary"].strip() or None
    if "category" in cleaned:
        value = (cleaned.get("category") or "").strip()
        cleaned["category"] = value or "未分类"
    if "sort_order" in cleaned and cleaned.get("sort_order") is None:
        cleaned["sort_order"] = 0
    return cleaned


def _build_copied_experiment_slug(db: DBSession, source_slug: str) -> str:
    base_slug = f"{source_slug}-copy"
    candidate = base_slug
    suffix = 2
    while crud_experiment.get_by_slug(db, slug=candidate):
        candidate = f"{base_slug}-{suffix}"
        suffix += 1
    return candidate


@router.get("/overview", response_model=AdminOverviewRead)
def get_admin_overview(db: DBSession, admin_user: CurrentAdmin) -> AdminOverviewRead:
    _ = admin_user
    payload = crud_admin.get_overview_stats(db)
    return AdminOverviewRead.model_validate(payload)


@router.get("/docs", response_model=list[AdminDocItemRead])
def get_admin_docs(
    db: DBSession,
    admin_user: CurrentAdmin,
    keyword: str = Query(default=""),
    category: str = Query(default=""),
) -> list[AdminDocItemRead]:
    _ = admin_user
    items = crud_doc.list_admin_docs(db, keyword=keyword, category=category)
    return [_to_admin_doc_item(item) for item in items]


@router.get("/docs/categories", response_model=list[str])
def get_admin_doc_categories(
    db: DBSession,
    admin_user: CurrentAdmin,
) -> list[str]:
    _ = admin_user
    return crud_doc.list_admin_categories(db)


@router.post("/docs", response_model=AdminDocItemRead, status_code=status.HTTP_201_CREATED)
def create_admin_doc(
    payload: AdminDocCreateRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminDocItemRead:
    _ = admin_user
    create_payload = _clean_doc_payload(payload.model_dump())
    existed = crud_doc.get_by_slug(db, slug=create_payload["slug"])
    if existed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="slug 已存在")
    created = crud_doc.create_doc(db, payload=create_payload)
    return _to_admin_doc_item(created)


@router.put("/docs/{doc_id}", response_model=AdminDocItemRead)
def update_admin_doc(
    doc_id: int,
    payload: AdminDocUpdateRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminDocItemRead:
    _ = admin_user
    doc = crud_doc.get_by_id(db, doc_id=doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")
    update_payload = payload.model_dump(exclude_unset=True)
    cleaned_payload = _clean_doc_payload(update_payload)
    if "slug" in cleaned_payload:
        existed = crud_doc.get_by_slug_excluding_id(db, slug=cleaned_payload["slug"], exclude_id=doc_id)
        if existed:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="slug 已存在")
    updated = crud_doc.update_doc(db, doc=doc, payload=cleaned_payload)
    return _to_admin_doc_item(updated)


@router.delete("/docs/{doc_id}", response_model=AdminDocDeleteResponse)
def delete_admin_doc(
    doc_id: int,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminDocDeleteResponse:
    _ = admin_user
    doc = crud_doc.get_by_id(db, doc_id=doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")
    crud_doc.delete_doc(db, doc=doc)
    return AdminDocDeleteResponse(id=doc_id, message="文档删除成功")


@router.get("/experiments", response_model=AdminExperimentPage)
def get_admin_experiments(
    db: DBSession,
    admin_user: CurrentAdmin,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
    interaction_mode: str = Query(default="all"),
    is_active: bool | None = Query(default=None),
    is_published: bool | None = Query(default=None),
    sort_by: str = Query(default="sort_order"),
    sort_order: str = Query(default="asc"),
) -> AdminExperimentPage:
    _ = admin_user
    if interaction_mode not in ALLOWED_EXPERIMENT_INTERACTION_MODE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="interaction_mode 参数仅支持 all/native_editor/guided_template")
    if sort_by not in ALLOWED_EXPERIMENT_SORT_BY:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="sort_by 参数不支持")
    if sort_order not in ALLOWED_EXPERIMENT_SORT_ORDER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="sort_order 参数仅支持 asc/desc")
    data = crud_experiment.list_admin_experiments(
        db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        interaction_mode=interaction_mode,
        is_active=is_active,
        is_published=is_published,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return AdminExperimentPage(
        items=[_to_admin_experiment_item(item) for item in data["items"]],
        total=data["total"],
        page=data["page"],
        page_size=data["page_size"],
        total_pages=data["total_pages"],
    )


@router.post("/experiments", response_model=AdminExperimentItem, status_code=status.HTTP_201_CREATED)
def create_admin_experiment(
    payload: AdminExperimentCreateRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminExperimentItem:
    _ = admin_user
    clean_title = payload.title.strip()
    if not clean_title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="标题不能为空")
    clean_slug = payload.slug.strip()
    if not clean_slug:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="slug 不能为空")
    if payload.open_at and payload.due_at and payload.due_at <= payload.open_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="截止时间必须晚于开放时间")
    existed = crud_experiment.get_by_slug(db, slug=clean_slug)
    if existed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="slug 已存在")
    create_payload = payload.model_dump()
    create_payload["slug"] = clean_slug
    create_payload["title"] = clean_title
    if isinstance(payload.description, str):
        create_payload["description"] = payload.description.strip() or None
    if isinstance(payload.instruction_content, str):
        create_payload["instruction_content"] = payload.instruction_content.strip() or None
    if isinstance(payload.starter_code, str):
        create_payload["starter_code"] = payload.starter_code
    if isinstance(payload.template_type, str):
        create_payload["template_type"] = payload.template_type.strip() or None
    if isinstance(payload.code_template, str):
        create_payload["code_template"] = payload.code_template or None
    created = crud_experiment.create_admin_experiment(db, create_payload)
    return _to_admin_experiment_item(created)


@router.get("/experiments/{experiment_id}", response_model=AdminExperimentItem)
def get_admin_experiment_detail(
    experiment_id: int,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminExperimentItem:
    _ = admin_user
    experiment = crud_experiment.get(db, experiment_id=experiment_id)
    if not experiment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="实验不存在")
    return _to_admin_experiment_item(experiment)


@router.put("/experiments/{experiment_id}", response_model=AdminExperimentItem)
def update_admin_experiment(
    experiment_id: int,
    payload: AdminExperimentUpdateRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminExperimentItem:
    _ = admin_user
    experiment = crud_experiment.get(db, experiment_id=experiment_id)
    if not experiment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="实验不存在")
    update_payload = payload.model_dump(exclude_unset=True)
    if "slug" in update_payload:
        clean_slug = (update_payload.get("slug") or "").strip()
        if not clean_slug:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="slug 不能为空")
        existed = crud_experiment.get_by_slug_excluding_id(db, slug=clean_slug, exclude_id=experiment_id)
        if existed:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="slug 已存在")
        update_payload["slug"] = clean_slug
    if "title" in update_payload:
        clean_title = (update_payload.get("title") or "").strip()
        if not clean_title:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="标题不能为空")
        update_payload["title"] = clean_title
    if "description" in update_payload and isinstance(update_payload.get("description"), str):
        update_payload["description"] = update_payload["description"].strip() or None
    if "instruction_content" in update_payload and isinstance(update_payload.get("instruction_content"), str):
        update_payload["instruction_content"] = update_payload["instruction_content"].strip() or None
    if "template_type" in update_payload and isinstance(update_payload.get("template_type"), str):
        update_payload["template_type"] = update_payload["template_type"].strip() or None
    if "code_template" in update_payload and isinstance(update_payload.get("code_template"), str):
        update_payload["code_template"] = update_payload["code_template"] or None
    open_at = update_payload.get("open_at", experiment.open_at)
    due_at = update_payload.get("due_at", experiment.due_at)
    if open_at and due_at and due_at <= open_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="截止时间必须晚于开放时间")
    updated = crud_experiment.update_admin_experiment(db, experiment=experiment, payload=update_payload)
    return _to_admin_experiment_item(updated)


@router.post("/experiments/{experiment_id}/enable", response_model=AdminExperimentStatusUpdateResponse)
def enable_admin_experiment(
    experiment_id: int,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminExperimentStatusUpdateResponse:
    _ = admin_user
    experiment = crud_experiment.get(db, experiment_id=experiment_id)
    if not experiment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="实验不存在")
    updated = crud_experiment.update_admin_experiment(db, experiment=experiment, payload={"is_active": True})
    return AdminExperimentStatusUpdateResponse(experiment_id=updated.id, is_active=bool(updated.is_active), message="实验已启用")


@router.post("/experiments/{experiment_id}/disable", response_model=AdminExperimentStatusUpdateResponse)
def disable_admin_experiment(
    experiment_id: int,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminExperimentStatusUpdateResponse:
    _ = admin_user
    experiment = crud_experiment.get(db, experiment_id=experiment_id)
    if not experiment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="实验不存在")
    updated = crud_experiment.update_admin_experiment(db, experiment=experiment, payload={"is_active": False})
    return AdminExperimentStatusUpdateResponse(experiment_id=updated.id, is_active=bool(updated.is_active), message="实验已停用")


@router.post("/experiments/{experiment_id}/copy", response_model=AdminExperimentItem, status_code=status.HTTP_201_CREATED)
def copy_admin_experiment(
    experiment_id: int,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminExperimentItem:
    _ = admin_user
    source = crud_experiment.get(db, experiment_id=experiment_id)
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="实验不存在")

    copied_slug = _build_copied_experiment_slug(db, source.slug)
    copied_payload = {
        "title": f"{source.title}（副本）",
        "slug": copied_slug,
        "description": source.description,
        "instruction_content": source.instruction_content,
        "starter_code": source.starter_code,
        "interaction_mode": source.interaction_mode,
        "template_type": source.template_type,
        "template_schema": deepcopy(source.template_schema) if source.template_schema is not None else None,
        "code_template": source.code_template,
        "import_config": deepcopy(source.import_config) if source.import_config is not None else None,
        "allow_edit_generated_code": bool(source.allow_edit_generated_code),
        "sort_order": source.sort_order or 0,
        "is_active": bool(source.is_active),
        "is_published": False,
        "open_at": source.open_at,
        "due_at": source.due_at,
    }
    created = crud_experiment.create_admin_experiment(db, copied_payload)
    return _to_admin_experiment_item(created)


@router.delete("/experiments/{experiment_id}", response_model=AdminExperimentDeleteResponse)
def delete_admin_experiment(
    experiment_id: int,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminExperimentDeleteResponse:
    _ = admin_user
    experiment = crud_experiment.get(db, experiment_id=experiment_id)
    if not experiment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="实验不存在")
    crud_experiment.delete_admin_experiment(db, experiment=experiment)
    return AdminExperimentDeleteResponse(experiment_id=experiment_id, message="实验删除成功")


@router.get("/admin-users", response_model=AdminAccountPage)
def get_admin_accounts(
    db: DBSession,
    admin_user: CurrentAdmin,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
    is_enabled: bool | None = Query(default=None),
) -> AdminAccountPage:
    _ = admin_user
    data = crud_admin.list_admin_accounts(
        db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        is_enabled=is_enabled,
    )
    return AdminAccountPage(
        items=[AdminAccountItem.model_validate(item) for item in data["items"]],
        total=data["total"],
        page=data["page"],
        page_size=data["page_size"],
        total_pages=data["total_pages"],
    )


@router.post("/admin-users", response_model=AdminAccountItem, status_code=status.HTTP_201_CREATED)
def create_admin_account(
    payload: AdminCreateAdminRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminAccountItem:
    _ = admin_user
    username = payload.username.strip()
    if not username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名不能为空")
    existed = crud_user.get_by_username(db, username=username)
    if existed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    try:
        created = crud_admin.create_admin_account(
            db,
            username=username,
            full_name=payload.full_name,
            password=payload.password,
        )
    except IntegrityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在") from exc
    return AdminAccountItem(
        user_id=created.id,
        username=created.username,
        full_name=created.full_name,
        role=created.role,
        is_enabled=created.is_enabled,
        must_change_password=bool(created.must_change_password),
        created_at=created.created_at,
    )


@router.post("/admin-users/{user_id}/enable", response_model=AdminAccountStatusUpdateResponse)
def enable_admin_account(
    user_id: int,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminAccountStatusUpdateResponse:
    user, error_message = crud_admin.set_admin_account_enabled(
        db,
        target_user_id=user_id,
        is_enabled=True,
        acting_admin_id=admin_user.id,
    )
    if not user:
        if error_message == "用户不存在":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message or "操作失败")
    return AdminAccountStatusUpdateResponse(user_id=user.id, is_enabled=user.is_enabled, message="管理员账号已启用")


@router.post("/admin-users/{user_id}/disable", response_model=AdminAccountStatusUpdateResponse)
def disable_admin_account(
    user_id: int,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminAccountStatusUpdateResponse:
    user, error_message = crud_admin.set_admin_account_enabled(
        db,
        target_user_id=user_id,
        is_enabled=False,
        acting_admin_id=admin_user.id,
    )
    if not user:
        if error_message == "用户不存在":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message or "操作失败")
    return AdminAccountStatusUpdateResponse(user_id=user.id, is_enabled=user.is_enabled, message="管理员账号已停用")


@router.post("/admin-users/{user_id}/reset-password", response_model=AdminAccountResetPasswordResponse)
def reset_admin_account_password(
    user_id: int,
    payload: AdminAccountResetPasswordRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminAccountResetPasswordResponse:
    _ = admin_user
    cleaned_password = payload.new_password.strip()
    if len(cleaned_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="新密码长度不能少于 6 位")
    user, error_message = crud_admin.reset_admin_account_password(
        db,
        target_user_id=user_id,
        new_password=cleaned_password,
    )
    if not user:
        if error_message == "用户不存在":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message or "操作失败")
    return AdminAccountResetPasswordResponse(
        user_id=user.id,
        must_change_password=bool(user.must_change_password),
        message="管理员密码重置成功",
    )


@router.get("/users", response_model=AdminUserPage)
def get_admin_users(
    db: DBSession,
    admin_user: CurrentAdmin,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
    role_filter: str = Query(default="all", alias="role"),
    class_name: str = Query(default=""),
    is_enabled: bool | None = Query(default=None),
) -> AdminUserPage:
    _ = admin_user
    if role_filter not in {"all", "student", "teacher", "admin"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="role 参数仅支持 all/student/teacher/admin")
    data = crud_admin.list_users(
        db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        role_filter=role_filter,
        class_name=class_name,
        is_enabled=is_enabled,
    )
    return AdminUserPage(
        items=[AdminUserItem.model_validate(item) for item in data["items"]],
        total=data["total"],
        page=data["page"],
        page_size=data["page_size"],
        total_pages=data["total_pages"],
    )


@router.get("/users/class-options", response_model=list[str])
def get_admin_user_class_options(
    db: DBSession,
    admin_user: CurrentAdmin,
) -> list[str]:
    _ = admin_user
    return crud_admin.list_user_class_options(db)


@router.post("/teachers", response_model=AdminUserItem, status_code=status.HTTP_201_CREATED)
def create_admin_teacher(
    payload: AdminCreateTeacherRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminUserItem:
    _ = admin_user
    username = payload.username.strip()
    if not username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名不能为空")
    existed = crud_user.get_by_username(db, username=username)
    if existed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    try:
        created = crud_admin.create_teacher(
            db,
            username=username,
            full_name=payload.full_name,
            password=payload.password,
        )
    except IntegrityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在") from exc
    return AdminUserItem(
        user_id=created.id,
        username=created.username,
        full_name=created.full_name,
        role=created.role,
        student_no=created.student_no,
        class_name=created.class_name,
        is_enabled=created.is_enabled,
        created_at=created.created_at,
    )


@router.post("/users/{user_id}/enable", response_model=AdminUserStatusUpdateResponse)
def enable_admin_user(
    user_id: int,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminUserStatusUpdateResponse:
    user, error_message = crud_admin.set_user_enabled(
        db,
        target_user_id=user_id,
        is_enabled=True,
        acting_admin_id=admin_user.id,
    )
    if not user:
        if error_message == "用户不存在":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message or "操作失败")
    return AdminUserStatusUpdateResponse(user_id=user.id, is_enabled=user.is_enabled, message="账号已启用")


@router.post("/users/{user_id}/disable", response_model=AdminUserStatusUpdateResponse)
def disable_admin_user(
    user_id: int,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminUserStatusUpdateResponse:
    user, error_message = crud_admin.set_user_enabled(
        db,
        target_user_id=user_id,
        is_enabled=False,
        acting_admin_id=admin_user.id,
    )
    if not user:
        if error_message == "用户不存在":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message or "操作失败")
    return AdminUserStatusUpdateResponse(user_id=user.id, is_enabled=user.is_enabled, message="账号已停用")


@router.post("/users/{user_id}/reset-password", response_model=AdminResetPasswordResponse)
def reset_admin_user_password(
    user_id: int,
    payload: AdminResetPasswordRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminResetPasswordResponse:
    _ = admin_user
    cleaned_password = payload.new_password.strip()
    if len(cleaned_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="新密码长度不能少于 6 位")
    user, error_message = crud_admin.reset_user_password(
        db,
        target_user_id=user_id,
        new_password=cleaned_password,
    )
    if not user:
        if error_message == "用户不存在":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message or "操作失败")
    return AdminResetPasswordResponse(
        user_id=user.id,
        must_change_password=bool(user.must_change_password),
        message="密码重置成功",
    )


@router.post("/users/{user_id}/set-role", response_model=AdminUserRoleUpdateResponse)
def set_admin_user_role(
    user_id: int,
    payload: AdminSetUserRoleRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminUserRoleUpdateResponse:
    user, error_message = crud_admin.set_user_role(
        db,
        target_user_id=user_id,
        target_role=payload.role,
        acting_admin_id=admin_user.id,
    )
    if not user:
        if error_message == "用户不存在":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message or "操作失败")
    return AdminUserRoleUpdateResponse(user_id=user.id, role=user.role, message="角色设置成功")


@router.post("/users/{user_id}/update-info", response_model=AdminUpdateUserInfoResponse)
def update_admin_user_info(
    user_id: int,
    payload: AdminUpdateUserInfoRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminUpdateUserInfoResponse:
    _ = admin_user
    user, error_message = crud_admin.update_user_basic_info(
        db,
        target_user_id=user_id,
        username=payload.username,
        full_name=payload.full_name,
    )
    if not user:
        if error_message == "用户不存在":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message or "操作失败")
    return AdminUpdateUserInfoResponse(
        message="用户信息更新成功",
        user=AdminUserItem(
            user_id=user.id,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            student_no=user.student_no,
            class_name=user.class_name,
            is_enabled=user.is_enabled,
            created_at=user.created_at,
        ),
    )


@router.post("/users/{user_id}/delete", response_model=AdminUserDeleteResponse)
def delete_admin_user(
    user_id: int,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminUserDeleteResponse:
    success, error_message = crud_admin.delete_user(
        db,
        target_user_id=user_id,
        acting_admin_id=admin_user.id,
    )
    if not success:
        if error_message == "用户不存在":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message or "删除失败")
    return AdminUserDeleteResponse(user_id=user_id, message="账号删除成功")


@router.post("/users/batch-delete", response_model=AdminUserBatchDeleteResponse)
def batch_delete_admin_users(
    payload: AdminBatchDeleteRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminUserBatchDeleteResponse:
    success_user_ids, failed_items = crud_admin.batch_delete_users(
        db,
        user_ids=payload.user_ids,
        acting_admin_id=admin_user.id,
    )
    return AdminUserBatchDeleteResponse(
        success_count=len(success_user_ids),
        failed_count=len(failed_items),
        success_user_ids=success_user_ids,
        failed_items=[AdminBatchDeleteFailedItem.model_validate(item) for item in failed_items],
        message="批量删除完成",
    )


@router.post("/users/batch-enable", response_model=AdminUserBatchStatusUpdateResponse)
def batch_enable_admin_users(
    payload: AdminBatchStatusRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminUserBatchStatusUpdateResponse:
    success_user_ids, failed_items = crud_admin.batch_set_users_enabled(
        db,
        user_ids=payload.user_ids,
        target_enabled=True,
        acting_admin_id=admin_user.id,
    )
    return AdminUserBatchStatusUpdateResponse(
        success_count=len(success_user_ids),
        failed_count=len(failed_items),
        success_user_ids=success_user_ids,
        failed_items=[AdminBatchDeleteFailedItem.model_validate(item) for item in failed_items],
        message="批量启用完成",
    )


@router.post("/users/batch-disable", response_model=AdminUserBatchStatusUpdateResponse)
def batch_disable_admin_users(
    payload: AdminBatchStatusRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminUserBatchStatusUpdateResponse:
    success_user_ids, failed_items = crud_admin.batch_set_users_enabled(
        db,
        user_ids=payload.user_ids,
        target_enabled=False,
        acting_admin_id=admin_user.id,
    )
    return AdminUserBatchStatusUpdateResponse(
        success_count=len(success_user_ids),
        failed_count=len(failed_items),
        success_user_ids=success_user_ids,
        failed_items=[AdminBatchDeleteFailedItem.model_validate(item) for item in failed_items],
        message="批量停用完成",
    )


@router.post("/users/batch-reset-password", response_model=AdminUserBatchResetPasswordResponse)
def batch_reset_admin_users_password(
    payload: AdminBatchResetPasswordRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminUserBatchResetPasswordResponse:
    _ = admin_user
    new_password = payload.new_password.strip()
    if len(new_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="新密码长度不能少于 6 位")
    success_user_ids, failed_items = crud_admin.batch_reset_users_password(
        db,
        user_ids=payload.user_ids,
        new_password=new_password,
    )
    return AdminUserBatchResetPasswordResponse(
        success_count=len(success_user_ids),
        failed_count=len(failed_items),
        success_user_ids=success_user_ids,
        failed_items=[AdminBatchDeleteFailedItem.model_validate(item) for item in failed_items],
        message="批量重置密码完成",
    )
