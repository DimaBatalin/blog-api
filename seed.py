"""
seed.py — Скрипт начального заполнения базы данных.

Создаёт:
  • 3 пользователя с разными ролями
  • 4 категории
  • 6 статей (черновики и опубликованные)
  • 5 комментариев
  • несколько лайков

Данные для входа
──────────────────────────────────────────
 reader_user  / reader123   (Reader)
 author_user  / author123   (Author)
 moderator    / moder123    (Moderator)
──────────────────────────────────────────

Запуск:
    python seed.py
"""

import sys
import os

# Убедимся, что корень проекта в PYTHONPATH
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import Base, SessionLocal, engine
from app import models  # noqa: F401 — регистрируем все модели

from app.core.security import hash_password
from app.models.category import Category
from app.models.comment import Comment
from app.models.like import Like
from app.models.post import Post, PostStatus
from app.models.user import User, UserRole

# ──────────────────────────────────────────────────────────────────────────────
# Учётные данные (зашиты здесь намеренно, чтобы отобразить в README)
# ──────────────────────────────────────────────────────────────────────────────
USERS = [
    {"username": "reader_user", "password": "reader123", "role": UserRole.READER},
    {"username": "author_user", "password": "author123", "role": UserRole.AUTHOR},
    {"username": "moderator",   "password": "moder123",  "role": UserRole.MODERATOR},
]

CATEGORIES = ["Технологии", "Наука", "Культура", "Разное"]

POSTS = [
    {
        "title": "Введение в FastAPI",
        "content": (
            "FastAPI — современный, быстрый веб-фреймворк для создания API с Python 3.8+ "
            "на основе стандартных подсказок типов Python. Он основан на Starlette и Pydantic."
        ),
        "status": PostStatus.PUBLISHED,
        "category": "Технологии",
    },
    {
        "title": "SQLAlchemy 2.0: что нового?",
        "content": (
            "SQLAlchemy 2.0 принёс синтаксис Mapped[T], новый стиль объявления моделей "
            "и улучшенную поддержку асинхронности. В этой статье разберём ключевые изменения."
        ),
        "status": PostStatus.PUBLISHED,
        "category": "Технологии",
    },
    {
        "title": "Чёрные дыры и горизонт событий",
        "content": (
            "Горизонт событий — граница в пространстве-времени, за которой события "
            "не могут влиять на наблюдателя снаружи. Что происходит за этой границей?"
        ),
        "status": PostStatus.PUBLISHED,
        "category": "Наука",
    },
    {
        "title": "Ренессанс цифрового искусства",
        "content": (
            "NFT, генеративное искусство и нейросети — как технологии меняют "
            "представление о творчестве и авторском праве в XXI веке."
        ),
        "status": PostStatus.PUBLISHED,
        "category": "Культура",
    },
    {
        "title": "Черновик: Тест производительности API",
        "content": "Здесь будут результаты нагрузочного тестирования...",
        "status": PostStatus.DRAFT,
        "category": "Технологии",
    },
    {
        "title": "Жизнь за пределами экрана",
        "content": (
            "Цифровой детокс — модное слово или реальная необходимость? "
            "Делимся опытом двухнедельного отдыха от гаджетов."
        ),
        "status": PostStatus.PUBLISHED,
        "category": "Разное",
    },
]

COMMENTS = [
    {"post_title": "Введение в FastAPI",           "text": "Отличная статья! FastAPI действительно очень удобен."},
    {"post_title": "SQLAlchemy 2.0: что нового?",  "text": "Наконец-то разобрался с Mapped[T]. Спасибо!"},
    {"post_title": "Чёрные дыры и горизонт событий", "text": "Всегда мечтал понять, что за горизонтом событий."},
    {"post_title": "Введение в FastAPI",           "text": "Очень жду продолжения серии!"},
    {"post_title": "Жизнь за пределами экрана",   "text": "Сам пробовал — первые три дня тяжело, потом отлично."},
]


def run_seed() -> None:
    print("🌱 Начинаю заполнение базы данных…")

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # ── Пользователи ──────────────────────────────────────────────────────
        created_users: dict[str, User] = {}
        for u in USERS:
            existing = db.query(User).filter(User.username == u["username"]).first()
            if not existing:
                user = User(
                    username=u["username"],
                    password_hash=hash_password(u["password"]),
                    role=u["role"],
                )
                db.add(user)
                db.flush()
                created_users[u["username"]] = user
                print(f"  ✅ Пользователь: {u['username']} ({u['role'].value})")
            else:
                created_users[u["username"]] = existing
                print(f"  ⏩ Пользователь уже существует: {u['username']}")

        author = created_users["author_user"]
        reader = created_users["reader_user"]
        moderator = created_users["moderator"]

        # ── Категории ─────────────────────────────────────────────────────────
        created_cats: dict[str, Category] = {}
        for name in CATEGORIES:
            existing = db.query(Category).filter(Category.name == name).first()
            if not existing:
                cat = Category(name=name)
                db.add(cat)
                db.flush()
                created_cats[name] = cat
                print(f"  ✅ Категория: {name}")
            else:
                created_cats[name] = existing
                print(f"  ⏩ Категория уже существует: {name}")

        # ── Статьи ────────────────────────────────────────────────────────────
        from datetime import datetime, timezone

        created_posts: dict[str, Post] = {}
        for p in POSTS:
            existing = db.query(Post).filter(Post.title == p["title"]).first()
            if not existing:
                cat = created_cats.get(p["category"])
                post = Post(
                    author_id=author.id,
                    category_id=cat.id if cat else None,
                    title=p["title"],
                    content=p["content"],
                    status=p["status"],
                    published_at=(
                        datetime.now(timezone.utc)
                        if p["status"] == PostStatus.PUBLISHED
                        else None
                    ),
                )
                db.add(post)
                db.flush()
                created_posts[p["title"]] = post
                print(f"  ✅ Статья: «{p['title']}» ({p['status'].value})")
            else:
                created_posts[p["title"]] = existing
                print(f"  ⏩ Статья уже существует: «{p['title']}»")

        # ── Комментарии ───────────────────────────────────────────────────────
        for i, c in enumerate(COMMENTS):
            post = created_posts.get(c["post_title"])
            if not post:
                continue
            # Чередуем авторов комментариев
            commenter = reader if i % 2 == 0 else moderator
            existing = (
                db.query(Comment)
                .filter(Comment.post_id == post.id, Comment.text == c["text"])
                .first()
            )
            if not existing:
                comment = Comment(
                    post_id=post.id,
                    user_id=commenter.id,
                    text=c["text"],
                )
                db.add(comment)
                print(f"  ✅ Комментарий к «{c['post_title']}»")
            else:
                print("  ⏩ Комментарий уже существует")

        # ── Лайки ─────────────────────────────────────────────────────────────
        like_pairs = [
            (reader.id,    "Введение в FastAPI"),
            (reader.id,    "Чёрные дыры и горизонт событий"),
            (moderator.id, "Введение в FastAPI"),
            (moderator.id, "SQLAlchemy 2.0: что нового?"),
            (reader.id,    "Жизнь за пределами экрана"),
        ]
        for user_id, post_title in like_pairs:
            post = created_posts.get(post_title)
            if not post:
                continue
            existing = (
                db.query(Like)
                .filter(Like.user_id == user_id, Like.post_id == post.id)
                .first()
            )
            if not existing:
                db.add(Like(user_id=user_id, post_id=post.id))
                print(f"  ✅ Лайк: user_id={user_id} → «{post_title}»")

        db.commit()
        print("\n🎉 База данных успешно заполнена!")
        print("\n📋 Данные для входа:")
        print("  reader_user  / reader123  (Reader)")
        print("  author_user  / author123  (Author)")
        print("  moderator    / moder123   (Moderator)")

    except Exception as exc:
        db.rollback()
        print(f"\n❌ Ошибка: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
