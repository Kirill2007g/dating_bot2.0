from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from db.database import engine
from db.models import User
from db.schemas import UserCreate
from pydantic import ValidationError

# 1. Настраиваем фабрику сессий
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Данные для теста (изменим tg_id, чтобы не было ошибки дубликата UNIQUE)
raw_bot_data = {
    "tg_id": 987654332319,  
    "username": "alex_dating",
    "description": "Люблю программировать! и путешествовать!",
    "age": 23,
    "city": "Одесса",
    "looked_for": "Серьезные отношения!"
}

try:
    # 2. Проверяем через Pydantic
    validated_user = UserCreate(**raw_bot_data)
    
    # Проверяем, нет ли уже пользователя с таким tg_id, чтобы код не падал
    existing_user = db.scalar(select(User).where(User.tg_id == validated_user.tg_id))
    
    if not existing_user:
        # Переводим в SQLAlchemy модель и сохраняем
        db_user = User(**validated_user.model_dump())
        db.add(db_user)
        db.commit()
        print(f"✅ Успешно записан пользователь: {db_user.username}\n")
    else:
        print(f"ℹ️ Пользователь с tg_id {validated_user.tg_id} уже есть в базе.\n")

    # 3. ВЫВОД ТАБЛИЦЫ НА ЭКРАН
    print("=== СОДЕРЖИМОЕ ТАБЛИЦЫ USERS ===")
    
    # Делаем запрос: SELECT * FROM users
    query = select(User)
    result = db.scalars(query).all()  # Получаем список всех объектов User

    # Пробегаемся циклом по каждой строчке и печатаем поля
    for user in result:
        print(f"ID: {user.id} | TG_ID: {user.tg_id} | Юзернейм: @{user.username} | Возраст: {user.age} | Город: {user.city} | О себе: {user.description}")
        print("-" * 40)

except ValidationError as e:
    print("❌ Ошибка валидации Pydantic:")
    print(e.json(indent=2))

finally:
    # Обязательно закрываем сессию, отпуская соединение
    db.close()
