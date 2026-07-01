from sqlalchemy import func, select, case
from datetime import datetime, timedelta

from models.borrowed_book import BorrowedBook, BorrowStatus
from models.book_copy import BookCopy
from models.book import Book
from models.user import User
from models.shelf import Shelf


async def count_total_borrowed(db):
    stmt = select(func.count()).select_from(BorrowedBook)

    result = await db.scalar(stmt)

    return result


async def count_active_users(db):
    stmt = select(func.count(func.distinct(BorrowedBook.user_id)))

    result = await db.scalar(stmt)

    return result


async def count_overdue_items(db):
    stmt = select(func.count()).where(BorrowedBook.status == BorrowStatus.OVERDUE)

    result = await db.scalar(stmt)

    return result


async def get_most_popular_genre(db):
    stmt = (
        select(Book.genre, func.count(BorrowedBook.id).label("count"))
        .join(BookCopy, BookCopy.isbn == Book.isbn)
        .join(BorrowedBook, BorrowedBook.book_copy_id == BookCopy.id)
        .group_by(Book.genre)
        .order_by(func.count(BorrowedBook.id).desc())
        .limit(1)
    )

    result = await db.execute(stmt)

    row = result.first()

    return row[0] if row else None


async def get_circulation_trends(db, range):
    days_map = {
        "7d": 7,
        "30d": 30,
        "90d": 90,
    }

    since = datetime.utcnow() - timedelta(days=days_map[range])

    returned_stmt = (
        select(func.date(BorrowedBook.borrowed_at), func.count(BorrowedBook.id))
        .where(
            BorrowedBook.borrowed_at >= since,
            BorrowedBook.status == BorrowStatus.RETURNED,
        )
        .group_by(func.date(BorrowedBook.borrowed_at))
        .order_by(func.date(BorrowedBook.borrowed_at))
    )

    borrowed_stmt = (
        select(
            func.date(BorrowedBook.borrowed_at),
            func.count(BorrowedBook.id),
        )
        .where(
            BorrowedBook.borrowed_at >= since,
            BorrowedBook.status == BorrowStatus.BORROWED,
        )
        .group_by(func.date(BorrowedBook.borrowed_at))
        .order_by(func.date(BorrowedBook.borrowed_at))
    )

    overdue_stmt = (
        select(func.date(BorrowedBook.due_date), func.count(BorrowedBook.id))
        .where(
            BorrowedBook.due_date >= since,
            BorrowedBook.status == BorrowStatus.OVERDUE,
        )
        .group_by(func.date(BorrowedBook.due_date))
        .order_by(func.date(BorrowedBook.due_date))
    )

    returned_result = await db.execute(returned_stmt)
    borrowed_result = await db.execute(borrowed_stmt)
    overdue_result = await db.execute(overdue_stmt)
    borrowed_map = {
        str(row.date): row.count for row in borrowed_result.mappings().all()
    }

    returned_map = {
        str(row.date): row.count for row in returned_result.mappings().all()
    }
    overdue_map = {str(row.date): row.count for row in overdue_result.mappings().all()}

    all_dates = sorted(
        set(borrowed_map.keys() | returned_map.keys() | overdue_map.keys())
    )

    return [
        {
            "date": date,
            "borrowed": borrowed_map.get(date, 0),
            "returned": returned_map.get(date, 0),
            "overdue": overdue_map.get(date, 0),
        }
        for date in all_dates
    ]


async def get_recent_activities(db, range):
    days_map = {
        "7d": 7,
        "30d": 30,
        "90d": 90,
    }

    since = datetime.utcnow() - timedelta(days=days_map[range])

    stmt = (
        select(BorrowedBook, User, BookCopy, Book)
        .join(User, BorrowedBook.user_id == User.id)
        .join(BookCopy, BorrowedBook.book_copy_id == BookCopy.id)
        .join(Book, BookCopy.isbn == Book.isbn)
        .where(BorrowedBook.created_at >= since)
        .order_by(BorrowedBook.created_at.desc())
        .limit(10)
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "id": borrow.id,
            "user": user.name,
            "book_copy_id": borrow.book_copy_id,
            "status": borrow.status,
            "date": borrow.borrowed_at,
            "title": book.title,
            "action": "Borrowed"
            if borrow.status == BorrowStatus.BORROWED
            else "Returned",
            "due_date": borrow.due_date
            if borrow.status == BorrowStatus.BORROWED
            else "-",
        }
        for borrow, user, bookcopy, book in rows
    ]


async def get_inventory_summary(db):
    stmt = select(BookCopy.status, func.count(BookCopy.id)).group_by(BookCopy.status)

    result = await db.execute(stmt)

    rows = result.all()
    return [
        {
            "status": row[0].value,
            "count": row[1],
        }
        for row in rows
    ]


async def get_top_books(db):
    stmt = (
        select(Book.title, func.count(BorrowedBook.id).label("borrow_count"))
        .join(BookCopy, BookCopy.isbn == Book.isbn)
        .join(BorrowedBook, BorrowedBook.book_copy_id == BookCopy.id)
        .group_by(Book.title)
        .order_by(func.count(BorrowedBook.id).desc())
        .limit(5)
    )

    result = await db.execute(stmt)

    rows = result.all()
    return [
        {
            "title": row[0],
            "borrow_count": row[1],
        }
        for row in rows
    ]


async def get_shelf_sage(db):
    stmt = (
        select(
            Shelf.id,
            Shelf.shelf_code,
            Shelf.office_location,
            func.count(BookCopy.id).label("total_books"),
            func.sum(
                case(
                    (BookCopy.status == "AVAILABLE", 1),
                    else_=0,
                )
            ).label("available_books"),
            func.sum(
                case(
                    (BookCopy.status == "BORROWED", 1),
                    else_=0,
                )
            ).label("borrowed_books"),
            func.sum(
                case(
                    (BorrowedBook.status == BorrowStatus.OVERDUE, 1),
                    else_=0,
                )
            ).label("overdue_books"),
        )
        .outerjoin(BookCopy, BookCopy.shelf_id == Shelf.id)
        .outerjoin(BorrowedBook, BorrowedBook.book_copy_id == BookCopy.id)
        .group_by(Shelf.id, Shelf.shelf_code, Shelf.office_location)
    )

    result = await db.execute(stmt)
    rows = result.mappings().all()

    return [
        {
            "shelf_id": row["id"],
            "shelf_name": f"{row['shelf_code']} - {row['office_location']}",
            "total_books": row["total_books"] or 0,
            "available_books": row["available_books"] or 0,
            "borrowed_books": row["borrowed_books"] or 0,
            "overdue_books": row["overdue_books"] or 0,
            "utilization_rate": (
                round(
                    ((row["borrowed_books"] or 0) / (row["total_books"] or 1)) * 100,
                    2,
                )
            ),
        }
        for row in rows
    ]
