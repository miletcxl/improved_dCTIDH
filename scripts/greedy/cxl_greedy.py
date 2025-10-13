#!/usr/bin/env python3

# ==============================================================================
# dCTIDH-H 精细化成本优化器 & Strategy 生成器
# ==============================================================================
#
# 版本说明:
# - 融合了 dCTIDH-H 的分层优化框架与 greedyriver.py 的精细化成本模型。
# - 核心成本使用动态规划算法进行精确计算。
# - 总成本包含核心计算成本和协议开销（余因子、求逆等）。
# - 在找到最优分组后，会为该分组生成最终的 C-style strategy 数组。
#
# ==============================================================================

import math
import logging
from functools import lru_cache
from multiprocessing import Pool
import sys
import copy
import numpy as np

# --- 全局常量与配置 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TOTAL_PRIMES_N = 226  # 可以调整以进行测试, e.g., 67
MIN_SECURITY_BITS = 221
PARALLELISM = 4       # 根据你的 CPU 核心数调整
K_RANGE = range(9, 14) # 探索的分组数量范围
MAX_ITER_MACRO = 50  # 宏观搜索的最大迭代次数
MAX_ITER_MICRO = 20  # 微观微调的最大迭代次数

# ==============================================================================
# 占位符模块：请用您的实际代码替换这些函数
# ==============================================================================

class Placeholder:
    """
    这个类包含了所有来自外部模块的占位符函数。
    这些函数返回合理但简化的值，以确保脚本可以完整运行。
    为了获得精确结果，您必须用您自己的 `costisog`, `chain` 模块替换它们。
    """
    @staticmethod
    def costisog_dac(ell):
        """占位符：来自 costisog.py。计算差分加法链的成本。"""
        return 2 * ell  # 简单线性估算

    @staticmethod
    def costisog_isog_matryoshka(l_min, l_max, push):
        """占位符：来自 costisog.py。计算 Matryoshka 同源成本。"""
        base_cost = (l_min + l_max) * 2
        eval_cost = (l_max - l_min) * 1.5
        if push == 0: return base_cost
        return base_cost + eval_cost * (push or 1)
        
    @staticmethod
    def costisog_xDBL():
        """占位符：来自 costisog.py。返回点加倍的成本。"""
        return 6

    @staticmethod
    def chain_cost2(chain):
        """占位符：来自 chain.py。返回链的成本（乘法和平方次数）。"""
        return (len(str(bin(chain))) * 2, len(str(bin(chain))) * 1.5)

# --- 使用占位符 ---
dac = Placeholder.costisog_dac
isog_matryoshka = Placeholder.costisog_isog_matryoshka
xDBL = Placeholder.costisog_xDBL
chain_cost2 = Placeholder.chain_cost2


# ==============================================================================
# 动态规划 Strategy 生成器 (替换原占位符)
# ==============================================================================

def memoized(func):
    """简单的 LRU 缓存装饰器"""
    return lru_cache(maxsize=4096)(func)

@memoized
def dac_search(target,r0,r1,r2,chain,chainlen,best,bestlen):
  if chainlen >= bestlen: return best,bestlen
  if r2 > target: return best,bestlen
  if r2<<(bestlen-1-chainlen) < target: return best,bestlen
  if (r2 == target): return chain,chainlen
  chain *= 2; chainlen += 1
  best,bestlen = dac_search(target,r0,r2,r0+r2,chain+1,chainlen,best,bestlen)
  best,bestlen = dac_search(target,r1,r2,r1+r2,chain,chainlen,best,bestlen)
  return best,bestlen

@memoized
def daclen(target):
  best = None; bestlen = -1
  while best == None:
    bestlen += 1
    best, bestlen = dac_search(target,1,2,3,0,0,best,bestlen)
  return bestlen

@lru_cache(maxsize=4096)
def dynamic_programming_algorithm(L_tuple, C_dac_tuple, C_isog_tuple, C_eval_tuple):
    """
    动态规划算法，用于为给定的素数批次找到最优的计算策略和成本。
    输入必须是元组才能被缓存。
    """
    L = list(L_tuple)
    C_xMUL = list(C_dac_tuple)
    C_xISOG = list(C_isog_tuple)
    C_xEVAL = list(C_eval_tuple)
    n = len(L)
    if n == 0: return [], 0.0

    S, C = {1: {}}, {1: {}}
    for i in range(n):
        S[1][(L[i],)] = []
        C[1][(L[i],)] = C_xISOG[i]

    get_neighboring_sets = lambda lst, k: [tuple(lst[i:i+k]) for i in range(len(lst)-k+1)]
                                                      
    for i in range(2, n + 1):
        C[i], S[i] = {}, {}
        for tpl in get_neighboring_sets(L, i):
            # 为了缓存，将列表索引转换为值索引
            # 注意：这假设批次内没有重复的素数，在dCTIDH中这是成立的
            L_indices = {prime: idx for idx, prime in enumerate(L)}

            alpha = []
            for b in range(1, i):
                cost = (C[b][tpl[:b]] + C[i-b][tpl[b:]] +
                        sum(C_xMUL[L_indices[t]] for t in tpl[:b]) +
                        sum(C_xEVAL[L_indices[t]] for t in tpl[b:]) +
                        sum(C_xMUL[L_indices[t]] for t in tpl[b:]))
                alpha.append((b, cost))
            
            # 找到成本最小的分割点
            best_b, min_cost = min(alpha, key=lambda t: t[1])
            C[i][tpl] = min_cost
            
            # 构建策略
            # 策略格式：[分割点, 左子策略, 右子策略]
            left_strategy = S[i-best_b][tpl[best_b:]]
            right_strategy = S[best_b][tpl[:best_b]]
            S[i][tpl] = [best_b] + left_strategy + right_strategy

    final_tuple = tuple(L)
    return S[n][final_tuple], C[n][final_tuple]

# ==============================================================================
# 数据与函数 (源自 greedyriver.py)
# ==============================================================================
first_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997, 1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091, 1093, 1097, 1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187, 1193, 1201, 1213, 1217, 1223, 1229, 1231, 1237, 1249, 1259, 1277, 1279, 1283, 1289, 1291, 1297, 1301, 1303, 1307, 1319, 1321, 1327, 1361, 1367, 1373, 1381, 1399, 1409, 1423, 1427, 1429]
cofactors = {226:((68),[]),221:((115),[3])} # 简化版 cofactor

M = S = 1
def sqrt_cost(p):
    sqrtchain = (p + 1) // 4; sqrtchaincost = chain_cost2(sqrtchain)
    return sqrtchaincost[0] + (sqrtchaincost[1] + 1)
def elligator_cost(p): return S + M * 6 + sqrt_cost(p)
def inv_cost(p):
    invchain = p - 2; invchaincost = chain_cost2(invchain)
    return invchaincost[0] + invchaincost[1]

@lru_cache(maxsize=None)
def batch_daccost(primes_tuple):
    if not primes_tuple: return 0
    return max([dac(l) for l in primes_tuple])

@lru_cache(maxsize=None)
def batchkeys_wombat(N, M):
    if N < 0 or M < 0 or M > N: return 0
    return sum(math.comb(N, j) * (2**j) for j in range(M + 1))

def security_dCTIDH_H(k, M_H, total_log2_KS_L1):
    if k < M_H or M_H <= 0: return 0
    try: log2_C_k_MH = math.log2(math.comb(k, M_H))
    except ValueError: return 0
    return log2_C_k_MH + total_log2_KS_L1

@lru_cache(maxsize=4096)
def calculate_detailed_batch_cost(batch_primes_tuple, M_i):
    batch_primes = list(batch_primes_tuple)
    if M_i == 0 or not batch_primes: return 0, []
    n = len(batch_primes)
    if M_i > n: M_i = n
    L_max = batch_primes[n - M_i:]; L_max.reverse()
    L_min = batch_primes[:M_i]
    dac_cost = batch_daccost(batch_primes_tuple)
    C_mul, C_isog, C_eval = [dac_cost] * M_i, [], []
    for l_min, l_max in zip(L_min, L_max):
        ic = isog_matryoshka(l_min, l_max, 0)
        ice = isog_matryoshka(l_min, l_max, 1)
        C_isog.append(ic); C_eval.append(ice - ic)
    C_isog.reverse(); C_eval.reverse()
    
    # 调用真实的DP算法
    strategy, cost = dynamic_programming_algorithm(tuple(L_max), tuple(C_mul), tuple(C_isog), tuple(C_eval))
    return cost, strategy

def calculate_total_overhead_cost(n_primes, all_primes_list):
    if n_primes not in cofactors: return 0
    f = cofactors[n_primes]
    cofactor_cost = 2 * xDBL() * f[0] + 2 * sum([dac(p) for p in f[1]])
    try: p_minus_1 = (2**f[0] * math.prod(f[1]) * math.prod(all_primes_list[:n_primes])) - 1
    except (OverflowError, ValueError): return cofactor_cost
    final_inv = inv_cost(p_minus_1) + 1
    point_ops = elligator_cost(p_minus_1)
    return cofactor_cost + final_inv + point_ops

# ==============================================================================
# 核心优化算法 v2.1 - 支持可变 M_i
# ==============================================================================
def find_best_config_for_grouping(grouping, all_primes):
    k = len(grouping)
    best_config_for_grouping = {'cost': float('inf')}
    prime_groups = [[all_primes[i] for i in grp_indices] for grp_indices in grouping]
    
    batch_data = []
    for i, grp_primes in enumerate(prime_groups):
        if not grp_primes: continue
        group_info = {'id': i, 'size': len(grp_primes), 'primes': grp_primes, 'options': []}
        options = []
        for mi in range(1, len(grp_primes) + 1):
            cost, _ = calculate_detailed_batch_cost(tuple(grp_primes), mi) # 忽略strategy
            keyspace = batchkeys_wombat(len(grp_primes), mi)
            log2_ks = math.log2(keyspace) if keyspace > 0 else 0
            options.append({'mi': mi, 'cost': cost, 'log2_ks': log2_ks})
        
        for j in range(1, len(options)):
            cost_delta = options[j]['cost'] - options[j-1]['cost']
            log2_ks_delta = options[j]['log2_ks'] - options[j-1]['log2_ks']
            options[j]['efficiency'] = cost_delta / log2_ks_delta if log2_ks_delta > 0 else float('inf')
        
        if options:
            options[0]['efficiency'] = options[0]['cost'] / options[0]['log2_ks'] if options[0]['log2_ks'] > 0 else float('inf')

        group_info['options'] = options
        batch_data.append(group_info)

    for M_H in range(k, 3, -1):
        if M_H > len(batch_data): continue
        batch_data.sort(key=lambda b: b['options'][0]['cost'] if b['options'] else float('inf'))
        active_batches_template = copy.deepcopy(batch_data[:M_H])

        current_mi_indices = {b['id']: 0 for b in active_batches_template}
        current_total_cost = sum(b['options'][0]['cost'] for b in active_batches_template)
        current_total_log2_ks = sum(b['options'][0]['log2_ks'] for b in active_batches_template)

        while True:
            current_security = security_dCTIDH_H(k, M_H, current_total_log2_ks)
            
            if current_security >= MIN_SECURITY_BITS:
                if current_total_cost < best_config_for_grouping.get('cost', float('inf')):
                    # 重新从 template 构建 active_batches 以包含所有信息
                    active_batches = [next(b for b in batch_data if b['id'] == ab_temp['id']) for ab_temp in active_batches_template]
                    final_mi_list = [b['options'][current_mi_indices[b['id']]]['mi'] for b in active_batches]
                    
                    best_config_for_grouping = {
                        'cost': current_total_cost, 'M_H': M_H, 'k': k,
                        'total_isogenies': sum(final_mi_list), 'security': current_security,
                        'group_sizes': [len(g) for g in grouping],
                        'mi_list': final_mi_list,
                        'active_batches_config': [
                            {'id': b['id'], 'size': b['size'], 'primes': b['primes'], 'mi': final_mi_list[idx]}
                            for idx, b in enumerate(active_batches)
                        ]
                    }
                break

            best_upgrade = {'efficiency': float('inf'), 'batch_id': -1, 'next_mi_idx': -1}
            for batch in active_batches_template:
                current_idx = current_mi_indices[batch['id']]
                if current_idx + 1 < len(batch['options']):
                    next_option = batch['options'][current_idx + 1]
                    if next_option['efficiency'] < best_upgrade['efficiency']:
                        best_upgrade = {'efficiency': next_option['efficiency'], 'batch_id': batch['id'], 'next_mi_idx': current_idx + 1}
            if best_upgrade['batch_id'] == -1: break
            
            batch_to_upgrade = next(b for b in active_batches_template if b['id'] == best_upgrade['batch_id'])
            old_idx = current_mi_indices[best_upgrade['batch_id']]
            new_idx = best_upgrade['next_mi_idx']
            current_total_cost += batch_to_upgrade['options'][new_idx]['cost'] - batch_to_upgrade['options'][old_idx]['cost']
            current_total_log2_ks += batch_to_upgrade['options'][new_idx]['log2_ks'] - batch_to_upgrade['options'][old_idx]['log2_ks']
            current_mi_indices[best_upgrade['batch_id']] = new_idx
    return best_config_for_grouping

def build_groups_from_sizes(sizes, n_primes):
    """根据大小列表构建分组索引列表"""
    groups = []
    indices = list(range(n_primes))
    start_idx = 0
    for size in sizes:
        if size <= 0: return None # 无效的大小
        groups.append(indices[start_idx : start_idx + size])
        start_idx += size
    if start_idx != n_primes: return None # 总和不匹配
    return groups

def macro_search_by_adjusting_sizes(initial_group_sizes, all_primes):
    """
    阶段一：宏观搜索。直接优化分组大小的列表，以进行大范围的结构性搜索。
    """
    k = len(initial_group_sizes)
    n = len(all_primes)
    current_sizes = list(initial_group_sizes)
    
    initial_groups = build_groups_from_sizes(current_sizes, n)
    best_config = find_best_config_for_grouping(initial_groups, all_primes)
    logging.info(f"  k={k} [Macro-Search] 初始分组大小: {current_sizes}, 初始核心成本: {best_config.get('cost', 'N/A')}")
    
    for iter_num in range(MAX_ITER_MACRO):
        improved = False
        
        # 尝试将大小从批次 i 移动到批次 j
        for i in range(k):
            for j in range(k):
                if i == j or current_sizes[i] <= 5: # 不从太小的组移出
                    continue
                
                neighbor_sizes = list(current_sizes)
                neighbor_sizes[i] -= 1
                neighbor_sizes[j] += 1
                
                neighbor_groups = build_groups_from_sizes(neighbor_sizes, n)
                if neighbor_groups is None: continue

                neighbor_config = find_best_config_for_grouping(neighbor_groups, all_primes)
                
                if neighbor_config.get('cost', float('inf')) < best_config.get('cost', float('inf')):
                    best_config = neighbor_config
                    current_sizes = neighbor_sizes
                    improved = True
                    logging.info(f"    k={k} [Macro Iter {iter_num+1}] 改进! 新分组大小: {best_config.get('group_sizes')}, 成本: {best_config.get('cost'):.2f}")
                    break
            if improved:
                break
                
        if not improved:
            logging.info(f"  k={k} [Macro-Search] 达到局部最优，停止宏观搜索。")
            break
            
    return best_config

def micro_tune_by_swapping_content(initial_groups, all_primes, initial_best_config):
    """
    阶段二：微观微调。在给定的分组基础上，通过移动单个素数进行精细化调整。
    """
    k = len(initial_groups)
    current_groups = [list(g) for g in initial_groups]
    best_config = initial_best_config
    
    logging.info(f"  k={k} [Micro-Tune] 开始微调. 初始成本: {best_config.get('cost', 'N/A')}")

    for iter_num in range(MAX_ITER_MICRO):
        improved = False
        # 邻域操作：移动单个素数到相邻批次
        for i in range(k - 1):
            # 正向移动: i -> i+1
            if len(current_groups[i]) > 5:
                neighbor_groups = [list(g) for g in current_groups]
                moved_prime_idx = neighbor_groups[i].pop()
                neighbor_groups[i+1].insert(0, moved_prime_idx)
                
                neighbor_config = find_best_config_for_grouping(neighbor_groups, all_primes)
                if neighbor_config.get('cost', float('inf')) < best_config.get('cost', float('inf')):
                    best_config, current_groups, improved = neighbor_config, neighbor_groups, True
                    logging.info(f"    k={k} [Micro Iter {iter_num+1}] 改进! 新分组大小: {best_config.get('group_sizes')}, 成本: {best_config.get('cost'):.2f}")
                    break

            # 反向移动: i+1 -> i
            if len(current_groups[i+1]) > 5:
                neighbor_groups = [list(g) for g in current_groups]
                moved_prime_idx = neighbor_groups[i+1].pop(0)
                neighbor_groups[i].append(moved_prime_idx)

                neighbor_config = find_best_config_for_grouping(neighbor_groups, all_primes)
                if neighbor_config.get('cost', float('inf')) < best_config.get('cost', float('inf')):
                    best_config, current_groups, improved = neighbor_config, neighbor_groups, True
                    logging.info(f"    k={k} [Micro Iter {iter_num+1}] 改进! 新分组大小: {best_config.get('group_sizes')}, 成本: {best_config.get('cost'):.2f}")
                    break
        
        if not improved:
            logging.info(f"  k={k} [Micro-Tune] 达到局部最优，停止微调。")
            break
    
    return best_config


def two_stage_optimization_for_k(k, all_primes):
    """
    顶层协调函数，按顺序执行宏观搜索和微观微调。
    """
    logging.info(f"--- 开始对 k={k} 进行两阶段优化 ---")
    n = len(all_primes)
    
    # 阶段一：宏观搜索
    initial_group_sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
    macro_best_config = macro_search_by_adjusting_sizes(initial_group_sizes, all_primes)
    
    if not macro_best_config or 'group_sizes' not in macro_best_config:
        logging.error(f"k={k} 宏观搜索失败，未找到有效配置。")
        return {'cost': float('inf')}

    # 阶段二：微观微调
    # 从宏观最优解中构建用于微调的初始分组
    initial_groups_for_micro_tuning = build_groups_from_sizes(macro_best_config['group_sizes'], n)
    final_best_config = micro_tune_by_swapping_content(initial_groups_for_micro_tuning, all_primes, macro_best_config)
    
    return final_best_config

def optimize_groups_for_k(k, all_primes):
    n = len(all_primes)
    group_sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
    indices = list(range(n))
    current_groups = []
    start_idx = 0
    for size in group_sizes:
        current_groups.append(indices[start_idx : start_idx + size]); start_idx += size
    
    best_config = find_best_config_for_grouping(current_groups, all_primes)
    logging.info(f"k={k}, 初始分组: {[len(g) for g in current_groups]}, 初始核心成本: {best_config.get('cost', 'N/A')}")
    
    max_iterations = 3 * k
    for iter_num in range(max_iterations):
        improved = False
        for i in range(k - 1):
            if len(current_groups[i]) <= 5: continue
            neighbor_groups = [list(g) for g in current_groups]
            moved_prime_idx = neighbor_groups[i].pop()
            neighbor_groups[i+1].insert(0, moved_prime_idx)
            neighbor_config = find_best_config_for_grouping(neighbor_groups, all_primes)
            if neighbor_config.get('cost', float('inf')) < best_config.get('cost', float('inf')):
                best_config = neighbor_config
                current_groups = neighbor_groups
                improved = True
                logging.info(f"  k={k} [Iter {iter_num+1}] 改进! 新分组: {best_config.get('group_sizes')}, 成本: {best_config.get('cost'):.2f}, M_total: {best_config.get('total_isogenies')}")
                break
        if not improved:
            logging.info(f"k={k}, 达到局部最优，停止迭代。")
            break
    return best_config

def generate_final_strategy(best_config):
    """为最优配置生成最终的C-style strategy数组"""
    if 'active_batches_config' not in best_config:
        print("无法生成strategy：最优配置信息不完整。")
        return []

    final_strategy_list = []
    
    # 按批次ID排序，以确保策略顺序与C代码预期一致
    active_batches = sorted(best_config['active_batches_config'], key=lambda b: b['id'])

    for batch_config in active_batches:
        batch_primes = batch_config['primes']
        mi = batch_config['mi']
        
        # 重新调用DP，这次是为了获取 strategy
        _, batch_strategy = calculate_detailed_batch_cost(tuple(batch_primes), mi)
        
        # C代码中的策略通常以问题大小(同源数量-1)开头
        # DP算法返回的是分割点列表，其长度为 mi-1
        # 我们需要在前面加上 mi 本身或 mi-1
        # 假设格式是 [大小, 分割点...]
        strategy_with_header = [mi -1] + batch_strategy if mi > 1 else []
        final_strategy_list.extend(strategy_with_header)

    return final_strategy_list

def main():
    primes_to_use = first_primes[:TOTAL_PRIMES_N]
    overall_best = {'cost': float('inf')}
    
    with Pool(PARALLELISM) as p:
        # 使用新的两阶段优化函数
        tasks = [(k, primes_to_use) for k in K_RANGE]
        results = p.starmap(two_stage_optimization_for_k, tasks)

    for config_for_k, k in zip(results, K_RANGE):
        if config_for_k:
            logging.info(f"--- k={k} 的最终结果: 核心成本={config_for_k.get('cost', 'N/A')} ---")
            if config_for_k.get('cost', float('inf')) < overall_best.get('cost', float('inf')):
                overall_best = config_for_k
                overall_best['k'] = k # 记录下是哪个 k 得到的最优解
                
    print("\n" + "="*70)
    print(f"--- 最终找到的最优 dCTIDH-H 配置 (n={TOTAL_PRIMES_N}, 可变 M_i) ---")
    print("="*70)
    if 'k' in overall_best:
        overhead_cost = calculate_total_overhead_cost(TOTAL_PRIMES_N, primes_to_use)
        core_cost = overall_best['cost']
        total_cost = core_cost + overhead_cost

        print(f"总批次数 (k):              {overall_best['k']}")
        print(f"最优分组大小:              {overall_best['group_sizes']}")
        print("-" * 70)
        print(f"高层计算边界 (M_H):        {overall_best['M_H']}")
        print(f"低层计算边界 (M_i 列表):   {overall_best.get('mi_list', 'N/A')}")
        print(f"总同源计算次数:            {overall_best['total_isogenies']}")
        print("-" * 70)
        print(f"达到的安全性 (比特):       {overall_best['security']:.2f} (目标: >{MIN_SECURITY_BITS})")
        print("-" * 70)
        print(f"核心计算成本:              {core_cost:.2f}")
        print(f"协议开销成本:              {overhead_cost:.2f}")
        print(f"估算的总成本:              {total_cost:.2f}")
        print("="*70)

        # --- 生成并打印最终的 Strategy ---
        print("\n--- 生成最终 Strategy Array ---")
        final_strategy = generate_final_strategy(overall_best)
        if final_strategy:
            c_code_output = ", ".join(map(str, final_strategy))
            print(f"\nconst int8_t strategy[{len(final_strategy)}] = {{ {c_code_output} }};")
        else:
            print("未能生成 Strategy。")

    else:
        print("未能在指定参数范围内找到满足安全条件的配置。")
    print("="*70)

if __name__ == '__main__':
    # 增加Python的递归深度限制，以适应更深的DP树
    sys.setrecursionlimit(20000) 
    main()