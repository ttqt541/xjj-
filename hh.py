import pulp as lp


def production_optimization():
    # ===================== 1. 定义业务参数（请替换为工厂实际数据）=====================
    # 产品/机器名称（可自定义）
    products = ["产品1", "产品2", "产品3"]
    machines = ["机器1", "机器2"]

    # 核心参数：单位产品生产时间（小时/单位）、单位生产成本（元/单位）
    unit_time = {"产品1": 2, "产品2": 3, "产品3": 1}  # 生产1单位产品所需时间
    unit_cost = {"产品1": 10, "产品2": 15, "产品3": 8}  # 生产1单位产品的成本

    # 机器每日可用时间（小时）
    machine_available_time = {"机器1": 8, "机器2": 8}

    # 产品-机器适配矩阵：1=可生产，0=不可生产（确保每个产品至少对应1台机器）
    product_machine_matrix = {
        "产品1": {"机器1": 1, "机器2": 1},
        "产品2": {"机器1": 1, "机器2": 0},
        "产品3": {"机器1": 0, "机器2": 1}
    }

    # 权重参数：alpha∈[0,1]，越大越看重订单量，越小越看重成本
    # 【关键修正】先设为1（只最大化订单量），验证有解后再调低
    alpha = 1.0  # 优先保证有非零解，后续可调整为0.7/0.8等

    # ===================== 2. 参数校验（新增：避免因参数错误导致全0）=====================
    # 检查每个产品是否至少对应1台可生产的机器
    for p in products:
        machine_count = sum(product_machine_matrix[p][m] for m in machines)
        if machine_count == 0:
            print(f"⚠️ 警告：{p} 没有可生产的机器，请检查product_machine_matrix！")
            return

    # 检查机器可用时间是否为正
    for m in machines:
        if machine_available_time[m] <= 0:
            print(f"⚠️ 警告：{m} 可用时间为0或负数，请检查machine_available_time！")
            return

    # ===================== 3. 构建线性规划模型 =====================
    # 创建问题实例：LpMaximize表示最大化目标函数
    prob = lp.LpProblem("ProductionOptimization", lp.LpMaximize)

    # 定义决策变量：各产品生产数量（整数、非负）
    x = lp.LpVariable.dicts(
        "ProductionQuantity",  # 变量名前缀
        products,  # 变量索引（对应产品）
        lowBound=0,  # 下界：生产数量不能为负
        cat=lp.LpInteger  # 变量类型：整数（允许半产品则改为LpContinuous）
    )

    # 【关键修正】优化目标函数：先纯最大化订单量（alpha=1），验证有解后再加入成本项
    # 若要同时考虑成本，建议对成本做归一化（避免成本数值过大覆盖订单量）
    if alpha == 1.0:
        # 纯最大化订单量
        objective = lp.lpSum([x[p] for p in products])
    else:
        # 加权目标：订单量（归一化） - 成本（归一化），平衡量级
        total_possible_quantity = sum(machine_available_time[m] // min(unit_time.values()) for m in machines)
        max_cost = max(unit_cost.values())
        objective = alpha * (lp.lpSum([x[p] for p in products]) / total_possible_quantity) - \
                    (1 - alpha) * (lp.lpSum([unit_cost[p] * x[p] for p in products]) / (
                    total_possible_quantity * max_cost))

    prob += objective, "WeightedObjective"

    # 添加约束：每台机器的总生产时间 ≤ 每日可用时间
    for m in machines:
        time_constraint = lp.lpSum([product_machine_matrix[p][m] * unit_time[p] * x[p] for p in products]) <= \
                          machine_available_time[m]
        prob += time_constraint, f"MachineTimeConstraint_{m}"

    # ===================== 4. 求解模型并输出结果 =====================
    # 调用内置求解器（设置日志级别，方便排查）
    status = prob.solve(lp.PULP_CBC_CMD(msg=0))  # msg=0关闭冗余日志

    # 输出求解状态与生产方案
    print("求解状态:", lp.LpStatus[status])  # Optimal=最优解，Infeasible=无解
    if lp.LpStatus[status] != "Optimal":
        print("❌ 模型无可行解，请检查约束条件或参数！")
        return

    print("=" * 50)
    print("最优生产方案：")
    total_quantity = 0  # 总订单完成量
    total_cost = 0  # 总成本
    has_non_zero = False
    for p in products:
        quantity = x[p].varValue  # 该产品的最优生产数量
        cost = unit_cost[p] * quantity
        total_quantity += quantity
        total_cost += cost
        print(f"{p}: 生产 {quantity} 单位，成本 {cost} 元")
        if quantity > 0:
            has_non_zero = True

    if not has_non_zero:
        print("⚠️ 警告：所有产品生产数量为0！建议：")
        print("  1. 将alpha调大（如1.0），优先最大化订单量")
        print("  2. 检查机器可用时间是否过小")
        print("  3. 检查产品生产时间是否过大")

    print("=" * 50)
    print(f"总订单完成量：{total_quantity} 单位")
    print(f"总成本：{total_cost} 元")
    print(f"加权目标函数值：{lp.value(prob.objective):.2f}")


# 执行优化函数
if __name__ == "__main__":
    production_optimization()