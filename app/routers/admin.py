from fastapi import APIRouter
from fastapi import Request
from fastapi import Depends
from fastapi import Form
from app.models.site_content import SiteContent
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.review import Review
from app.core.database import get_db
from app.models.vip_prediction import VipPrediction
from app.models.stat import Stat
from app.models.setting import Setting
import os
import shutil
from uuid import uuid4

from fastapi import UploadFile
from fastapi import File
COOKIE_NAME = "admin_session"

ADMIN_LOGIN = "pokusai228"
ADMIN_PASSWORD = "pokusaikyrylo911"
UPLOAD_DIR = "app/static/uploads"


def save_upload(file: UploadFile):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return f"/static/uploads/{filename}"
def datetime_value(value):
    if value:
        return value.strftime("%Y-%m-%dT%H:%M")

    return datetime.now().strftime("%Y-%m-%dT%H:%M")
router = APIRouter(prefix="/admin")

templates = Jinja2Templates(
    directory="app/templates"
)


def check_auth(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    return token == "logged"


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin/login.html",
        context={}
    )
@router.get("/content")
def content_page(
    request: Request,
    db: Session = Depends(get_db)
):
    if not check_auth(request):
        return RedirectResponse(
            "/admin/login",
            status_code=303
        )

    content = db.query(SiteContent).first()

    return templates.TemplateResponse(
        request=request,
        name="admin/content.html",
        context={
            "content": content
        }
    )

@router.post("/content")
def save_content(
    request: Request,
    about_text: str = Form(...),
    predictions: str = Form(...),
    win_rate: str = Form(...),
    roi: str = Form(...),
    members: str = Form(...),
    db: Session = Depends(get_db)
):
    if not check_auth(request):
        return RedirectResponse(
            "/admin/login",
            status_code=303
        )

    content = db.query(SiteContent).first()

    if content is None:

        content = SiteContent(
            about_text=about_text,
            predictions=predictions,
            win_rate=win_rate,
            roi=roi,
            members=members
        )

        db.add(content)

    else:

        content.about_text = about_text
        content.predictions = predictions
        content.win_rate = win_rate
        content.roi = roi
        content.members = members

    db.commit()

    return RedirectResponse(
        "/admin/content",
        status_code=303
    )

@router.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...)
):
    if username != ADMIN_LOGIN:
        return RedirectResponse(
            "/admin/login",
            status_code=303
        )

    if password != ADMIN_PASSWORD:
        return RedirectResponse(
            "/admin/login",
            status_code=303
        )

    response = RedirectResponse(
        "/admin/stats",
        status_code=303
    )

    response.set_cookie(
        key=COOKIE_NAME,
        value="logged",
        httponly=True,
        max_age=86400
    )

    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(
        "/admin/login",
        status_code=303
    )

    response.delete_cookie(COOKIE_NAME)

    return response


@router.get("/stats")
def stats_list(
    request: Request,
    db: Session = Depends(get_db)
):
    if not check_auth(request):
        return RedirectResponse(
            "/admin/login",
            status_code=303
        )

    stats = db.query(Stat).all()

    return templates.TemplateResponse(
        request=request,
        name="admin/stats_list.html",
        context={
            "stats": stats
        }
    )


@router.get("/stats/create")
def create_form(
    request: Request
):
    if not check_auth(request):
        return RedirectResponse(
            "/admin/login",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="admin/stat_form.html",
        context={
            "stat": None,
            "today": datetime.now().strftime("%Y-%m-%d")
        }
    )

@router.post("/stats/create")
def create_stat(
    request: Request,
    category: str = Form(...),
    match_date: str = Form(...),
    sport: str = Form(...),
    event: str = Form(...),
    prediction: str = Form(...),
    odds: str = Form(...),
    result: str = Form(...),
    db: Session = Depends(get_db)
):
    if not check_auth(request):
        return RedirectResponse(
            "/admin/login",
            status_code=303
        )

    stat = Stat(
        category=category,
        match_date=datetime.strptime(match_date, "%Y-%m-%d").date(),
        sport=sport,
        event=event,
        prediction=prediction,
        odds=odds,
        result=result
    )

    db.add(stat)
    db.commit()

    return RedirectResponse(
        "/admin/stats",
        status_code=303
    )
@router.get("/stats/edit/{stat_id}")
def edit_form(
    stat_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    if not check_auth(request):
        return RedirectResponse(
            "/admin/login",
            status_code=303
        )

    stat = db.get(Stat, stat_id)
    if stat is None:
        return RedirectResponse("/admin/stats", status_code=303)


    return templates.TemplateResponse(
        request=request,
        name="admin/stat_form.html",
        context={
            "stat": stat
        }
    )


@router.post("/stats/edit/{stat_id}")
def edit_stat(
    stat_id: int,
    request: Request,
    name: str = Form(...),
    total: int = Form(...),
    wins: int = Form(...),
    losses: int = Form(...),
    roi: str = Form(...),
    db: Session = Depends(get_db)
):
    if not check_auth(request):
        return RedirectResponse(
            "/admin/login",
            status_code=303
        )

    stat = db.get(Stat, stat_id)
    if stat is None:
        return RedirectResponse("/admin/stats", status_code=303)
    if wins + losses > total:
        return RedirectResponse(f"/admin/stats/edit/{stat_id}", status_code=303)

    stat.name = name
    stat.total = total
    stat.wins = wins
    stat.losses = losses
    stat.roi = roi

    db.commit()

    return RedirectResponse(
        "/admin/stats",
        status_code=303
    )


@router.post("/stats/delete/{stat_id}")
def delete_stat(
    stat_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    if not check_auth(request):
        return RedirectResponse("/admin/login", status_code=303)

    stat = db.get(Stat, stat_id)

    if stat:
        db.delete(stat)
        db.commit()

    return RedirectResponse("/admin/stats", status_code=303)


@router.get("/settings")
def settings_page(
    request: Request,
    db: Session = Depends(get_db)
):
    if not check_auth(request):
        return RedirectResponse(
            "/admin/login",
            status_code=303
        )

    setting = db.query(Setting).first()

    return templates.TemplateResponse(
        request=request,
        name="admin/settings.html",
        context={
            "setting": setting
        }
    )


@router.post("/settings")
def save_settings(
    request: Request,
    telegram_url: str = Form(...),
    db: Session = Depends(get_db)
):
    if not check_auth(request):
        return RedirectResponse(
            "/admin/login",
            status_code=303
        )

    setting = db.query(Setting).first()

    if setting is None:
        setting = Setting(
            telegram_url=telegram_url
        )
        db.add(setting)
    else:
        setting.telegram_url = telegram_url

    db.commit()

    return RedirectResponse(
        "/admin/settings",
        status_code=303
    )

@router.get("/reviews")
def reviews_list(
    request: Request,
    db: Session = Depends(get_db)
):
    if not check_auth(request):
        return RedirectResponse(
            "/admin/login",
            status_code=303
        )

    reviews = (
        db.query(Review)
        .order_by(Review.id.desc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="admin/reviews_list.html",
        context={
            "reviews": reviews
        }
    )


@router.get("/reviews/create")
def review_create_form(
    request: Request
):
    if not check_auth(request):
        return RedirectResponse("/admin/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="admin/review_form.html",
        context={
            "review": None,
            "published_at_value": datetime.now().strftime("%Y-%m-%dT%H:%M")
        }
    )

@router.post("/reviews/create")
def review_create(
    request: Request,
    avatar: UploadFile = File(...),
    author: str = Form(...),
    text: str = Form(...),
    rating: int = Form(...),
    published_at: str = Form(""),
    db: Session = Depends(get_db)
):
    if not check_auth(request):
        return RedirectResponse(
            "/admin/login",
            status_code=303
        )

    final_date = datetime.now()

    if published_at:
        final_date = datetime.fromisoformat(published_at)

    avatar_path = save_upload(avatar)

    review = Review(
        avatar=avatar_path,
        author=author,
        text=text,
        rating=rating,
        published_at=final_date
    )

    db.add(review)
    db.commit()

    return RedirectResponse(
        "/admin/reviews",
        status_code=303
    )


@router.get("/reviews/edit/{review_id}")
def review_edit_form(
    review_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    if not check_auth(request):
        return RedirectResponse("/admin/login", status_code=303)

    review = db.get(Review, review_id)

    if review is None:
        return RedirectResponse("/admin/reviews", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="admin/review_form.html",
        context={
            "review": review,
            "published_at_value": datetime_value(review.published_at)
        }
    )


@router.post("/reviews/edit/{review_id}")
def review_edit(
    review_id: int,
    request: Request,
    avatar: UploadFile = File(None),
    author: str = Form(...),
    text: str = Form(...),
    rating: int = Form(...),
    published_at: str = Form(""),
    db: Session = Depends(get_db)
):
    if not check_auth(request):
        return RedirectResponse(
            "/admin/login",
            status_code=303
        )

    review = db.get(
        Review,
        review_id
    )

    if review is None:
        return RedirectResponse(
            "/admin/reviews",
            status_code=303
        )

    final_date = datetime.now()

    if published_at:
        final_date = datetime.fromisoformat(published_at)

    review.author = author
    review.text = text
    review.rating = rating
    review.published_at = final_date

    if avatar and avatar.filename:
        review.avatar = save_upload(avatar)

    db.commit()

    return RedirectResponse(
        "/admin/reviews",
        status_code=303
    )


@router.post("/reviews/delete/{review_id}")
def review_delete(
    review_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    if not check_auth(request):
        return RedirectResponse("/admin/login", status_code=303)

    review = db.get(Review, review_id)

    if review:
        db.delete(review)
        db.commit()

    return RedirectResponse("/admin/reviews", status_code=303)

@router.get("/vip")
def vip_page(
    request: Request,
    db: Session = Depends(get_db)
):
    if not check_auth(request):
        return RedirectResponse("/admin/login", status_code=303)

    vip_predictions = (
        db.query(VipPrediction)
        .order_by(VipPrediction.match_date.desc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="admin/vip_list.html",
        context={
            "vip_predictions": vip_predictions
        }
    )


@router.get("/vip/create")
def vip_create_form(
    request: Request
):
    if not check_auth(request):
        return RedirectResponse("/admin/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="admin/vip_form.html",
        context={
            "vip": None,
            "now": datetime.now().strftime("%Y-%m-%dT%H:%M")
        }
    )


@router.post("/vip/create")
def vip_create(
    request: Request,
    league: str = Form(...),
    match_name: str = Form(...),
    match_date: str = Form(...),
    team_1_logo: UploadFile = File(...),
    team_2_logo: UploadFile = File(...),
    is_active: str = Form("0"),
    db: Session = Depends(get_db)
):
    if not check_auth(request):
        return RedirectResponse("/admin/login", status_code=303)

    team_1_logo_path = save_upload(team_1_logo)
    team_2_logo_path = save_upload(team_2_logo)

    vip = VipPrediction(
        league=league,
        match_name=match_name,
        match_date=datetime.fromisoformat(match_date),
        team_1_logo=team_1_logo_path,
        team_2_logo=team_2_logo_path,
        is_active=is_active == "1"
    )

    db.add(vip)
    db.commit()

    return RedirectResponse("/admin/vip", status_code=303)


@router.get("/vip/edit/{vip_id}")
def vip_edit_form(
    vip_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    if not check_auth(request):
        return RedirectResponse("/admin/login", status_code=303)

    vip = db.get(VipPrediction, vip_id)

    if vip is None:
        return RedirectResponse("/admin/vip", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="admin/vip_form.html",
        context={
            "vip": vip,
            "now": datetime.now().strftime("%Y-%m-%dT%H:%M")
        }
    )


@router.post("/vip/edit/{vip_id}")
def vip_edit(
    vip_id: int,
    request: Request,
    league: str = Form(...),
    match_name: str = Form(...),
    match_date: str = Form(...),
    team_1_logo: UploadFile = File(None),
    team_2_logo: UploadFile = File(None),
    is_active: str = Form("0"),
    db: Session = Depends(get_db)
):
    if not check_auth(request):
        return RedirectResponse("/admin/login", status_code=303)

    vip = db.get(VipPrediction, vip_id)

    if vip is None:
        return RedirectResponse("/admin/vip", status_code=303)

    vip.league = league
    vip.match_name = match_name
    vip.match_date = datetime.fromisoformat(match_date)
    vip.is_active = is_active == "1"

    if team_1_logo and team_1_logo.filename:
        vip.team_1_logo = save_upload(team_1_logo)

    if team_2_logo and team_2_logo.filename:
        vip.team_2_logo = save_upload(team_2_logo)

    db.commit()

    return RedirectResponse("/admin/vip", status_code=303)


@router.post("/vip/delete/{vip_id}")
def vip_delete(
    vip_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    if not check_auth(request):
        return RedirectResponse("/admin/login", status_code=303)

    vip = db.get(VipPrediction, vip_id)

    if vip:
        db.delete(vip)
        db.commit()

    return RedirectResponse("/admin/vip", status_code=303)