import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'pechati5.db')


def migrate_sqlite():
    if not os.path.exists(DB_PATH):
        print(f'База {DB_PATH} не найдена. Пропуск миграции.')
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("PRAGMA table_info(orders)")
        cols = [r[1] for r in cur.fetchall()]
        for col_name, col_def in [
            ('needs_delivery', 'INTEGER DEFAULT 0'),
            ('delivery_datetime', "TEXT DEFAULT ''"),
            ('delivery_address', "TEXT DEFAULT ''"),
        ]:
            if col_name not in cols:
                cur.execute(f"ALTER TABLE orders ADD COLUMN {col_name} {col_def}")
                print(f'Добавлена колонка orders.{col_name}')
            else:
                print(f'Колонка orders.{col_name} уже есть')
        conn.commit()
        print('Миграция завершена.')
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


if __name__ == '__main__':
    migrate_sqlite()
