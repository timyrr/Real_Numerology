from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, text
from sqlalchemy.orm import Session, joinedload

from . import auth, models
from .database import Base, engine, get_db

import os


DEFAULT_POST_IMAGE = "/static/post-images/default.svg"
FLAG = os.getenv("FLAG")


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE posts ADD COLUMN IF NOT EXISTS image_url VARCHAR(255)"))
        connection.execute(text(
            "UPDATE posts SET image_url = :default_image WHERE image_url IS NULL OR image_url = ''"
        ), {"default_image": DEFAULT_POST_IMAGE})
        connection.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_posts_created_at ON posts (created_at)"
        ))
    yield


app = FastAPI(title="Violet Posts", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


def render_template(request: Request, template_name: str, **context):
    context.setdefault("current_user", None)
    context.setdefault("error", None)
    context.setdefault("message", None)
    context.setdefault("default_post_image", DEFAULT_POST_IMAGE)
    context["request"] = request
    return templates.TemplateResponse(name=template_name, context=context)


def get_current_user(request: Request, db: Session = Depends(get_db)):
    cookie_value = request.cookies.get(auth.COOKIE_NAME)
    return auth.get_current_user_from_cookie(db, cookie_value)


def normalize_image_url(raw_value: str | None) -> str:
    value = (raw_value or "").strip()
    return value or DEFAULT_POST_IMAGE


@app.get("/")
def home(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User | None = Depends(get_current_user),
):
    posts = (
        db.query(models.Post)
        .options(joinedload(models.Post.author))
        .order_by(models.Post.created_at.desc(), models.Post.id.desc())
        .all()
    )

    total_posts = db.query(func.count(models.Post.id)).scalar() or 0

    last_galaxy_number = (
        db.query(models.GalaxyNumber)
        .order_by(models.GalaxyNumber.created_at.desc(), models.GalaxyNumber.id.desc())
        .first()
    )

    return render_template(
        request,
        "index.html",
        posts=posts,
        current_user=current_user,
        total_posts=total_posts,
        last_galaxy_number=last_galaxy_number,
        flag=FLAG
    )


@app.get("/posts/{post_id}")
def post_detail(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User | None = Depends(get_current_user),
):
    post = (
        db.query(models.Post)
        .options(joinedload(models.Post.author))
        .filter(models.Post.id == post_id)
        .first()
    )
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден.")

    related_posts = (
        db.query(models.Post)
        .options(joinedload(models.Post.author))
        .filter(models.Post.id != post.id)
        .order_by(models.Post.created_at.desc(), models.Post.id.desc())
        .limit(3)
        .all()
    )
    return render_template(
        request,
        "post_detail.html",
        post=post,
        related_posts=related_posts,
        current_user=current_user,
    )


@app.get("/register")
def register_page(request: Request, current_user: models.User | None = Depends(get_current_user)):
    if current_user:
        return RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)
    return render_template(request, "register.html", current_user=current_user)


@app.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    username = username.strip()
    if len(username) < 3 or len(password) < 4:
        return render_template(
            request,
            "register.html",
            error="Логин должен быть не короче 3 символов, пароль — не короче 4.",
        )

    existing_user = db.query(models.User).filter(models.User.username == username).first()
    if existing_user:
        return render_template(request, "register.html", error="Пользователь с таким логином уже существует.")

    user = models.User(username=username, password_hash=auth.hash_password(password))
    db.add(user)
    db.commit()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/login")
def login_page(request: Request, current_user: models.User | None = Depends(get_current_user)):
    if current_user:
        return RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)
    return render_template(request, "login.html", current_user=current_user)


@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.username == username.strip()).first()
    if not user or not auth.verify_password(password, user.password_hash):
        return render_template(request, "login.html", error="Неверный логин или пароль.")

    cookie_value = auth.create_session(db, user)
    response = RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key=auth.COOKIE_NAME,
        value=cookie_value,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24,
    )
    return response


@app.post("/logout")
def logout(
    request: Request,
    db: Session = Depends(get_db),
):
    cookie_value = request.cookies.get(auth.COOKIE_NAME)
    parsed_cookie = auth.read_cookie_value(cookie_value) if cookie_value else None
    if parsed_cookie:
        db.query(models.UserSession).filter(models.UserSession.token == parsed_cookie.session).delete()
        db.commit()

    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(auth.COOKIE_NAME)
    return response


@app.get("/profile")
def profile(request: Request, current_user: models.User | None = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    user_posts = (
        db.query(models.Post)
        .filter(models.Post.user_id == current_user.id)
        .order_by(models.Post.created_at.desc(), models.Post.id.desc())
        .all()
    )
    return render_template(request, "profile.html", posts=user_posts, current_user=current_user)


@app.post("/posts")
def create_post(
    title: str = Form(...),
    content: str = Form(...),
    image_url: str = Form(""),
    current_user: models.User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    title = title.strip()
    content = content.strip()
    if not title or not content:
        raise HTTPException(status_code=400, detail="Заголовок и содержимое поста не должны быть пустыми.")

    post = models.Post(
        title=title,
        content=content,
        image_url=normalize_image_url(image_url),
        user_id=current_user.id,
    )
    db.add(post)
    db.commit()
    return RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/posts/{post_id}/delete")
def delete_post(
    post_id: int,
    current_user: models.User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден.")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Удалять можно только свои посты.")

    db.delete(post)
    db.commit()
    return RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)
