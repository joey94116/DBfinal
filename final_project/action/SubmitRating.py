# action/SubmitRating.py

from datetime import datetime
from pymongo import MongoClient
import psycopg2

# ----------------------------------------------------
# 初始化 PostgreSQL
# ----------------------------------------------------
def get_postgres_conn():
    return psycopg2.connect(
        dbname="appdb",
        user="appuser",
        password="appsecret",
        host="db",   # docker-compose 服務名稱
        port=5432
    )

# ----------------------------------------------------
# 初始化 MongoDB
# ----------------------------------------------------
def get_mongo_collection():
    client = MongoClient("mongodb://mongo:27017/")
    db = client["appdb"]                 # 你的 Mongo 資料庫
    col = db["ratings"]                  # 使用 ratings collection
    return col

# ----------------------------------------------------
# 提交評分（取代 Firestore 版本）
# ----------------------------------------------------
def execute(user_id, movie_id, score, comment):
    """
    新版本：寫入 PostgreSQL + MongoDB。
    - PostgreSQL 儲存結構化資料
    - MongoDB 儲存完整 JSON document
    """

    # ================================
    # 1) 寫入 PostgreSQL (結構化)
    # ================================
    pg_conn = None
    mongo_col = None
    try:
        pg_conn = get_postgres_conn()
        cur = pg_conn.cursor()

        # 確保 table 存在
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                movie_id TEXT NOT NULL,
                score INTEGER NOT NULL,
                comment TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 插入一筆資料
        cur.execute("""
            INSERT INTO ratings (user_id, movie_id, score, comment)
            VALUES (%s, %s, %s, %s)
            RETURNING id, timestamp;
        """, (user_id, movie_id, score, comment))

        rating_id, timestamp = cur.fetchone()
        pg_conn.commit()

    except Exception as e:
        return False, f"PostgreSQL 寫入失敗: {e}"

    finally:
        if pg_conn:
            pg_conn.close()

    # ================================
    # 2) 寫入 MongoDB（非結構化）
    # ================================
    try:
        mongo_col = get_mongo_collection()

        rating_doc = {
            "postgres_rating_id": rating_id,  # 對應 SQL 的 ID
            "user_id": user_id,
            "movie_id": movie_id,
            "score": score,
            "comment": comment,
            "timestamp": timestamp,

            # 額外資訊（Mongo 方便放 JSON）
            "user_info": {
                "user_id": user_id,
                "user_name": f"TestUser_{user_id}"
            },
            "movie_info": {
                "movie_id": movie_id,
                "title": f"測試電影 {movie_id}",
            }
        }

        result = mongo_col.insert_one(rating_doc)

    except Exception as e:
        return False, f"MongoDB 寫入失敗: {e}"

    return True, f"評論新增成功！Postgres ID: {rating_id}, MongoDB _id: {result.inserted_id}"
