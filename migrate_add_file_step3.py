from app import app, db


def migrate():
    with app.app_context():
        try:
            db.session.execute(db.text("ALTER TABLE orders ADD COLUMN file_path_step3 VARCHAR(300) DEFAULT ''"))
            db.session.commit()
            print('OK: колонка file_path_step3 добавлена')
        except Exception as e:
            if 'duplicate column name' in str(e).lower() or 'already exists' in str(e).lower():
                print('Колонка file_path_step3 уже существует')
            else:
                raise


if __name__ == '__main__':
    migrate()
