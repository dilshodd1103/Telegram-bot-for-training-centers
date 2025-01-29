from operator import truediv
from typing import Union

import asyncpg
from asyncpg.pool import Pool

from data import config


class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )

        if self.pool is None:
            raise RuntimeError("Pool obyekti yaratilmagan. connect() funksiyasini chaqirganingizni tekshiring.")

    async def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                try:
                    if fetchone:
                        result = await connection.fetchrow(sql, *parameters)
                        return result
                    elif fetchall:
                        result = await connection.fetch(sql, *parameters)
                        return result
                    else:
                        await connection.execute(sql, *parameters)
                        if commit:
                            return True
                except Exception as e:
                    print(f"Xatolik yuz berdi: {e}")
                    raise

    #
    # async def create_tables(self):
    #     sql = """
    #     CREATE TABLE IF NOT EXISTS informations_obunachilar (
    #         id SERIAL PRIMARY KEY,
    #         username VARCHAR(150) UNIQUE NOT NULL,
    #         phone_num VARCHAR(15) UNIQUE NULL,
    #         joined_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    #         admin BOOLEAN DEFAULT FALSE,
    #         telegram_id BIGINT NOT NULL UNIQUE,
    #         language VARCHAR(2) DEFAULT    'uz',
    #         chat_ID BIGINT NOT NULL
    #     );
    #     """
    #     await self.execute(sql, commit=True)
    #
    #     sql = """
    #     CREATE TABLE IF NOT EXISTS informations_kurslar (
    #         id SERIAL PRIMARY KEY,
    #         nom VARCHAR(255) NOT NULL,
    #         tarif TEXT NOT NULL
    #     );
    #     """
    #     await self.execute(sql, commit=True)
    #
    #     sql = """
    #     CREATE TABLE  informations_xabarlar (
    #         id SERIAL PRIMARY KEY,
    #         content_type VARCHAR(50) NOT NULL,
    #         content TEXT NOT NULL,
    #         send_to_all BOOLEAN DEFAULT TRUE,
    #         sent_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    #     );
    #     """
    #     await self.execute(sql, commit=True)

    @staticmethod
    def format_args(queries, parameters: dict):
        queries += " AND ".join([f"{item} = ${idx + 1}" for idx, item in enumerate(parameters)])
        return queries, tuple(parameters.values())

    async def add_user(self, full_name, username, phone_num, telegram_id, language, admin, joined_at):
        sql = """
          INSERT INTO informations_obunachilar (full_name, username, phone_num, telegram_id, language, admin, joined_at) 
          VALUES ($1, $2, $3, $4, $5, $6, $7) 
          """
        await self.execute(sql, parameters=(full_name, username, phone_num, telegram_id, language, admin, joined_at),
                           commit=True)

    async def select_all_users(self):
        sql = "SELECT * FROM informations_obunachilar"
        return await self.execute(sql, fetchall=True)

    async def select_user(self, telegram_id: int):
        sql = "SELECT * FROM informations_obunachilar WHERE telegram_id = $1"
        return await self.execute(sql, parameters=(telegram_id,), fetchone=True)

    async def get_admin(self):
        sql = "SELECT * FROM informations_obunachilar WHERE admin = TRUE"
        result = await self.execute(sql, fetchall=True)
        return result

    async def check_admin(self, selected_data):
        sql = "SELECT admin FROM informations_obunachilar WHERE telegram_id=$1"
        result = await self.execute(sql, parameters=(selected_data,), fetchone=True)
        if result:
            return bool(result['admin'])
        return False

    async def remove_admin(self, admin_id: int):
        sql = "UPDATE informations_obunachilar SET admin = FALSE WHERE id = $1"
        return await self.execute(sql, parameters=(admin_id,), commit=True)

    async def set_admin(self, selected_data):
        sql = "UPDATE informations_obunachilar SET admin = TRUE WHERE id = $1"
        result = await self.execute(sql, parameters=(selected_data,), commit=True)
        return result

    async def update_user_name(self, name, id: int):
        sql = "UPDATE informations_obunachilar SET full_name = $1 WHERE telegram_id = $2"
        return await self.execute(sql, parameters=(name, id,), commit=True)

    async def update_user_number(self, id, raqam):
        sql = "UPDATE informations_obunachilar SET phone_num = $2 WHERE telegram_id = $1"
        return await self.execute(sql, parameters=(id, raqam,), commit=True)

    async def add_kurs(self, nom, tarif, rasm):
        sql = "INSERT INTO informations_kurslar(nom, tarif, rasm) VALUES($1, $2, $3)"
        return await self.execute(sql, parameters=(nom, tarif, rasm), commit=True)

    async def select_all_kurs(self):
        sql = "SELECT * FROM informations_kurslar"
        return await self.execute(sql, fetchall=True)

    async def select_kurs(self, id: int):
        sql = "SELECT * FROM informations_kurslar WHERE id = $1"
        return await self.execute(sql, parameters=(id,), fetchone=True)

    async def update_nom(self, id, tarif):
        sql = "UPDATE informations_kurslar SET nom = $1 WHERE id = $2"
        return await self.execute(sql, parameters=(tarif, id), commit=True)

    async def update_tarif(self, id, tarif):
        sql = "UPDATE informations_kurslar SET tarif = $1 WHERE id = $2"
        return await self.execute(sql, parameters=(tarif, id), commit=True)

    async def update_course_image(self, id, image):
        sql = "UPDATE informations_kurslar SET rasm = $1 WHERE id = $2"
        return await self.execute(sql, parameters=(image, id,), commit=True)

    async def delete_kurs(self, kurs_id):
        sql = "DELETE FROM informations_kurslar WHERE id=$1"
        return await self.execute(sql, parameters=(kurs_id,), commit=True)

    async def get_image(self, data):
        sql = "SELECT rasm FROM informations_kurslar WHERE id = $1"
        result = await self.execute(sql, parameters=(data,), fetchone=True)
        if result:
            return result['rasm']

    async def update_course_name(self, id, name):
        sql = "UPDATE informations_kurslar SET nom = $1 WHERE id = $2"
        return await self.execute(sql, parameters=(name, id,), commit=True)

    async def count_admins(self):
        sql = """
        SELECT COUNT(*) FROM informations_obunachilar 
        WHERE admin = TRUE;
        """
        result = await self.execute(sql, fetchone=True)
        return result[0]

    async def add_admin_reklama(self, content_type, content, sent_date):
        sql = """
        INSERT INTO informations_xabar_yuborish (content_type, content, sent_date)
        VALUES ($1, $2, $3)
        """
        await self.execute(sql, parameters=(content_type, content, sent_date,), commit=True)

    async def count_users(self):
        result = await self.execute("SELECT COUNT(*) FROM informations_obunachilar", fetchone=True)
        return result[0] if result else 0

    # async def select_users_with_pagination(self, limit: int, offset: int):
    #     sql = "SELECT * FROM informations_obunachilar LIMIT  $1 OFFSET  $2"
    #     result = await self.execute(sql, parameters=(limit, offset), fetchall=True)
    #     return result[0] if result else 0

    async def add_month(self):
        sql = """
        SELECT COUNT(joined_at) AS for_last_month
        FROM informations_obunachilar
        WHERE joined_at > NOW() - INTERVAL '1 month'
        """
        result = await self.execute(sql, fetchone=True)
        return result[0] if result else 0

    # async def latest_news_reader(self):
    #     sql = """
    #     SELECT send_to_all
    #     FROM informations_xabar_yuborish
    #     ORDER BY id DESC LIMIT 1
    #     """
    #
    #     result = await self.execute(sql, fetchone=True)
    #     return result[0] if result else 0

    async def add_statistic(self, all_subscribers: int, for_last_month: int, ):
        sql = """
            INSERT INTO informations_statistika (all_subscribers, for_last_month)
            VALUES ($1, $2)
           """
        await self.execute(sql, parameters=(all_subscribers, for_last_month), commit=True)

    async def add_informations(self, data, message):
        sql = "INSERT INTO informations_malumotlar (admins, last_message_sent_date) VALUES ($1, $2)"
        await self.execute(sql, parameters=(data, message,), commit=True)

    async def get_message(self):
        sql = """
            SELECT sent_date 
            FROM informations_xabar_yuborish 
            ORDER BY sent_date DESC LIMIT 1
            """
        result = await self.execute(sql, fetchone=True)
        if result:
            return result[0]
        return None

    async def get_user_language(self, user_id):
        sql = "SELECT language FROM informations_obunachilar WHERE telegram_id=$1"
        result = await self.execute(sql, parameters=(user_id,), fetchone=True)
        return result["language"] if result else None

    async def update_language(self, user_id, new_language):
        sql = """ 
            UPDATE informations_obunachilar
            SET language = $1, last_active_at = NOW()
            WHERE telegram_id = $2
            RETURNING language
            """
        result = await self.execute(sql, parameters=(new_language, user_id,), commit=True)
        return result

    async def save_user_action(self, user_id: int):
        sql = """
        UPDATE informations_obunachilar
        SET last_active_at = NOW()
        WHERE telegram_id = $1
        """
        await self.execute(sql, parameters=(user_id,), commit=True)

    async def get_active_users(self):
        sql = """
        SELECT COUNT(*)
        FROM informations_obunachilar
        WHERE last_active_at >= NOW() - INTERVAL '24 hours'
        """
        result = await self.execute(sql, fetchone=True)
        return result[0] if result else 0
