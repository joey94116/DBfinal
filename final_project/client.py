# client.py

import server

def display_menu(options):
    """根據 server.py 提供的選項顯示菜單"""
    print("\n--- 請輸入您的操作 ---")
    for option in options:
        print(option)
    return input("選擇: ")

def main_loop():
    """程式的主迴圈"""
    
    if not server.start_services():
        print("系統初始化失敗，程式退出。")
        return
        
    while True:
        menu_options = server.handle_view_menu()
        choice = display_menu(menu_options)
        
        # 處理未登入狀態的選項
        if server.CURRENT_USER is None:
            if choice == '1':
                username = input("帳號: ")
                password = input("密碼: ")
                success, message = server.handle_login(username, password)
                print(f"結果: {message}")
            elif choice == '3':
                print("感謝使用，再見！")
                break
        
        # TODO: 處理登入後的選項 (這裡將是模塊二/三的主要工作)
        elif server.CURRENT_USER is not None:
            if choice == '4': # 登出
                server.CURRENT_USER = None
                server.IS_ADMIN = False
                print("已登出。")
            elif choice == '2' and not server.IS_ADMIN: # 用戶：發表評論 (模塊二功能)
                print("進入發表評論頁面...")
                print("\n--- 發表您的評論 ---")
            
                # --- 以下是需要添加的輸入邏輯 ---
                movie_id = input("請輸入電影代號 (如 M001): ").strip()
                try:
                    score = int(input("請輸入評分 (1-5分): "))
                    if not 1 <= score <= 5:
                        print("評分必須在 1 到 5 之間，請重新輸入。")
                        continue # 重新開始迴圈
                except ValueError:
                    print("評分輸入無效，請重新輸入。")
                    continue # 重新開始迴圈
                
                comment = input("請輸入評論內容: ").strip()
                
                # 呼叫 server 處理業務邏輯
                success, message = server.handle_post_rating(server.CURRENT_USER, movie_id, score, comment)
                print(f"\n--- 評論結果 ---\n{message}")

if __name__ == '__main__':
    main_loop()