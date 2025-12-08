"""
配送路径规划功能快速演示
展示核心算法和距离计算
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))


def demo_distance_calculation():
    """演示距离计算"""
    print("=" * 60)
    print("1. 距离计算演示")
    print("=" * 60)
    
    from amap import AmapService
    
    # 上海市内几个地标
    locations = {
        "浦东机场": (121.805214, 31.143378),
        "人民广场": (121.475266, 31.231763),
        "虹桥机场": (121.336319, 31.197875),
        "外滩": (121.490317, 31.240022),
        "迪士尼": (121.669543, 31.145157)
    }
    
    print("\n上海地标位置:")
    for name, (lon, lat) in locations.items():
        print(f"  {name}: ({lon:.6f}, {lat:.6f})")
    
    print("\n距离矩阵（直线距离）:")
    print("%-12s" % "", end="")
    for name in locations:
        print("%-12s" % name, end="")
    print()
    
    for name1, (lon1, lat1) in locations.items():
        print("%-12s" % name1, end="")
        for name2, (lon2, lat2) in locations.items():
            if name1 == name2:
                print("%-12s" % "-", end="")
            else:
                dist = AmapService.calculate_distance_haversine(lon1, lat1, lon2, lat2)
                print("%-12s" % AmapService.format_distance(dist), end="")
        print()


def demo_greedy_algorithm():
    """演示贪心最近邻算法"""
    print("\n" + "=" * 60)
    print("2. 贪心最近邻算法演示")
    print("=" * 60)
    
    from amap import _tsp_greedy_nearest_neighbor, AmapService
    
    # 简单测试数据（上海市内配送点）
    locations = [
        ("仓库", 121.48, 31.23),      # 起点
        ("药店A", 121.50, 31.22),
        ("药店B", 121.51, 31.21),
        ("药店C", 121.49, 31.24),
        ("药店D", 121.52, 31.23)
    ]
    
    print("\n配送点位置:")
    for i, (name, lon, lat) in enumerate(locations):
        print(f"  点{i} - {name}: ({lon:.6f}, {lat:.6f})")
    
    # 构建距离矩阵
    n = len(locations)
    matrix = [[0.0] * n for _ in range(n)]
    
    for i in range(n):
        for j in range(i + 1, n):
            dist = AmapService.calculate_distance_haversine(
                locations[i][1], locations[i][2],
                locations[j][1], locations[j][2]
            )
            matrix[i][j] = dist
            matrix[j][i] = dist
    
    print("\n距离矩阵:")
    for i in range(n):
        print(f"  点{i}: " + " ".join(f"{d:>8.0f}" for d in matrix[i]))
    
    # 运行贪心算法
    route = _tsp_greedy_nearest_neighbor(matrix)
    
    print("\n贪心算法结果:")
    print(f"  访问顺序: 0 (起点) -> " + " -> ".join(str(p) for p in route))
    print(f"  路径详情:")
    
    current = 0
    total_distance = 0
    
    for i, next_point in enumerate(route):
        dist = matrix[current][next_point]
        total_distance += dist
        print(f"    {i+1}. {locations[current][0]} -> {locations[next_point][0]}: "
              f"{AmapService.format_distance(dist)}")
        current = next_point
    
    print(f"\n  总距离: {AmapService.format_distance(total_distance)}")


def demo_dynamic_programming():
    """演示动态规划算法"""
    print("\n" + "=" * 60)
    print("3. 动态规划精确算法演示")
    print("=" * 60)
    
    from amap import _tsp_dynamic_programming, _tsp_greedy_nearest_neighbor, AmapService
    
    # 使用较小的数据集（动态规划对大数据集性能较差）
    locations = [
        ("仓库", 121.48, 31.23),      # 起点
        ("药店A", 121.50, 31.22),
        ("药店B", 121.51, 31.21),
        ("药店C", 121.49, 31.24)
    ]
    
    print("\n配送点位置:")
    for i, (name, lon, lat) in enumerate(locations):
        print(f"  点{i} - {name}: ({lon:.6f}, {lat:.6f})")
    
    # 构建距离矩阵
    n = len(locations)
    matrix = [[0.0] * n for _ in range(n)]
    
    for i in range(n):
        for j in range(i + 1, n):
            dist = AmapService.calculate_distance_haversine(
                locations[i][1], locations[i][2],
                locations[j][1], locations[j][2]
            )
            matrix[i][j] = dist
            matrix[j][i] = dist
    
    # 运行两种算法对比
    route_greedy = _tsp_greedy_nearest_neighbor(matrix)
    route_dp = _tsp_dynamic_programming(matrix)
    
    def calculate_total_distance(route, matrix):
        current = 0
        total = 0
        for next_point in route:
            total += matrix[current][next_point]
            current = next_point
        return total
    
    greedy_distance = calculate_total_distance(route_greedy, matrix)
    dp_distance = calculate_total_distance(route_dp, matrix)
    
    print("\n贪心算法:")
    print(f"  顺序: 0 -> " + " -> ".join(str(p) for p in route_greedy))
    print(f"  总距离: {AmapService.format_distance(greedy_distance)}")
    
    print("\n动态规划算法（最优解）:")
    print(f"  顺序: 0 -> " + " -> ".join(str(p) for p in route_dp))
    print(f"  总距离: {AmapService.format_distance(dp_distance)}")
    
    if greedy_distance == dp_distance:
        print("\n✓ 贪心算法找到了最优解！")
    else:
        improvement = (greedy_distance - dp_distance) / greedy_distance * 100
        print(f"\n动态规划比贪心算法优化了 {improvement:.2f}%")


def demo_optimize_delivery_route():
    """演示完整路径优化流程"""
    print("\n" + "=" * 60)
    print("4. 完整路径优化演示")
    print("=" * 60)
    
    from amap import optimize_delivery_route
    
    # 仓库位置
    warehouse = (121.48, 31.23)
    
    # 配送目的地列表
    destinations = [
        {"name": "徐汇药店", "longitude": 121.50, "latitude": 31.22},
        {"name": "静安药店", "longitude": 121.51, "latitude": 31.21},
        {"name": "黄浦药店", "longitude": 121.49, "latitude": 31.24},
        {"name": "长宁药店", "longitude": 121.52, "latitude": 31.23},
        {"name": "杨浦药店", "longitude": 121.47, "latitude": 31.25}
    ]
    
    print("\n仓库位置: ({:.6f}, {:.6f})".format(warehouse[0], warehouse[1]))
    print("\n待配送药店:")
    for i, dest in enumerate(destinations, 1):
        print(f"  {i}. {dest['name']}: ({dest['longitude']:.6f}, {dest['latitude']:.6f})")
    
    # 使用贪心算法优化
    print("\n正在优化路径（贪心算法）...")
    optimized_route = optimize_delivery_route(
        warehouse, 
        destinations, 
        use_api=False, 
        algorithm='greedy'
    )
    
    print("\n优化后的配送顺序:")
    total_distance = 0
    
    for dest in optimized_route:
        print(f"  {dest['order']}. {dest['name']}")
        print(f"     位置: ({dest['longitude']:.6f}, {dest['latitude']:.6f})")
        print(f"     距上一点: {dest['distance_from_prev_text']}")
        total_distance += dest['distance_from_prev']
    
    print(f"\n总配送距离: {total_distance/1000:.2f} 公里")
    
    # 对比动态规划
    print("\n正在计算最优解（动态规划算法）...")
    optimized_route_dp = optimize_delivery_route(
        warehouse,
        destinations,
        use_api=False,
        algorithm='dp'
    )
    
    total_distance_dp = sum(d['distance_from_prev'] for d in optimized_route_dp)
    print(f"动态规划总距离: {total_distance_dp/1000:.2f} 公里")
    
    if abs(total_distance - total_distance_dp) < 10:
        print("\n✓ 两种算法结果一致，贪心算法已找到最优解！")
    else:
        improvement = (total_distance - total_distance_dp) / total_distance * 100
        print(f"\n动态规划相比贪心算法优化了 {improvement:.2f}%")


def demo_performance_comparison():
    """演示性能对比"""
    print("\n" + "=" * 60)
    print("5. 算法性能对比")
    print("=" * 60)
    
    import time
    from amap import AmapService, _tsp_greedy_nearest_neighbor, _tsp_dynamic_programming
    
    # 测试不同规模的数据
    test_sizes = [5, 8, 10, 12, 15]
    
    print("\n配送点数量 | 贪心算法耗时 | 动态规划耗时 | 速度比")
    print("-" * 60)
    
    for n in test_sizes:
        # 生成随机坐标点
        import random
        locations = [(121.48 + random.uniform(-0.1, 0.1), 
                     31.23 + random.uniform(-0.1, 0.1)) 
                     for _ in range(n)]
        
        # 构建距离矩阵
        matrix = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                dist = AmapService.calculate_distance_haversine(
                    locations[i][0], locations[i][1],
                    locations[j][0], locations[j][1]
                )
                matrix[i][j] = dist
                matrix[j][i] = dist
        
        # 测试贪心算法
        start_time = time.time()
        _tsp_greedy_nearest_neighbor(matrix)
        greedy_time = time.time() - start_time
        
        # 测试动态规划
        start_time = time.time()
        _tsp_dynamic_programming(matrix)
        dp_time = time.time() - start_time
        
        print(f"{n:>12} | {greedy_time*1000:>13.2f}ms | {dp_time*1000:>14.2f}ms | {dp_time/greedy_time:>6.1f}x")
    
    print("\n建议:")
    print("  • 配送点 ≤ 10 个: 使用动态规划算法（精确最优）")
    print("  • 配送点 > 10 个: 使用贪心算法（快速、效果好）")


if __name__ == '__main__':
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "配送路径规划功能演示" + " " * 15 + "║")
    print("╚" + "═" * 58 + "╝")
    print("\n")
    
    # 运行各个演示
    demo_distance_calculation()
    demo_greedy_algorithm()
    demo_dynamic_programming()
    demo_optimize_delivery_route()
    demo_performance_comparison()
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)
    print("\n提示:")
    print("  1. 运行 'python test_dispatch.py' 进行完整的单元测试")
    print("  2. 启动后端服务后访问前端 '/service' 页面体验可视化功能")
    print("  3. 查看 DISPATCH_ROUTE_PLANNING_GUIDE.md 了解详细使用说明")
    print()
