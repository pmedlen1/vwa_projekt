from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from starlette import status
from services.trainings import TrainingsService
from services.auth import User
from dependencies import get_conn, get_current_user, require_admin_or_coach, require_user, trainings_service

router = APIRouter()


@router.get("/", name="trainings_ui")
async def trainings_ui(
    request: Request,
    svc: TrainingsService = Depends(trainings_service),
    user: Optional[User] = Depends(get_current_user),
):
    trainings = svc.get_all_trainings()

    # Pridanie informácie o účasti pre hráčov
    trainings_with_attendance = []
    if user and user.role == 'player':
        for t in trainings:
            t_copy = dict(t)
            t_copy['attendance_confirmed'] = svc.get_player_attendance(user.id, t['id'])
            trainings_with_attendance.append(t_copy)
    else:
        trainings_with_attendance = trainings

    return request.app.state.templates.TemplateResponse(
        "trainings.html",
        {"request": request, "trainings": trainings_with_attendance, "user": user},
    )

#                VYTVORENIE

@router.post("/new", name="create_training_post")
async def create_training_post(
    request: Request,
    location: str = Form(...),
    date: str = Form(...),
    description: str = Form(""),
    svc: TrainingsService = Depends(trainings_service),
    user: User = Depends(require_admin_or_coach),
):

    if not location.strip() or not date:
        trainings_list = svc.get_all_trainings()
        return request.app.state.templates.TemplateResponse(
            "trainings.html",
            {
                "request": request,
                "trainings": trainings_list,
                "user": user,
                "error": "Dátum a miesto sú povinné údaje."
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    svc.create_training(date, location, description)
    return RedirectResponse(url=request.url_for("trainings_ui"), status_code=status.HTTP_303_SEE_OTHER)

#           ÚPRAVA

@router.get("/edit/{training_id}", name="edit_training_ui")
async def edit_training_ui(
    request: Request,
    training_id: int,
    svc: TrainingsService = Depends(trainings_service),
    user: User = Depends(require_admin_or_coach),
):
    training = svc.get_training_by_id(training_id)
    if not training:
        return RedirectResponse(url=request.url_for("trainings_ui"))

    return request.app.state.templates.TemplateResponse(
        "edit_training.html",
        {"request": request, "training": training, "user": user}
    )

@router.post("/edit/{training_id}", name="edit_training_post")
async def edit_training_post(
    request: Request,
    training_id: int,
    location: str = Form(...),
    date: str = Form(...),
    description: str = Form(""),
    svc: TrainingsService = Depends(trainings_service),
    user: User = Depends(require_admin_or_coach),
):

    if not location.strip():
        training = svc.get_training(training_id)
        return request.app.state.templates.TemplateResponse(
            "edit_training.html",
            {
                "request": request,
                "training": training,
                "user": user,
                "error": "Miesto tréningu nesmie byť prázdne."
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    svc.edit_training(training_id, date, location, description)
    return RedirectResponse(url=request.url_for("trainings_ui"), status_code=status.HTTP_303_SEE_OTHER)

#           ZMAZANIE

@router.post("/delete/{training_id}", name="delete_training_post")
async def delete_training_post(
    request: Request,
    training_id: int,
    svc: TrainingsService = Depends(trainings_service),
    user: User = Depends(require_admin_or_coach),
):
    svc.remove_training(training_id)
    return RedirectResponse(url=request.url_for("trainings_ui"), status_code=status.HTTP_303_SEE_OTHER)

#           ÚČASŤ

@router.post("/attend/{training_id}", name="toggle_training_attendance_post")
async def toggle_training_attendance_post(
    request: Request,
    training_id: int,
    svc: TrainingsService = Depends(trainings_service),
    user: User = Depends(require_user),
):
    current_status = svc.get_player_attendance(user.id, training_id)
    svc.confirm_attendance(user.id, training_id, not current_status)
    return RedirectResponse(url=request.url_for("trainings_ui"), status_code=status.HTTP_303_SEE_OTHER)