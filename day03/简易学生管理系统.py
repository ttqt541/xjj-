Stu={}
while True:
    try:
        s =int( input(
        "输入数字1到5    1的时候表示添加学生 2的时候表示查询学生 3的时候表示修改学生  4的时候表示删除学生  5的时候表示退出系统"))
    except ValueError:
        print("请输入有效数字")
        continue
    if s==5:
        print("该系统已退出")
        break


    if s==1:
        print("开始添加学生")
        n=input("输入学生名字")
        if n in Stu:
            print("该学生已存在")
        else:
            score=float(input("输入学生的分数"))
            Stu[n]=score
            print("添加成功")
    if  s==2:
        print("开始修改学生")
        Na=input("请输入修改学生的姓名")
        if Na in Stu:
            fen=float(input("输入学生需要的分数"))
        else:
            print("该学生不存在请先添加")
    if s==3:
        print("开始查询")
        name=input("输入需查找的学生姓名")
        if name in Stu:
            print(Stu[name])
        else:
            print("该学生不存在")
    if s==4:
        print("开始删除")
        Name=input("请输入删除学生姓名")
        if Name in Stu:
            del Stu[Name]
print(Stu)