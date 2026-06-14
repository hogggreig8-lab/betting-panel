from fastapi import APIRouter
from fastapi import Request
from fastapi import Depends
from app.models.site_content import SiteContent
from sqlalchemy.orm import Session
from app.models.review import Review
from fastapi.templating import Jinja2Templates
from app.models.review import Review
from app.core.database import get_db
from fastapi import Query
from app.models.stat import Stat
from app.models.setting import Setting
from app.models.vip_prediction import VipPrediction
router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def home(
    request: Request,
    db: Session = Depends(get_db)
):
    content = db.query(SiteContent).first()
    setting = db.query(Setting).first()
    vip_prediction = (
        db.query(VipPrediction)
        .filter(VipPrediction.is_active == True)
        .order_by(VipPrediction.match_date.desc())
        .first()
    )
    latest_reviews = (
        db.query(Review)
        .order_by(Review.published_at.desc())
        .limit(3)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "content": content,
            "telegram": setting,
            "latest_reviews": latest_reviews,
            "vip_prediction": vip_prediction
        }
    )
@router.get("/reviews")
def reviews(
    request: Request,
    page: int = 1,
    db: Session = Depends(get_db)
):
    if page < 1:
        page = 1

    per_page = 6

    total_reviews = db.query(Review).count()

    total_pages = (total_reviews + per_page - 1) // per_page

    reviews = (
        db.query(Review)
        .order_by(Review.published_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="reviews.html",
        context={
            "reviews": reviews,
            "page": page,
            "total_pages": total_pages
        }
    )

@router.get("/stats")
def stats_page(
    request: Request,
    tab: str = Query("free"),
    page: int = Query(1),
    db: Session = Depends(get_db)
):
    per_page = 10

    if tab not in ["free", "paid"]:
        tab = "free"

    if page < 1:
        page = 1

    total_items = (
        db.query(Stat)
        .filter(Stat.category == tab)
        .count()
    )

    total_pages = (total_items + per_page - 1) // per_page

    if total_pages < 1:
        total_pages = 1

    if page > total_pages:
        page = total_pages

    offset = (page - 1) * per_page

    current_stats = (
        db.query(Stat)
        .filter(Stat.category == tab)
        .order_by(Stat.match_date.desc(), Stat.id.desc())
        .offset(offset)
        .limit(per_page)
        .all()
    )

    all_current_stats = (
        db.query(Stat)
        .filter(Stat.category == tab)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="stats.html",
        context={
            "current_stats": current_stats,
            "all_current_stats": all_current_stats,
            "active_tab": tab,
            "page": page,
            "total_pages": total_pages
        }
    )


@router.get("/reviews")
def reviews(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="reviews.html",
        context={}
    )


@router.get("/contact")
def contact(
    request: Request,
    db: Session = Depends(get_db)
):
    setting = db.query(Setting).first()

    return templates.TemplateResponse(
        request=request,
        name="contact.html",
        context={
            "telegram": setting
        }
    )