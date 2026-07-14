from __future__ import annotations

import argparse
import ast
from collections import Counter
import json
from typing import Sequence

from .de_r1 import de_r1

# 检查 pd_code 是否合法
# 不考虑平面图条件
def arc_index_checker(pd_code) -> bool:
    if not isinstance(pd_code, (list, tuple)):
        return False
    counts = Counter()
    for item in pd_code:
        if not isinstance(item, (list, tuple)):
            return False
        if len(item) != 4:
            return False
        for arc_index in item:
            if isinstance(arc_index, bool) or not isinstance(arc_index, int) or arc_index <= 0:
                return False
            counts[arc_index] += 1
    expected = set(range(1, 2 * len(pd_code) + 1))
    return set(counts) == expected and all(count == 2 for count in counts.values())

# 获得后继（默认后继 +1，特殊处理最大值位置）
def get_nxt_arc_number(b, blk, fa) -> int:
    v = fa[b]
    if b == max(blk[v]):
        ans = min(blk[v])
    else:
        ans = b + 1
    return ans

# 获得前驱
def get_lst_arc_number(a, blk, fa) -> int:
    v = fa[a]
    if a == min(blk[v]):
        return max(blk[v])
    else:
        return a - 1

def get_a(a, i, j, m, n, blk, fa):
    if i != n:
        return (a + j*m, i)
    else:
        return (get_nxt_arc_number(a, blk, fa) + j*m, 0)
    
def get_b(b, i, j, m, n, blk, fa):
    return get_a(b, j, i, m, n, blk, fa)

# 获取交叉点矩阵
def get_crossing_matrix_for_item(item, blk, fa, m, n):
    b, a, bp, ap = item
    if bp != get_nxt_arc_number(b, blk, fa):
        raise ValueError(f"the third label must follow the first label along its component: {item!r}")
    previous_a = get_lst_arc_number(a, blk, fa)
    next_a = get_nxt_arc_number(a, blk, fa)
    if ap not in (previous_a, next_a):
        raise ValueError(
            f"the fourth label must be adjacent to the second label along its component: {item!r}"
        )
    arr = []
    for i in range(n):
        for j in range(n):
            if ap == previous_a: # 减小方向 [b, a+1, b+1, a]
                arr.append([
                    get_b( b,   i,   j, m, n, blk, fa), 
                    get_a(ap, i+1,   j, m, n, blk, fa), 
                    get_b( b,   i, j+1, m, n, blk, fa), 
                    get_a(ap,   i,   j, m, n, blk, fa)
                ])
            else: # 增大方向 [b, a, b+1, a+1]
                arr.append([
                    get_b(b,   i,   j, m, n, blk, fa), 
                    get_a(a,   i,   j, m, n, blk, fa), 
                    get_b(b,   i, j+1, m, n, blk, fa), 
                    get_a(a, i+1,   j, m, n, blk, fa)
                ])
    return arr

# 合并两个连通块
# 直接在 dic 上进行修改
def merge_dic_term(dic, x, y):
    if x == y:
        return
    merged_list = dic[x] + dic[y]
    dic[x] = []
    dic[y] = []
    dic[min(x, y)] = sorted(merged_list)

def find(fa, x): # 路径压缩并查集
    if fa[x] == x:
        return x
    else:
        root  = find(fa, fa[x])
        fa[x] = root
        return root

# 合并连通块
def merge(fa: dict, a, b):
    a = find(fa, a)
    b = find(fa, b)
    fa[max(a, b)] = fa[min(a, b)]

# 获得所有联通分支以及并查集
def get_componets(pd_code):
    fa  = {}
    blk = {}
    for item in pd_code:
        for v in item:
            fa[v]  = v
            blk[v] = []
    for item in pd_code:
        a, b, c, d = item
        merge(fa, a, c)
        merge(fa, d, b)
    for v in fa: # 拍扁并查集
        find(fa, v)
    for v in fa:
        blk[fa[v]].append(v)
    for v in blk:
        blk[v] = sorted(blk[v])
        if blk[v] and blk[v] != list(range(blk[v][0], blk[v][-1] + 1)):
            raise ValueError(
                "labels for each oriented component must form one consecutive integer interval"
            )
    return blk, fa

# 对所有 arc 进行重新编号
def renumbering(arr) -> list:
    all_id= []
    for item in arr:
        for term in item:
            if term not in all_id:
                all_id.append(term)
    all_id  = sorted(all_id)
    get_new_idx = {
        old_id: new_id + 1
        for new_id, old_id in enumerate(all_id)
    }
    new_pd_code = []
    for old_item in arr:
        new_item = []
        for old_term in old_item:
            new_item.append(get_new_idx[old_term])
        new_pd_code.append(new_item)
    return new_pd_code

# 计算扭结的
def n_parallel(pd_code: list, n: int):
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer")
    if not arc_index_checker(pd_code):
        raise ValueError(
            "PD code must contain four positive integers per crossing and labels 1..2c exactly twice"
        )
    pd_code = [list(item) for item in pd_code]
    if not pd_code:
        return []
    # The historical operation is an n-parallel/doubling construction. Remove
    # explicit R1 kinks first so equivalent diagrams that differ only by those
    # kinks do not acquire different blackboard twists.
    pd_code = de_r1(pd_code)
    if not pd_code:
        return []
    m       = len(pd_code) * 2       # 记录弧线总段数
    blk, fa = get_componets(pd_code) # 记录连通块以及并查集
    arr = []
    for item in pd_code:
        arr += get_crossing_matrix_for_item(item, blk, fa, m, n)
    return renumbering(arr)


def _parse_pd_code(text: str) -> list[list[int]]:
    try:
        value = ast.literal_eval(text)
    except (SyntaxError, ValueError) as exc:
        raise ValueError("PD code must be a Python/JSON-style nested list") from exc
    if not isinstance(value, list):
        raise ValueError("PD code must be a nested list")
    return value


def cli(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute the n-parallel of a PD code.")
    parser.add_argument("n", type=int, help="positive parallel multiplicity")
    parser.add_argument("pd_code", help="PD code in [[...], ...] form")
    args = parser.parse_args(argv)
    try:
        result = n_parallel(_parse_pd_code(args.pd_code), args.n)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, separators=(",", ":")))
    return 0

if __name__ == "__main__":
    raise SystemExit(cli())
