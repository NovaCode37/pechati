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
        cur.execute("PRAGMA table_info(layouts)")
        cols = [r[1] for r in cur.fetchall()]
        if 'price' not in cols:
            cur.execute("ALTER TABLE layouts ADD COLUMN price REAL DEFAULT 750")
            print('Добавлена колонка layouts.price')
        else:
            print('Колонка layouts.price уже есть')

        cur.execute("PRAGMA table_info(price_options)")
        cols = [r[1] for r in cur.fetchall()]
        if 'description' not in cols:
            cur.execute("ALTER TABLE price_options ADD COLUMN description TEXT DEFAULT ''")
            print('Добавлена колонка price_options.description')
        else:
            print('Колонка price_options.description уже есть')

        conn.commit()
        print('Миграция завершена.')
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


if __name__ == '__main__':
    migrate_sqlite()
