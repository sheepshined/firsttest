import pymysql
import time
import datetime
# 图书管理核心类
class BOOKManager:
    # 初始化数据库连接
    def __init__(self):
        try:
            self.conn = pymysql.connect(
                host="localhost",
                user="root",          # 改为自己的MySQL账号
                password="123456",# 改为自己的MySQL密码
                database="book_db",
                charset="utf8mb4",
                autocommit=False
            )
            self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            print("✅ 数据库连接成功（双表模式）")
        except Exception as e:
            print("❌ 数据库连接失败：", e)

    def write_log(self, msg):
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            with open("book_log.txt", "a", encoding="utf-8") as f:
                f.write(f"[{now}] {msg}\n")
#添加图书信息
    def add_book(self, book_id, book_name, book_kind, book_date,price,wirter):
        try:
            # 先插入图书info基础信息
            sql_stu = "INSERT INTO book_info(book_id, book_name) VALUES(%s,%s)"
            self.cursor.execute(sql_stu, (book_id, book_name,))

            # 再插入对应book_in
            sql_score = "INSERT INTO book_in(nid, book_kind, book_date,price,wirter) VALUES(%s,%s,%s,%s,%s)"
            self.cursor.execute(sql_score, (book_id, book_kind, book_date, price, wirter))

            self.conn.commit()
            print("✅ 图书信息添加成功")
            self.write_log(f"新增图书：ID{book_id} 书名{book_name}")
        except Exception as e:
            self.conn.rollback()
            print("❌ 添加失败！重复或数据格式错误")

# 2. 查看所有图书（联查双表，展示完整信息+成绩）
    def show_all_book(self):

        sql = """
        SELECT bo.book_id, bo.book_name, bo.status, b.book_kind, b.book_date, b.price, b.wirter
        FROM book_info bo
        LEFT JOIN book_in b ON bo.book_id = b.nid
        """
        self.cursor.execute(sql)
        res = self.cursor.fetchall()

        if not res:
            print("暂无！")
            return
        
        print("\n========== 图书完整信息列表 ==========")
        for item in res:
            print(f"图书id：{item['book_id']} | 图书名称：{item['book_name']} | 图书状态：{item['status']} | 专业：{item['book_kind']}")
            print(f"发行日期：{item['book_date']} | 价格：{item['price']}  | 作者：{item['wirter']}")
            print("-" * 90)
        self.write_log(f"查询所有图书信息")

        #3按图书id查询图书信息
    def search_book_id(self, book_id):
        sql = """
        SELECT bo.book_id, bo.book_name, bo.status, b.book_kind, b.book_date, b.price,b.wirter
        FROM book_info bo
        LEFT JOIN book_in b ON bo.book_id = b.nid
        WHERE bo.book_id = %s
        """ 
        self.cursor.execute(sql, (book_id,))
        res = self.cursor.fetchone()

        if res:
            print("\n========== 图书详情 ==========")
            print(f"图书id：{res['book_id']}")
            print(f"图书名称：{res['book_name']}")
            print(f"状态：{res['status']}")
            print(f"分类：{res['book_kind']}")
            print(f"出版日期：{res['book_date']}")
            print(f"价格：{res['price']}")
            print(f"作者：{res['wirter']}")
        else:
            print("❌ 未查询到该信息！")
        
        self.write_log(f"查询图书id：{book_id} 信息")


    # 4. 修改学生基础信息（仅修改bo）
    def update_book_name(self, book_id, book_name):
      try:
          sql = "UPDATE book_info SET book_name=%s WHERE book_id=%s"
          self.cursor.execute(sql, (book_name, book_id))
          self.conn.commit()
          if self.cursor.rowcount > 0:
              print("✅ 书名修改成功")
          else:
              print("❌ 未找到该图书")
      except Exception as e:
          self.conn.rollback()
          print(f"❌ 修改失败: {e}")
      self.write_log(f'修改图书id：{book_id} 书名为：{book_name}')



    def update_book_info(self, book_id, book_kind, book_date, price, wirter):
      try:
          sql = "UPDATE book_in SET book_kind=%s, book_date=%s, price=%s, wirter=%s WHERE nid=%s"
          self.cursor.execute(sql, (book_kind, book_date, price, wirter, book_id))
          self.conn.commit()
          if self.cursor.rowcount > 0:
              print("✅ 修改成功")
          else:
              print("❌ 未找到该数据")
      except Exception as e:
          self.conn.rollback()
          print(f"❌ 修改失败: {e}")
      self.write_log(f'修改图书id：{book_id} 信息为：{book_kind} {book_date} {price} {wirter}')

    # 6. 删除学生信息（外键级联bo，b自动删除）
    def delete_book(self, book_id):
      try:
          sql = "DELETE FROM book_info WHERE book_id=%s"
          self.cursor.execute(sql, (book_id,))   # 必须写成元组
          self.conn.commit()
          if self.cursor.rowcount > 0:
              print("✅ 已全部删除")
          else:
              print("❌ 未找到该图书")
      except Exception as e:
          self.conn.rollback()
          print(f"❌ 删除失败: {e}")
      self.write_log(f'删除图书id：{book_id} 信息')
    # 7. 用户登录验证
    def show_user(self, username, password):
        try:
            sql = 'SELECT power FROM admin WHERE username = %s AND password = %s'
            self.cursor.execute(sql, (username, password))
            res = self.cursor.fetchone()
            if res:
                print('已登录')
                self.write_log(f'用户：{username} 登录成功')
                if res['power'] == 'high':
                    print('权限验证成功，当前为管理员账号')
                    return res['power']
                else:
                    print('当前权限为用户账号')
                    return res['power']
            else:
                print('账号或密码错误')
        except Exception as e:
            print(f'查询出错: {e}')
            return None
    
#注册
    def register(self):
        username = input("请输入用户名：")
        password = input("请输入密码：")
        try:
            sql = "INSERT INTO admin (username, password ) VALUES (%s, %s)"
            self.cursor.execute(sql, (username, password))
            self.conn.commit()
            print("✅ 注册成功")
            self.write_log(f'用户：{username} 注册成功')
        except Exception as e:
            self.conn.rollback()
            print(f"❌ 注册失败: {e}")
    
    def search_book_name(self, book_name):
        try:
            sql = """
                SELECT bo.book_id, bo.book_name, bo.status, b.book_kind, b.book_date, b.price, b.wirter
                FROM book_info bo
                LEFT JOIN book_in b ON bo.book_id = b.nid
                WHERE bo.book_name LIKE %s
            """
            self.cursor.execute(sql, (f'%{book_name}%',))
            results = self.cursor.fetchall()
            if not results:
                print("未找到匹配的图书")
                return

            for res in results:
                print(f'''相关书籍：
                    图书编号：{res['book_id']}
                    图书名称：{res['book_name']}
                    图书状态：{res['status']}
                    图书分类：{res['book_kind']}
                    出版日期：{res['book_date']}
                    价格：{res['price']}
                    作者：{res['wirter']}''')
                self.write_log(f"查询了图书:{res['book_name']}的信息")
        except Exception as e:
                        self.conn.rollback()
                        print(f"❌ 查询失败: {e}")

    def search_book_kind(self, book_kind):
        try:
            sql = """
                SELECT bo.book_id, bo.book_name, bo.status, b.book_kind, b.book_date, b.price, b.wirter
                FROM book_info bo
                LEFT JOIN book_in b ON bo.book_id = b.nid
                WHERE b.book_kind LIKE %s
            """
            self.cursor.execute(sql, (f'%{book_kind}%',))
            results = self.cursor.fetchall()

            if not results:
                print("未找到匹配的图书")
                return
            for res in results:
                print(f'''相关书籍：
                    图书编号：{res['book_id']}
                    图书名称：{res['book_name']}
                    图书状态：{res['status']}
                    图书分类：{res['book_kind']}
                    出版日期：{res['book_date']}
                    价格：{res['price']}
                    作者：{res['wirter']}''')
                self.write_log(f"查询了图书:{res['book_name']}的信息")
        except Exception as e:
            self.conn.rollback()
            print(f"❌ 查询失败: {e}")
    def search_book_wirter(self, wirter):
        try:
            sql = """
                SELECT bo.book_id, bo.book_name, bo.status, b.book_kind, b.book_date, b.price, b.wirter
                FROM book_info bo
                LEFT JOIN book_in b ON bo.book_id = b.nid
                WHERE b.wirter LIKE %s
            """
            self.cursor.execute(sql, (f'%{wirter}%',))
            results = self.cursor.fetchall()
            if not results:
                print("未找到匹配的图书")
                return
            for res in results:
                print(f'''相关书籍：
                    图书编号：{res['book_id']}
                    图书名称：{res['book_name']}
                    图书状态：{res['status']}
                    图书分类：{res['book_kind']}
                    出版日期：{res['book_date']}
                    价格：{res['price']}
                    作者：{res['wirter']}''')
                self.write_log(f"查询了图书:{res['book_name']}的信息")
        except Exception as e:
            self.conn.rollback()
            print(f"❌ 查询失败: {e}")
            return
    def borrow_book(self, username, bo_id):
      """借书功能"""
      try:
          sql = "SELECT bo_id FROM borrower WHERE bo_id = %s AND status = '在借'"
          self.cursor.execute(sql, (bo_id,))
          res = self.cursor.fetchone()
          if res:
              print("❌ 该书籍已被借出，暂时无法借阅")
              return

          out_date = datetime.date.today()
          in_date = out_date + datetime.timedelta(days=14)

          sql = """INSERT INTO borrower (br_name, bo_id, out_date, in_date, status)
                   VALUES (%s, %s, %s, %s, '在借')"""
          self.cursor.execute(sql, (username, bo_id, out_date, in_date))

          # 同步更新 book_info 状态
          sql2 = "UPDATE book_info SET status='已借阅' WHERE book_id=%s"
          self.cursor.execute(sql2, (bo_id,))

          self.conn.commit()
          print(f'✅ 用户：{username} {out_date} 借书成功，应还日期：{in_date}')
          self.write_log(f'用户：{username} 借书成功')
      except Exception as e:
          self.conn.rollback()
          print(f"❌ 借书失败: {e}")

    def return_book(self, username, bo_id):
      """还书功能：更新状态为已归还，保留借还记录"""
      try:
          # 查该用户所有在借的书，联查book_info获取书名
          sql = """
              SELECT br.id, br.out_date, br.in_date, br.bo_id, bi.book_name
              FROM borrower br
              LEFT JOIN book_info bi ON br.bo_id = bi.book_id
              WHERE br.br_name = %s AND br.status = '在借'
          """
          self.cursor.execute(sql, (username,))
          borrow_list = self.cursor.fetchall()

          if not borrow_list:
              print(f"\n❌ 用户 {username} 当前没有在借的书")
              return

          # 先打印该用户当前所有在借的书（含书名）
          print(f"\n{'='*62}")
          print(f"  📚 用户【{username}】当前在借图书")
          print(f"{'='*62}")
          for row in borrow_list:
              print(f"  编号：{row['bo_id']:<6} | 《{row['book_name']}》")
              print(f"  借书：{row['out_date']}  ->  应还：{row['in_date']}")
              print(f"  {'-'*56}")
          print(f"  共 {len(borrow_list)} 本在借")
          print(f"{'='*62}")

          # 找到要还的那本书
          found = None
          want_book_name = "未知"
          want_out_date = None
          want_in_date = None
          for row in borrow_list:
              if row['bo_id'] == int(bo_id):
                  found = row['id']
                  want_book_name = row['book_name']
                  want_out_date = row['out_date']
                  want_in_date = row['in_date']
                  break

          if found is None:
              print(f"\n❌ 图书编号 {bo_id} 不在你的借阅列表中")
              return

          # 更新状态为已归还，记录实际归还日期到return_date
          return_date = datetime.date.today()
          sql = "UPDATE borrower SET status = '已归还', return_date = %s WHERE id = %s"
          self.cursor.execute(sql, (return_date, found))

          # 同步更新 book_info 状态为可借阅
          sql2 = "UPDATE book_info SET status='可借阅' WHERE book_id=%s"
          self.cursor.execute(sql2, (bo_id,))

          self.conn.commit()

          # 归还成功，显示摘要
          print(f"\n✅ 还书成功！")
          print(f"  用户：{username}")
          print(f"  归还：《{want_book_name}》（编号：{bo_id}）")
          print(f"  借出：{want_out_date}  |  应还：{want_in_date}  |  实还：{return_date}")

          self.write_log(f'用户：{username} 归还了《{want_book_name}》（编号：{bo_id}），实还：{return_date}')

          # 还完书后，展示该用户的完整借还记录
          self.show_borrow_history(username)

      except Exception as e:
          self.conn.rollback()
          print(f"❌ 还书失败: {e}")

    def show_borrow_history(self, username):
      """查询某用户的完整借还记录：借了哪些书、借书时间、还书时间"""
      try:
          sql = """
              SELECT b.bo_id, bi.book_name, b.out_date, b.in_date, b.return_date, b.status
              FROM borrower b
              LEFT JOIN book_info bi ON b.bo_id = bi.book_id
              WHERE b.br_name = %s
              ORDER BY b.out_date DESC
          """
          self.cursor.execute(sql, (username,))
          records = self.cursor.fetchall()

          if not records:
              print(f"\n📭 用户 {username} 暂无借还记录")
              return

          print(f"\n========== 用户【{username}】借还记录 ==========")
          for r in records:
              return_str = str(r['return_date']) if r['return_date'] else "-"
              print(f"图书编号：{r['bo_id']} | 图书名称：{r['book_name']} | "
                    f"借出日期：{r['out_date']} | 应还日期：{r['in_date']} | "
                    f"实际归还：{return_str} | 状态：{r['status']}")
              print("-" * 100)

          self.write_log(f'查询用户：{username} 的借还记录')

      except Exception as e:
          print(f"❌ 查询借还记录失败: {e}")



  
    def close(self):
        self.cursor.close()
        self.conn.close()
        print("✅ 数据库连接已关闭")
        self.write_log("数据库连接已关闭")


# 主菜单函数
def main():
    sm = BOOKManager()
    while True:
        option = input("请输入操作：1.登录 2.注册")
        if option == '2':
            sm.register()
            continue
        elif option == '1':
            break
    while True:
        user = input("请输入用户名：")
        pw = input("请输入密码：")
        level = sm.show_user(user,pw)
        lit=[]
        power_limit = {'high': [1,2,3,4,5,6,7,0,8,9,10], 'low':[2,3,5,10,8,6,0,9,10]}
        if level == 'high':
            lit = power_limit['high']
        elif level == 'low':
            lit = power_limit['low']
        if lit :  
            break
        else:
            print("❌ 权限验证失败，重新选择操作！")
            continue 
        
    while True:
            print("\n======= 图书管理系统【双表版】=======")

            if 1 in lit:    
                print("1. 添加图书")
            if 2 in lit:
                print("2. 查看所有图书完整信息")
            if 3 in lit:    
                print("3. 按ID查询图书")
            if 4 in lit:
                print("4. 修改图书基础信息")
            if 5 in lit:
                print('5. 借阅图书')
            if 6 in lit:
                print('6. 归还图书')
            if 7 in lit:    
                print("7. 删除图书")
            if 8 in lit:
                print("8. 按图书名称查询图书")
            if 9 in lit:
                print("9. 按图书分类查询图书")
            if 10 in lit:
                print("10. 按作者查询图书")
            if 0 in lit:    
                print("0. 退出系统")
                print("==========================================")

            choice = input("请输入功能编号：")

            if choice == "1" and int(choice) in lit:
                sid = input("请输入图书id：")
                name = input("请输入图书名称：")
                kind = input("请输入分类：")
                c = input("请输入出版日期：")
                m = input("请输入价格：")
                e = input("请输入作者：")
                sm.add_book(sid, name, kind, c, m, e)

            elif choice == "2" and int(choice) in lit:
                sm.show_all_book()

            elif choice == "3" and int(choice) in lit:
                sid = input("请输入查询图书id：")
                sm.search_book_id(sid)

            elif choice == "4" and int(choice) in lit:
                if level == 'high':
                    sid = input("请输入要图书id：")
                    name = input("请输入新名称：")
                    c = input("请输入图书分类：")
                    m = input("请输入出版日期：")
                    e = input("请输入价格：")
                    w = input("请输入作者：")
                    
                    sm.update_book_name(sid, name)
                    sm.update_book_info(sid, c, m, e, w)
                else:
                    print("❌ 权限验证失败，重新选择操作！")

            

            elif choice == "7" and int(choice) in lit:
                if level == 'high':
                    sid = input("请输入要id：")
                    sm.delete_book(sid)
                else:
                    print("❌ 权限验证失败，重新选择操作！")
            elif choice == "0" and int(choice) in lit:
                sm.close()
                print("👋 系统退出成功，再见！")
                break
            
            elif choice == "5" and int(choice) in lit:
                sid = input("请输入要借阅的图书id：")
                sm.borrow_book(user, sid)

            elif choice == "6" and int(choice) in lit:
                sid = input("请输入要归还的图书id：")
                sm.return_book(user, sid)
            elif  choice == "8" and int(choice) in lit:
                book_name = input("请输入要查询的图书名称：")
                sm.search_book_name(book_name)
            elif  choice == "9" and int(choice) in lit:
                book_kind = input("请输入要查询的图书分类：")
                sm.search_book_kind(book_kind)
            elif choice =='10' and int(choice) in lit:
                wirter = input("请输入要查询的作者：")
                sm.search_book_wirter(wirter)
            else:
                print("❌ 输入无效，请正确的操作选择！")
        
            
if __name__ == "__main__":
    main()