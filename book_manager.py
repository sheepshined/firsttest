import pymysql
import time

# 学生管理核心类
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
            sql_score = "INSERT INTO book_in(book_kind, book_date,price,wirter) VALUES(%s,%s,%s,%s)"
            self.cursor.execute(sql_score, (book_kind, book_date,price,wirter))

            self.conn.commit()
            print("✅ 图书信息添加成功")
            self.write_log(f"新增图书：学号{book_id} 姓名{book_name} 并录入成绩")
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
        
        print("\n========== 学生完整信息及成绩列表 ==========")
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
            print("\n========== 学生成绩详情 ==========")
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
            self.cursor.execute(sql, (username, password))  # 参数传入
            res = self.cursor.fetchone()
            if res:
                print('已登录')
                if res['power'] == 'high':        # 取元组第一个元素
                    print('权限验证成功')
                    return res['power']
                else:
                    print('权限验证失败，当前权限低')
                    return res['power']
            else:
                print('账号或密码错误')
        except Exception as e:
            print(f'查询出错: {e}')
            return None
        self.write_log(f'用户：{username} 登录成功')
    
    def jieyue(self, book_id):
      try:
          # 先查状态
          sql1 = 'SELECT status FROM book_info WHERE book_id = %s'
          self.cursor.execute(sql1, (book_id,))
          res = self.cursor.fetchone()          # 必须 fetchone

          if res is None:
              print("❌ 未找到该图书")
              return
          if res['status'] == '可借阅':         # res 是字典，用键取值
              sql = "UPDATE book_info SET status='已借阅' WHERE book_id=%s"
              self.cursor.execute(sql, (book_id,))
              self.conn.commit()
              print("✅ 借阅成功")
          else:
              print("❌ 该图书已被借出")
      except Exception as e:
          self.conn.rollback()
          print(f"❌ 借阅失败: {e}")
      self.write_log(f'用户借阅图书id：{book_id} 信息')

    def guihua(self,book_id):
        try:
          # 先查状态
          sql1 = 'SELECT status FROM book_info WHERE book_id = %s'
          self.cursor.execute(sql1, (book_id,))
          res = self.cursor.fetchone()          # 必须 fetchone

          if res is None:
              print("❌ 未找到该图书")
              return
          if res['status'] == '已借阅':         # res 是字典，用键取值
              sql = "UPDATE book_info SET status='可借阅' WHERE book_id=%s"
              self.cursor.execute(sql, (book_id,))
              self.conn.commit()
              print("✅ 归还成功")
          else:
              print("❌归还失败")
        except Exception as e:
          self.conn.rollback()
          print(f"❌ 该图书还未被借阅: {e}")
        self.write_log(f'用户归还图书id：{book_id} 信息')

    
    def close(self):
        self.cursor.close()
        self.conn.close()
        print("✅ 数据库连接已关闭")
        self.write_log("数据库连接已关闭")


# 主菜单函数
def main():
    sm = BOOKManager()
    
    user = input("请输入用户名：")
    pw = input("请输入密码：")
    level = sm.show_user(user,pw)
    print(level)
    lit=[]
    power_limit = {'high': [1,2,3,4,5,6,7,0], 'low':[3,5,6,0]}
    if level == 'high':
        lit = power_limit['high']

    elif level == 'low':
        lit = power_limit['low']
    print(lit)
    while True:

            print("\n======= 学生信息成绩管理系统【双表版】=======")

            if 1 in lit:    
                print("1. 添加图书（含成绩录入）")
            if 2 in lit:
                print("2. 查看所有图书完整信息")
            if 3 in lit:    
                print("3. 按学号查询图书成绩")
            if 4 in lit:
                print("4. 修改图书基础信息")
            if 5 in lit:    
                print('5. 借阅图书')
            if 6 in lit:    
                print('6. 归还图书')
            if 7 in lit:    
                print("7. 删除图书（含信息）")
            if 0 in lit:    
                print("0. 退出系统")
                print("==========================================")

            choice = input("请输入功能编号：")

            if choice == "1":
                sid = input("请输入图书id：")
                name = input("请输入图书名称：")
                kind = input("请输入分类：")
                c = input("请输入出版日期：")
                m = input("请输入价格：")
                e = input("请输入作者：")
                sm.add_book(sid, name, kind, c, m, e)

            elif choice == "2":
                sm.show_all_book()

            elif choice == "3":
                sid = input("请输入查询图书id：")
                sm.search_book_id(sid)

            elif choice == "4":
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

            

            elif choice == "7":
                if level == 'high':
                    sid = input("请输入要id：")
                    sm.delete_book(sid)
                else:
                    print("❌ 权限验证失败，重新选择操作！")
            elif choice == "0":
                sm.close()
                print("👋 系统退出成功，再见！")
                break
            
            elif choice == "5":

                sid = input("请输入要借阅的图书id：")

                sm.jieyue(sid)
            elif    choice == "6":

                sid = input("请输入要归还的图书id：")

                sm.guihua(sid)
            else:
                print("❌ 输入无效，请输入0-6的数字！")

            
if __name__ == "__main__":
    main()