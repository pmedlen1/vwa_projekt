from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from starlette import status
from services.users import UsersService
from services.auth import User
from dependencies import get_conn, require_admin

router = APIRouter()

def users_service(conn=Depends(get_conn)):
    return UsersService(conn)

@router.get("/", name="users_ui")
async def users_ui(
    request: Request,
    svc: UsersService = Depends(users_service),
    user: User = Depends(require_admin), # Len ADMIN
):
    users_list = svc.get_all_users()
    return request.app.state.templates.TemplateResponse(
        "users.html",
        {"request": request, "users": users_list, "user": user},
    )

@router.get("/new", name="create_user_ui")
async def create_user_ui(
    request: Request,
    user: User = Depends(require_admin)
):
    return request.app.state.templates.TemplateResponse(
        "edit_user.html",
        {"request": request, "edit_user": None, "user": user, "errors": None}
    )

@router.post("/new", name="create_user_post")
async def create_user_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...), # Tu admin vyberie rolu
    first_name: str = Form(""),
    last_name: str = Form(""),
    position: str = Form(None),
    birth_date: str = Form(None),
    svc: UsersService = Depends(users_service),
    user: User = Depends(require_admin),
):
    try:
        svc.create_user(username, password, role, first_name, last_name, position, birth_date)
        return RedirectResponse(url=request.url_for("users_ui"), status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        return request.app.state.templates.TemplateResponse(
            "edit_user.html",
            {"request": request, "edit_user": None, "user": user, "errors": str(e)}
        )

@router.get("/edit/{user_id}", name="edit_user_ui")
async def edit_user_ui(
    request: Request,
    user_id: int,
    svc: UsersService = Depends(users_service),
    user: User = Depends(require_admin),
):
    user_to_edit = svc.get_user(user_id)
    if not user_to_edit:
        return RedirectResponse(url=request.url_for("users_ui"))

    return request.app.state.templates.TemplateResponse(
        "edit_user.html",
        {"request": request, "edit_user": user_to_edit, "user": user, "errors": None}
    )

@router.post("/edit/{user_id}", name="edit_user_post")
async def edit_user_post(
    request: Request,
    user_id: int,
    role: str = Form(...),
    first_name: str = Form(""),
    last_name: str = Form(""),
    position: str = Form(None),
    birth_date: str = Form(None),
    svc: UsersService = Depends(users_service),
    user: User = Depends(require_admin),
):
    svc.update_user(user_id, role, first_name, last_name, position, birth_date)
    return RedirectResponse(url=request.url_for("users_ui"), status_code=status.HTTP_303_SEE_OTHER)

@router.post("/delete/{user_id}", name="delete_user_post")
async def delete_user_post(
    request: Request,
    user_id: int,
    svc: UsersService = Depends(users_service),
    user: User = Depends(require_admin),
):
    # Ochrana: Admin by nemal zmazať sám seba
    if user.id == user_id:
         # Tu by sme mohli vypísať chybu, ale pre jednoduchosť len presmerujeme
         return RedirectResponse(url=request.url_for("users_ui"), status_code=status.HTTP_303_SEE_OTHER)

    svc.remove_user(user_id)
    return RedirectResponse(url=request.url_for("users_ui"), status_code=status.HTTP_303_SEE_OTHER)