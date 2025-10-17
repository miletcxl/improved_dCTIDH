# #!/usr/bin/env python3

# # 导入必要的模块。请确保 costisog, optimal_strat, chain, memoized 
# # 这些自定义模块文件与本脚本在同一目录下。
# import scipy
# import scipy.special
# from math import log2
# import sys

# # 假设这些是您项目中的自定义模块
# try:
#     from memoized import memoized
#     import costisog
#     from optimal_strat import dynamic_programming_algorithm
#     import chain
# except ModuleNotFoundError as e:
#     print(f"错误：缺少必要的模块 - {e}")
#     print("请确保 'costisog.py', 'optimal_strat.py', 'chain.py', 'memoized.py' 文件与此脚本在同一目录中。")
#     sys.exit(1)


# # 使用与原脚本相同的素数列表
# first_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997, 1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091, 1093, 1097, 1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187, 1193, 1201, 1213, 1217, 1223, 1229, 1231, 1237, 1249, 1259, 1277, 1279, 1283, 1289, 1291, 1297, 1301, 1303, 1307, 1319, 1321, 1327, 1361, 1367, 1373, 1381, 1399, 1409, 1423, 1427, 1429]

# # --- 从原脚本中保留的辅助函数 ---

# def dac_search(target,r0,r1,r2,chain,chainlen,best,bestlen):
#   if chainlen >= bestlen:
#     return best,bestlen
#   if r2 > target: return best,bestlen
#   if r2<<(bestlen-1-chainlen) < target: return best,bestlen
#   if (r2 == target):
#     return chain,chainlen
#   chain *= 2
#   chainlen += 1
#   best,bestlen = dac_search(target,r0,r2,r0+r2,chain+1,chainlen,best,bestlen)
#   best,bestlen = dac_search(target,r1,r2,r1+r2,chain,chainlen,best,bestlen)
#   return best,bestlen

# def daclen(target):
#   best = None
#   bestlen = -1
#   while best == None:
#     bestlen += 1
#     best, bestlen = dac_search(target,1,2,3,0,0,best,bestlen)
#   return bestlen

# @memoized
# def daccost(target):
#   return costisog.dac(daclen(target))

# def batch_daccost(primes):
#   return max([daccost(ell) for ell in primes])

# # --- 原脚本的核心成本计算函数 ---

# def costfunction(primes0, primes1, N0, m0):
#   """
#   计算给定策略 (N0, m0) 和素数列表的成本。
#   这是原脚本的核心计算逻辑。
#   """
#   bounds = [sum(N0[:i+1]) for i in range((len(N0)))]
#   batch_stop =[b-1 for b in bounds]
#   batch_start = [0,]+bounds[:-1]

#   keyb = [sum(m0[:i+1]) for i in range(len(m0))]
#   key_start = [0,]+keyb[:-1]
#   key_stop = [b-1 for b in keyb]

#   L_max = []
#   L_min = []
#   C_mul = []
#   for b1, b2, k in zip(batch_start, batch_stop, m0):
#       dac = batch_daccost(primes0[b1:b2+1])
#       C_mul += [dac]*k
#       L_max += [primes0[i] for i in range(b2-k+1, b2+1)]
#       L_min += [primes0[i] for i in range(b1, b1+k)]

#   C_isog = []
#   C_eval = []
#   for min_val, max_val in zip(L_min, L_max):
#     ic = costisog.isog_matryoshka(min_val, max_val, 0)
#     ice = costisog.isog_matryoshka(min_val, max_val, 1) - ic
#     C_isog.append(ic)
#     C_eval.append(ice)

#   C_isog.reverse()
#   C_mul.reverse()
#   C_eval.reverse()
#   L = L_max
#   L.reverse()
  
#   # 调用动态规划算法来计算最终成本
#   cost = dynamic_programming_algorithm(L, C_mul, C_isog, C_eval)

#   return cost[1]

# # --- 新的、封装后的主函数 ---

# def calculate_cost_from_vector(strategy_vector):
#     """
#     接收一个策略向量，计算并返回其成本。
    
#     Args:
#         strategy_vector (list[int]): 一个整数列表，代表策略中的 N0。
#                                        例如: [10, 13, 15, ...]
    
#     Returns:
#         float: 计算出的总成本。
#     """
#     # 将输入向量作为 N0
#     N0 = tuple(strategy_vector)
    
#     # 基于 N0 生成一个默认的 m0 向量。
#     # 这里的策略是取 N0 中每个元素的一半（整数除法）。
#     # 这是原脚本在优化开始时使用的初始化策略。
#     m0 = (10,10,10,9,11,10,8,9,5,3)
    
#     print(f"输入向量 (N0): {N0}")
#     print(f"自动生成向量 (m0): {m0}")
    
#     # 确定需要的素数数量
#     num_primes_needed = sum(N0)
    
#     if num_primes_needed > len(first_primes):
#         raise ValueError(f"向量总和为 {num_primes_needed}，需要的素数比列表中定义（{len(first_primes)}）的要多。")
    
#     # 根据需要的数量选择素数
#     primes0 = tuple(first_primes[:num_primes_needed])
    
#     # 在这个场景下，我们假设没有需要跳过的素数
#     primes1 = tuple()
    
#     # 调用成本函数进行计算
#     total_cost = costfunction(primes0, primes1, N0, m0)
    
#     return total_cost

# # --- 主程序入口 ---
# if __name__ == '__main__':
#   # 增加Python的递归深度限制，以防 dac_search 函数出错
#   sys.setrecursionlimit(10000)

#   # 在这里输入您想计算成本的向量
#   input_vector = [20,20,20,19,23,20,18,21,23,18]

#   try:
#     # 调用计算函数
#     final_cost = calculate_cost_from_vector(input_vector)
    
#     # 打印最终结果
#     print("\n-----------------------------------------")
#     print(f"计算出的总成本为: {final_cost}")
#     print("-----------------------------------------")

#   except Exception as e:
#     print(f"\n在计算过程中发生错误: {e}")

#!/usr/bin/env python3

# ==============================================================================
# 密码学策略总成本计算器
# ------------------------------------------------------------------------------
# 作用:
#   本脚本接收一个代表分组策略的 N0 向量和一个代表密钥贡献的 m0 向量，
#   并精确计算该策略的总计算成本。
#
#   总成本 = 核心计算成本 (来自 costfunction) + 协议开销成本 (来自 cost_overhead)
#
#   所有成本模型均直接源自 greedyriver.py (代码一)，以确保结果的一致性。
# ==============================================================================

import scipy
import scipy.special
from math import log2, prod
import sys

# 假设这些是您项目中的自定义模块
try:
    from memoized import memoized
    import costisog
    from optimal_strat import dynamic_programming_algorithm
    import chain
except ModuleNotFoundError as e:
    print(f"错误：缺少必要的模块 - {e}")
    print("请确保 'costisog.py', 'optimal_strat.py', 'chain.py', 'memoized.py' 文件与此脚本在同一目录中。")
    sys.exit(1)


# --- 数据定义区 (来自代码一) ---

# 完整素数列表
first_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997, 1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091, 1093, 1097, 1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187, 1193, 1201, 1213, 1217, 1223, 1229, 1231, 1237, 1249, 1259, 1277, 1279, 1283, 1289, 1291, 1297, 1301, 1303, 1307, 1319, 1321, 1327, 1361, 1367, 1373, 1381, 1399, 1409, 1423, 1427, 1429]

# 完整的余因子字典，对于 cost_overhead 至关重要
cofactors = { 
    226 : ((1*64+4 ),[]), 225 : ((1*64+4 ),[107]), 224 : ((1*64+12),[3,3, 5, 17]), 223 : ((1*64+26),[3,3, 5]),
    222 : ((1*64+37),[47]), 221 : ((1*64+51),[3]), 220 : ((1*64+55),[3,3,3,3, 5]), 219 : ((2*64+4 ),[59]),
    218 : ((2*64+11),[7,7, 13]), 217 : ((2*64+24),[3, 5, 7]), 216 : ((2*64+33),[211]), 215 : ((2*64+46),[29]),
    214 : ((2*64+52),[23, 29]), 213 : ((3*64),[]), 212 : ((3*64+18),[]), 211 : ((3*64+24),[3, 11]),
    210 : ((3*64+29),[7, 109]), 209 : ((3*64+43),[73]), 208 : ((3*64+53),[73]), 207 : ((4*64), []),
    206 : ((4*64+11),[ 3, 13]), 205 : ((4*64+19),[ 13, 17]), 204 : ((4*64+31),[ 3, 5,5]),
    203 : ((4*64+39),[ 13, 23]), 202 : ((4*64+50),[ 7, 29]), 201 : ((5*64), []), 200 : ((5*64+9 ),[ 3, 13]),
    199 : ((5*64+16),[ 5, 53]), 198 : ((5*64+27),[ 191]), 197 : ((5*64+35),[ 719]), 196 : ((5*64+47),[ 3,3, 31]),
    195 : ((6*64), []), 194 : ((6*64+3 ),[ 7,41]), 193 : ((6*64+16),[ 67]), 192 : ((6*64+23),[ 3,3, 41]),
    191 : ((6*64+37),[ 43]), 190 : ((6*64+47),[ 5, 11]), 189 : ((6*64+55),[ 5, 31]), 188 : ((7*64+2 ),[ 7, 19]),
    187 : ((7*64+14),[ 3, 13]), 186 : ((7*64+23),[ 59]), 185 : ((7*64+31),[ 7, 43]), 184 : ((7*64+43),[ 97]),
    183 : ((7*64+55),[ 3, 5]), 182 : ((8*64), []), 181 : ((8*64+ 9 ),[ 83]), 180 : ((8*64+ 19),[ 3,3, 11]),
    179 : ((8*64+ 32),[ 3, 5]), 178 : ((8*64+ 37),[ 3, 5, 23]), 177 : ((8*64+ 48),[ 3, 5, 11]), 176 : ((9*64), []),
    175 : ((9*64+ 3 ),[ 13, 31]), 174 : ((9*64+ 15),[ 131]), 173 : ((9*64+ 26),[ 3, 5,5]),
    172 : ((9*64+ 35),[ 107]), 171 : ((9*64+ 46),[ 47]), 170 : ((9*64+ 55),[ 137]), 169 : ((10*64), []),
    168 : ((10*64+ 13),[ 23]), 167 : ((10*64+ 19),[ 17, 23]), 166 : ((10*64+ 30),[ 7, 43]),
    165 : ((10*64+ 42),[ 7, 11]), 164 : ((10*64+ 49),[ 449]), 163 : ((11*64), []), 162 : ((11*64+ 9 ),[  3, 11]),
    161 : ((11*64+ 18),[ 41]), 160 : ((11*64+ 24),[ 3, 7, 41]), 159 : ((11*64+ 40),[ 13]),
    158 : ((11*64+ 49),[ 23]), 157 : ((11*64+ 63), []), 156 : ((12*64+ 3 ),[ 53]), 155 : ((12*64+ 9 ),[ 5,5, 29]),
    154 : ((12*64+ 21),[ 227]), 153 : ((12*64+ 31),[ 137]), 152 : ((12*64+ 41),[ 13,13]), 151 : ((12*64+ 49),[ 401]),
}

# --- 基础成本函数 (来自代码一) ---
M = S = 1

def sqrt_cost(p):
  sqrtchain = chain.chain2((p+1)//4)
  sqrtchaincost = chain.cost2(sqrtchain)
  return sqrtchaincost[0]+(sqrtchaincost[1]+1)

def elligator_cost(p):
  return S+M+M+M+S+M+M+sqrt_cost(p)

def inv_cost(p):
  invchain = chain.chain2(p-2)
  invchaincost = chain.cost2(invchain)
  return invchaincost[0]+invchaincost[1]

def dac_search(target,r0,r1,r2,chain,chainlen,best,bestlen):
  if chainlen >= bestlen:
    return best,bestlen
  if r2 > target: return best,bestlen
  if r2<<(bestlen-1-chainlen) < target: return best,bestlen
  if (r2 == target):
    return chain,chainlen
  chain *= 2
  chainlen += 1
  best,bestlen = dac_search(target,r0,r2,r0+r2,chain+1,chainlen,best,bestlen)
  best,bestlen = dac_search(target,r1,r2,r1+r2,chain,chainlen,best,bestlen)
  return best,bestlen

def daclen(target):
  best = None
  bestlen = -1
  while best == None:
    bestlen += 1
    best, bestlen = dac_search(target,1,2,3,0,0,best,bestlen)
  return bestlen

@memoized
def daccost(target):
  return costisog.dac(daclen(target))

def batch_daccost(primes):
  # 确保输入是可迭代的
  if not hasattr(primes, '__iter__'):
      return daccost(primes)
  if not primes:
      return 0
  return max([daccost(ell) for ell in primes])

# --- 核心成本计算函数 (来自代码一) ---

def costfunction(primes0, primes1, N0, m0):
  bounds = [sum(N0[:i+1]) for i in range((len(N0)))]
  batch_stop =[b-1 for b in bounds]
  batch_start = [0,]+bounds[:-1]

  L_max = []
  L_min = []
  C_mul = []
  for b1, b2, k in zip(batch_start, batch_stop, m0):
      dac = batch_daccost(primes0[b1:b2+1])
      C_mul += [dac]*k
      L_max += [primes0[i] for i in range(b2-k+1, b2+1)]
      L_min += [primes0[i] for i in range(b1, b1+k)]

  C_isog = []
  C_eval = []
  for min_val, max_val in zip(L_min, L_max):
    ic = costisog.isog_matryoshka(min_val, max_val, 0)
    ice = costisog.isog_matryoshka(min_val, max_val, 1) - ic
    C_isog.append(ic)
    C_eval.append(ice)

  C_isog.reverse()
  C_mul.reverse()
  C_eval.reverse()
  L = L_max
  L.reverse()
  
  cost = dynamic_programming_algorithm(L, C_mul, C_isog, C_eval)
  return cost[1]

# --- 开销成本计算函数 (来自代码一) ---

def cost_overhead(N0, m0, primes0):
    bounds = [sum(N0[:i+1]) for i in range((len(N0)))]
    batch_stop = [b-1 for b in bounds]
    batch_start = [0,]+bounds[:-1] 
    C_mul = []
    for b1, b2, n, k in zip(batch_start,batch_stop,N0, m0):
      dac = batch_daccost(primes0[b1:b2+1])
      C_mul += 2*[dac]*(n-k)

    unused = sum(C_mul)
    
    # 查找余因子信息
    num_primes_total = sum(N0)
    if num_primes_total not in cofactors:
        raise KeyError(f"错误: cofactors 字典中没有键 {num_primes_total}。请确保字典是完整的。")
    f = cofactors[num_primes_total]

    # 计算余因子开销
    cofactor = 2*costisog.xDBL*f[0] + 2*sum([daccost(p) for p in f[1]])

    # 构建大素数 p
    p = (2**f[0] * prod(f[1]) * prod(first_primes[:num_primes_total])) - 1

    final_inv = inv_cost(p)+1
    point = elligator_cost(p)
    return cofactor + unused + final_inv + point

# --- 新的、封装后的主函数 ---

def calculate_total_cost_from_strategy(N0_vector, m0_vector):
    """
    接收一个 N0 和 m0 策略向量，计算并返回其核心、开销和总成本。
    
    Args:
        N0_vector (list[int]): 分组大小的列表。
        m0_vector (list[int]): 每个分组的密钥贡献列表。
    
    Returns:
        tuple: (核心成本, 开销成本, 总成本)。
    """
    N0 = tuple(N0_vector)
    m0 = tuple(m0_vector)
    
    print(f"输入分组策略 (N0): {N0}")
    print(f"输入密钥贡献 (m0): {m0}")

    if len(N0) != len(m0):
        raise ValueError(f"N0 向量的长度 ({len(N0)}) 与 m0 向量的长度 ({len(m0)}) 必须相等。")
    
    num_primes_needed = sum(N0)
    
    if num_primes_needed > len(first_primes):
        raise ValueError(f"N0 向量总和为 {num_primes_needed}，需要的素数比列表中定义的 ({len(first_primes)}) 要多。")
    
    primes0 = tuple(first_primes[:num_primes_needed])
    primes1 = tuple()
    
    # 1. 计算核心成本
    print(" -> 正在计算核心成本...")
    core_cost = costfunction(primes0, primes1, N0, m0)
    
    # 2. 计算开销成本
    print(" -> 正在计算开销成本...")
    overhead_cost = cost_overhead(N0, m0, primes0)
    
    # 3. 计算总成本
    total_cost = core_cost + overhead_cost
    
    return core_cost, overhead_cost, total_cost

# --- 主程序入口 ---

if __name__ == '__main__':
  # 增加Python的递归深度限制
  sys.setrecursionlimit(10000)

  # =================== 在这里输入您想计算成本的策略 ===================
  # 这是您之前优化器找到的最优解
  input_N0_vector = [20, 20, 20, 19, 23, 20, 18, 21, 23, 18]
  # 注意：m0 的长度需要与 N0 匹配。
  # 您的 M_H 是 17，所以 m0 应该有 17 个有效值，其余为0。
  input_m0_vector = [10, 10, 10, 9, 11, 10, 8, 9, 5, 3]
  # ====================================================================

  try:
    # 调用计算函数
    core, overhead, total = calculate_total_cost_from_strategy(input_N0_vector, input_m0_vector)
    
    # 打印最终结果
    print("\n" + "="*50)
    print("           *** 成本计算结果 ***")
    print("-"*50)
    print(f"核心计算成本 (Core Cost):   {core:,.2f}")
    print(f"协议开销成本 (Overhead Cost): {overhead:,.2f}")
    print("-"*50)
    print(f"估算的总成本 (Total Cost):    {total:,.2f}")
    print("="*50)

  except Exception as e:
    print(f"\n在计算过程中发生错误: {e}")