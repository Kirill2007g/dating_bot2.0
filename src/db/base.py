from src.db.database import engine, Base
# Импортируем модели, чтобы они зарегистрировались в Base
import src.db.models

# Base.metadata.drop_all(bind=engine)
print("Создание таблиц...")
# Теперь Base знает абсолютно все модели из файла models.py
Base.metadata.create_all(bind=engine)
print("Таблицы успешно созданы!")
