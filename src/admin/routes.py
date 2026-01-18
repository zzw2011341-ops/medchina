"""Admin panel routes for serving HTML pages"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from admin.auth import get_current_admin_optional

router = APIRouter(prefix="/admin", tags=["Admin Panel"])
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Admin login page"""
    return templates.TemplateResponse("admin/login.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    current_admin: dict = Depends(get_current_admin_optional)
):
    """Admin dashboard page"""
    if not current_admin:
        return templates.TemplateResponse("admin/login.html", {"request": request})
    
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request, "current_user": current_admin, "active": "dashboard"}
    )


@router.get("/users", response_class=HTMLResponse)
async def users_page(
    request: Request,
    current_admin: dict = Depends(get_current_admin_optional)
):
    """User management page"""
    if not current_admin:
        return templates.TemplateResponse("admin/login.html", {"request": request})
    
    return templates.TemplateResponse(
        "admin/users.html",
        {"request": request, "current_user": current_admin, "active": "users"}
    )


@router.get("/doctors", response_class=HTMLResponse)
async def doctors_page(
    request: Request,
    current_admin: dict = Depends(get_current_admin_optional)
):
    """Doctor management page"""
    if not current_admin:
        return templates.TemplateResponse("admin/login.html", {"request": request})
    
    return templates.TemplateResponse(
        "admin/doctors.html",
        {"request": request, "current_user": current_admin, "active": "doctors"}
    )


@router.get("/hospitals", response_class=HTMLResponse)
async def hospitals_page(
    request: Request,
    current_admin: dict = Depends(get_current_admin_optional)
):
    """Hospital management page"""
    if not current_admin:
        return templates.TemplateResponse("admin/login.html", {"request": request})
    
    return templates.TemplateResponse(
        "admin/users.html",  # Using users as template for simplicity
        {"request": request, "current_user": current_admin, "active": "hospitals"}
    )


@router.get("/diseases", response_class=HTMLResponse)
async def diseases_page(
    request: Request,
    current_admin: dict = Depends(get_current_admin_optional)
):
    """Disease management page"""
    if not current_admin:
        return templates.TemplateResponse("admin/login.html", {"request": request})
    
    return templates.TemplateResponse(
        "admin/doctors.html",  # Using doctors as template for simplicity
        {"request": request, "current_user": current_admin, "active": "diseases"}
    )


@router.get("/attractions", response_class=HTMLResponse)
async def attractions_page(
    request: Request,
    current_admin: dict = Depends(get_current_admin_optional)
):
    """Attraction management page"""
    if not current_admin:
        return templates.TemplateResponse("admin/login.html", {"request": request})
    
    return templates.TemplateResponse(
        "admin/doctors.html",  # Using doctors as template for simplicity
        {"request": request, "current_user": current_admin, "active": "attractions"}
    )


@router.get("/travel-plans", response_class=HTMLResponse)
async def travel_plans_page(
    request: Request,
    current_admin: dict = Depends(get_current_admin_optional)
):
    """Travel plan management page"""
    if not current_admin:
        return templates.TemplateResponse("admin/login.html", {"request": request})
    
    return templates.TemplateResponse(
        "admin/doctors.html",  # Using doctors as template for simplicity
        {"request": request, "current_user": current_admin, "active": "travel-plans"}
    )


@router.get("/appointments", response_class=HTMLResponse)
async def appointments_page(
    request: Request,
    current_admin: dict = Depends(get_current_admin_optional)
):
    """Appointment management page"""
    if not current_admin:
        return templates.TemplateResponse("admin/login.html", {"request": request})
    
    return templates.TemplateResponse(
        "admin/doctors.html",  # Using doctors as template for simplicity
        {"request": request, "current_user": current_admin, "active": "appointments"}
    )


@router.get("/payments", response_class=HTMLResponse)
async def payments_page(
    request: Request,
    current_admin: dict = Depends(get_current_admin_optional)
):
    """Payment management page"""
    if not current_admin:
        return templates.TemplateResponse("admin/login.html", {"request": request})
    
    return templates.TemplateResponse(
        "admin/doctors.html",  # Using doctors as template for simplicity
        {"request": request, "current_user": current_admin, "active": "payments"}
    )


@router.get("/finance", response_class=HTMLResponse)
async def finance_page(
    request: Request,
    current_admin: dict = Depends(get_current_admin_optional)
):
    """Finance management page"""
    if not current_admin:
        return templates.TemplateResponse("admin/login.html", {"request": request})
    
    return templates.TemplateResponse(
        "admin/finance.html",
        {"request": request, "current_user": current_admin, "active": "finance"}
    )


@router.get("/logs", response_class=HTMLResponse)
async def logs_page(
    request: Request,
    current_admin: dict = Depends(get_current_admin_optional)
):
    """Operation log page"""
    if not current_admin:
        return templates.TemplateResponse("admin/login.html", {"request": request})
    
    return templates.TemplateResponse(
        "admin/doctors.html",  # Using doctors as template for simplicity
        {"request": request, "current_user": current_admin, "active": "logs"}
    )
