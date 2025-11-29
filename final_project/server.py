# server.py

import psycopg2
from psycopg2 import OperationalError

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from action.SubmitRating import execute as submit_rating_action

CURRENT_USER = None
IS_ADMIN = False


# ----------------------------------------------------
# 服務啟動：初始化 PostgreSQL + MongoDB
# ----------------------------------------------------

def check_postgres():
    print("=== Checking PostgreSQL connection & CRUD ===")
    try:
        conn = psycopg2.connect(
            dbname="appdb",
            user="appuser",
            password="appsecret",
            host="db",         # docker-compose 的 service 名稱
            port=5432
        )
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id   SERIAL PRIMARY KEY,
                msg  TEXT NOT NULL
            );
        """)
        conn.commit()
        print("Table test_table is ready.")

        cur.execute(
            "INSERT INTO test_table (msg) VALUES (%s) RETURNING id;",
            ("hello",)
        )
        row_id = cur.fetchone()[0]
        conn.commit()
        print(f"Inserted row with id = {row_id}")

        cur.execute("SELECT id, msg FROM test_table WHERE id = %s;", (row_id,))
        row = cur.fetchone()
        print("Selected row:", row)

        cur.close()
        conn.close()

        print("PostgreSQL CRUD test finished.\n")
        return True

    except OperationalError as e:
        print("PostgreSQL connection failed:", e)
        return False
    except Exception as e:
        print("PostgreSQL CRUD error:", e)
        return False


def check_mongo():
    print("=== Checking MongoDB connection & CRUD ===")
    try:
        client = MongoClient("mongodb://mongo:27017/", serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        print("MongoDB connected successfully!")

        db = client["appdb"]
        col = db["test_collection"]

        doc = {"msg": "hello from mongo"}
        result = col.insert_one(doc)
        print("Inserted document _id =", result.inserted_id)

        found = col.find_one({"_id": result.inserted_id})
        print("Found document:", found)

        print("Last 5 documents:")
        for d in col.find().sort("_id", -1).limit(5):
            print("  ", d)

        client.close()

        print("MongoDB CRUD test finished.\n")
        return True

    except PyMongoError as e:
        print("MongoDB connection / CRUD failed:", e)
        return False
    except Exception as e:
        print("MongoDB other error:", e)
        return False


def start_services():
    print("==========================================")
    print("   啟動服務：檢查 PostgreSQL / MongoDB")
    print("==========================================")

    ok_pg = check_postgres()
    ok_mg = check_mongo()

    if ok_pg and ok_mg:
        print("==========================================")
        print("服務啟動成功：兩個資料庫連線正常")
        print("==========================================")
        return True

    print("❌ 有資料庫無法啟動，請檢查 docker-compose 或帳密設定")
    return False


# ----------------------------------------------------
# 使用者登入 / 評分 / 選單相關邏輯（保持不變）
# ----------------------------------------------------

def handle_login(username, password):
    global CURRENT_USER, IS_ADMIN

    if username == "admin" and password == "123":
        CURRENT_USER = username
        IS_ADMIN = True
        return True, "管理員登入成功！"
    elif username == "userA" and password == "123":
        CURRENT_USER = username
        IS_ADMIN = False
        return True, "用戶登入成功！"
    else:
        return False, "帳號或密碼錯誤。"


def handle_post_rating(username, movie_id, score, comment):
    if username == "userA":
        actual_user_id = 1001

        success, message = submit_rating_action(actual_user_id, movie_id, score, comment)
        return success, message

    return False, "無法識別用戶。"


def handle_view_menu():
    if CURRENT_USER is None:
        return ["1. 登入", "2. 註冊", "3. 離開"]
    elif IS_ADMIN:
        return ["1. 發布/維護電影", "2. 刪除評論", "3. 統計報表", "4. 登出"]
    else:
        return ["1. 搜尋電影", "2. 發表評論", "3. 觀影清單", "4. 登出"]


# ----------------------------------------------------
# 開發測試
# ----------------------------------------------------
if __name__ == "__main__":
    start_services()
