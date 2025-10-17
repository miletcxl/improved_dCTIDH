#!/usr/bin/env python3

# sample usage: ./greedyriver.py 512 220 3 0 2
# CSIDH-512 prime
# >=2^220 keys
# B=3
# force the 0 largest primes to be skipped
# try to use 2 cores

from multiprocessing import Pool

import scipy
import scipy.special
from math import log2 , prod

from memoized import memoized
import costisog
from optimal_strat import dynamic_programming_algorithm
import sys

from random import randrange

import chain

first_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997, 1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091, 1093, 1097, 1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187, 1193, 1201, 1213, 1217, 1223, 1229, 1231, 1237, 1249, 1259, 1277, 1279, 1283, 1289, 1291, 1297, 1301, 1303, 1307, 1319, 1321, 1327, 1367, 1373, 1381, 1399, 1409, 1423, 1427, 1429, 1433, 1439]


ells_new_m1 = (3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997, 1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091, 1093, 1097, 1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187, 1193, 1201, 1213, 1217, 1223, 1229, 1231, 1237,1249, 1259, 1277, 1279, 1283,
            1289, 1291, 1297, 1301, 1303, 1307, 1319, 1321, 1327, 1367, 1373, 1381,
            1399, 1409, 1423, 1427, 1429, 1433, 1439,)

cofactors = { 
    226 : ((1*64+4 ),[]),
    225 : ((1*64+4 ),[107]), 
    224 : ((1*64+12),[3,3, 5, 17]),
    223 : ((1*64+26),[3,3, 5]), 
    222 : ((1*64+37),[47]), 
    221 : ((1*64+51),[3]), 
    220 : ((1*64+55),[3,3,3,3, 5]), 
    219 : ((2*64+4 ),[59]), 
    218 : ((2*64+11),[7,7, 13]), 
    217 : ((2*64+24),[3, 5, 7]),
    216 : ((2*64+33),[211]), 
    215 : ((2*64+46),[29]), 
    214 : ((2*64+52),[23, 29]),
    213 : ((3*64),[]),
    212 : ((3*64+18),[]), 
    211 : ((3*64+24),[3, 11]),
    210 : ((3*64+29),[7, 109]),
    209 : ((3*64+43),[73]), 
    208 : ((3*64+53),[73]), 
    207 : ((4*64), []),
    206 : ((4*64+11),[ 3, 13]), 
    205 : ((4*64+19),[ 13, 17]), 
    204 : ((4*64+31),[ 3, 5,5]), 
    203 : ((4*64+39),[ 13, 23]), 
    202 : ((4*64+50),[ 7, 29]), 
    201 : ((5*64), []),
    200 : ((5*64+9 ),[ 3, 13]), 
    199 : ((5*64+16),[ 5, 53]),
    198 : ((5*64+27),[ 191]), 
    197 : ((5*64+35),[ 719]), 
    196 : ((5*64+47),[ 3,3, 31]), 
    195 : ((6*64), []),
    194 : ((6*64+3 ),[ 7,41]), 
    193 : ((6*64+16),[ 67]),
    192 : ((6*64+23),[ 3,3, 41]),
    191 : ((6*64+37),[ 43]),
    190 : ((6*64+47),[ 5, 11]),
    189 : ((6*64+55),[ 5, 31]),
    188 : ((7*64+2 ),[ 7, 19]),
    187 : ((7*64+14),[ 3, 13]),
    186 : ((7*64+23),[ 59]),
    185 : ((7*64+31),[ 7, 43]),
    184 : ((7*64+43),[ 97]),
    183 : ((7*64+55),[ 3, 5]),
    182 : ((8*64), []),
    181 : ((8*64+ 9 ),[ 83]),
    180 : ((8*64+ 19),[ 3,3, 11]),
    179 : ((8*64+ 32),[ 3, 5]),
    178 : ((8*64+ 37),[ 3, 5, 23]),
    177 : ((8*64+ 48),[ 3, 5, 11]),
    176 : ((9*64), []),
    175 : ((9*64+ 3 ),[ 13, 31]),
    174 : ((9*64+ 15),[ 131]),
    173 : ((9*64+ 26),[ 3, 5,5]),
    172 : ((9*64+ 35),[ 107]),
    171 : ((9*64+ 46),[ 47]),
    170 : ((9*64+ 55),[ 137]),
    169 : ((10*64), []),
    168 : ((10*64+ 13),[ 23]),
    167 : ((10*64+ 19),[ 17, 23]),
    166 : ((10*64+ 30),[ 7, 43]),
    165 : ((10*64+ 42),[ 7, 11]),
    164 : ((10*64+ 49),[ 449]),
    163 : ((11*64), []),
    162 : ((11*64+ 9 ),[  3, 11]),
    161 : ((11*64+ 18),[ 41]),
    160 : ((11*64+ 24),[ 3, 7, 41]),
    159 : ((11*64+ 40),[ 13]),
    158 : ((11*64+ 49),[ 23]),
    157 : ((11*64+ 63), []),
    156 : ((12*64+ 3 ),[ 53]),
    155 : ((12*64+ 9 ),[ 5,5, 29]),
    154 : ((12*64+ 21),[ 227]),
    153 : ((12*64+ 31),[ 137]),
    152 : ((12*64+ 41),[ 13,13]),
    151 : ((12*64+ 49),[ 401]),}


M = S = 1

def sqrt(p):
  sqrtchain = chain.chain2((p+1)//4)
  sqrtchaincost = chain.cost2(sqrtchain)
  return sqrtchaincost[0]+(sqrtchaincost[1]+1)

def elligator(p):
  return S+M+M+M+S+M+M+sqrt(p)


def inv(p):
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

def batch_daclen(primes):
  return max([daclen(ell) for ell in primes])

def batch_daccost(primes):
  return max([daccost(ell) for ell in primes])


def printstatus(prefix,cost,N0,m0,numprimes1):
  N = N0 if numprimes1 == 0 else N0+(numprimes1,)
  m = m0 if numprimes1 == 0 else m0+(0,)
  print('%s %a %s %s' % (prefix,cost,str(N).replace(' ',''),str(m).replace(' ','')))

@memoized
def batchstart(batchsize):
  B = len(batchsize)
  return [sum(batchsize[:j]) for j in range(B)]


@memoized
def batchstop(batchsize):
  B = len(batchsize)
  return [sum(batchsize[:j+1]) for j in range(B)]


def costfunction(primes0,primes1,N0,m0,dyn = True):

  bounds = [sum(N0[:i+1]) for i in range((len(N0)))]
  batch_stop =[b-1 for b in bounds]
  batch_start = [0,]+bounds[:-1]

  keyb = [sum(m0[:i+1]) for i in range(len(m0))]

  key_start = [0,]+keyb[:-1]

  key_stop = [b-1 for b in keyb]

  L_max = []
  L_min = []
  C_mul = []
  for b1, b2, k in zip(batch_start,batch_stop, m0):
      dac = batch_daccost(primes0[b1:b2+1])
      C_mul += [dac]*k
      L_max += [primes0[i] for i in range(b2-k+1, b2+1)]
      L_min += [primes0[i] for i in range(b1, b1+k)]

  C_isog = []
  C_eval = []
  for min, max in zip(L_min, L_max):
    ic = costisog.isog_matryoshka(min,max, 0)
    ice = costisog.isog_matryoshka(min,max, 1) - ic

    C_isog += [ic]
    C_eval += [ice]

  C_isog.reverse()
  C_mul.reverse()
  C_eval.reverse()
  L = L_max
  L.reverse()
  cost = dynamic_programming_algorithm(L, C_mul, C_isog, C_eval)

  return cost[1]

def costfunction_wombateval(primes0,primes1,N0,m0):
  primes = primes0+primes1
  cost = 0
  bstart = batchstart(N0)
  bstop =  batchstop(N0)

  # add cost to remove unused ells
  # for ell in primes1:
  #   cost += 2*daccost(ell)

  # remove all degrees not in ell
  # for (b1, b2, m) in zip(bstart, bstop, m0): 
  #   mdac = batch_daccost(primes[b1:b2])
  #   cost += 2*mdac*(b2-b1-m)


  # main action loop
  for i, (b1, b2, m) in enumerate(zip(bstart, bstop, m0)):  
    # remove all degrees up to batch
    for innerI, (b11, b22, mi) in enumerate(zip(bstart, bstop, m0)):
      if i == innerI:
        break
      mdac = batch_daccost(primes[b11:b22])
      cost += 2*mdac*mi


    mdac = batch_daccost(primes[b1:b2])
    # remove ells for obtain kernel point
    # sum(m-1,m-2,m-3,...,0)
    cost += (((m-1)*(m-2))/2)*mdac

    max_ell = primes[b2-1]
    min_ell = primes[b1]
    cost += costisog.isog_matryoshka(min_ell,max_ell, 4)*(m-2)
    cost += costisog.isog_matryoshka(min_ell,min_ell, 2)
    cost += costisog.isog_matryoshka(min_ell,max_ell, 0)
    
    cost += 4*mdac*(m-1)
    cost += 2*mdac
  
  return cost


@memoized
def batchkeys_wombat(x,y):
  ## (-1, 1)
  # return scipy.special.comb(x, i,exact=True)*(2**i)
  ## (-1, 0, +1)
  return sum([scipy.special.comb(x, i,exact=True)*(2**i) for i in range(0,y+1)])

def batchkeys_CTIDH(x,y):
  poly = [1]
  for i in range(x):
    newpoly = poly+[0]
    for j in range(len(poly)):
      newpoly[j+1] += poly[j]
    poly = newpoly
  for i in range(y):
    newpoly = poly+[0]
    for j in range(len(poly)):
      newpoly[j+1] += 2*poly[j]
    poly = newpoly
  return poly[x]

@memoized
def keys(N,m):
  result = 1
  for s,b in zip(N,m):
    result *= batchkeys_wombat(s,b)
  return result

# neighboring_intvec; search upwards in non-b directions
def searchdown(minkeyspace,primes0,primes1,N0,m0,cost,b,best):
  if cost >= best[0]:
     return best
  if keys(N0,m0) >= minkeyspace:
    return cost,m0

  return best


def optimizem(minkeyspace,primes0,primes1,N0,m0=None):
  B0 = len(N0)

  # Idea: randomize this and do multiple runs?
  m0 = [b//2 for b in N0]

  # for i, (m, N) in enumerate(zip(m0, N0)):
  #   best = batchkeys_wombat(N, m)
  #   for mnew in range(m, N):
  #     k =  batchkeys_wombat(N, mnew)
  #     if k > best:
  #       best = k
  #       m0[i] = mnew

  cost = costfunction(primes0,primes1,N0,m0, dyn=True)

  # random runs
  m0_best = []
  cost_best = 1_000_000
  for _ in range(15):
    m0 = [b//2 for b in N0]

    for j in range(5, B0):
        if m0[j] > 4:
            m0[j] -= randrange(5)
    while True:
      best = cost,m0
      for b in range(B0):
        if m0[b] == 0: continue
        newm = list(m0)
        newm[b] -= 1
        newm = tuple(newm)
        newcost = costfunction(primes0,primes1,N0,newm, dyn=True)
        best = searchdown(minkeyspace,primes0,primes1,N0,newm,newcost,b,best)
      if best == (cost,m0): break

      cost, m0 = best
      if cost < cost_best:
        cost_best = cost
        m0_best = m0
        printstatus('improved', cost, N0, tuple(m0), len(primes1))


  return cost_best,m0_best


def optimizeNm(minkeyspace,primes0,primes1,B,parallelism=1):
  B0 = B #B-1 if len(primes1)>0 else B
  N0 = tuple(len(primes0)//B0+(j<len(primes0)%B0) for j in range(B0))
  cost,m0 = optimizem(minkeyspace,primes0,primes1,N0)

  while True:
    best = cost,N0,m0
    variants = []
    for b in range(B0):
      if N0[b] <= 1: continue
      for c in range(B0):
        if c == b: continue
        newsize = list(N0)
        newsize[b] -= 1
        newsize[c] += 1
        newsize = tuple(newsize)
        variants += [(minkeyspace,primes0,primes1,newsize,m0)]
    with Pool(parallelism) as p:
      results = p.starmap(optimizem,variants,chunksize=1)
    for (newcost,newm),(_,_,_,newsize,_) in zip(results,variants):
      if newcost < best[0]:
        best = newcost,newsize,newm
    if best == (cost,N0,m0): break
    cost,N0,m0 = best

  return cost,N0,m0

def cost_overhead(N0, m0, primes0):
    bounds = [sum(N0[:i+1]) for i in range((len(N0)))]
    batch_stop = [b-1 for b in bounds]
    batch_start = [0,]+bounds[:-1] 
    C_mul = []
    for b1, b2, n, k in zip(batch_start,batch_stop,N0, m0):
      dac = batch_daccost(primes0[b1:b2+1])
      C_mul += 2*[dac]*(n-k)

    unused = sum(C_mul)
    f = cofactors[sum(N0)]
    cofactor = 2*costisog.xDBL*f[0] + 2*sum([daccost(p) for p in f[1]])

    p = (2**f[0] * prod(f[1]) * prod(first_primes[:sum(N0)+1]))-1

    final_inv = inv(p)+1
    point = elligator(p)
    return cofactor+unused+final_inv+point


def doit():
  """
  New search strategy based on hierarchical WOMBATs.
  We fix the high-level grouping (N, M) and adjust the security target
  for the low-level WOMBAT search.
  """
  sys.setrecursionlimit(10000)

  # High-level parameters for the hierarchical strategy
  N_HI = 19  # Total number of high-level groups
  M_HI = 17  # Number of active high-level groups
  TOTAL_SECURITY_TARGET = 221

  # Calculate security contribution from high-level combinations
  # This is log2(C(N, M))
  high_level_combinations = scipy.special.comb(N_HI, M_HI, exact=True)
  security_from_high_level = log2(high_level_combinations)

  print(f"Hierarchical Strategy (N={N_HI}, M={M_HI})")
  print(f"Security contribution from high-level: {security_from_high_level:.4f} bits")
  
  # Calculate the remaining security target for the low-level WOMBATs
  low_level_security_target = TOTAL_SECURITY_TARGET - security_from_high_level
  minkeyspace = 2**low_level_security_target

  print(f"Required security from low-level WOMBATs: {low_level_security_target:.4f} bits")
  print(f"Equivalent low-level keyspace target: 2^{low_level_security_target:.4f}\n")


  best_overall = (1000000, (), (), 0)

  # The number of groups for the low-level search is fixed to N_HI
  B = N_HI

  # Search over the total number of primes (n_ells)
  for n_ells in reversed(range(150, 226)):
    print(f"--------------------------------------------------")
    print(f"Start search for #ell = {n_ells} with {B} batches")
    
    primes0 = first_primes[:n_ells]
    primes1 = [] # Assuming no skipped primes for this strategy

    # We use a fixed number of batches B, so we only need to call optimizeNm once per n_ells
    parallelism = 8 # Or however many cores you want to use
    cost, N0, m0 = optimizeNm(minkeyspace, primes0, primes1, B, parallelism)

    print()
    print(f"Result for #ell = {n_ells}:")
    printstatus(f'[{n_ells}] output', cost, N0, tuple(m0), len(primes1))
    
    if cost < best_overall[0]:
      best_overall = (cost, N0, m0, n_ells)
      print(f"!!! Found new best overall cost: {cost} !!!")

    print(f"--------------------------------------------------\n")

  print("\n==================================================")
  print("Search finished. Best result found:")
  (cost, N0, m0, n_ells) = best_overall
  m0 = tuple(m0)
  
  # The total security is the sum of the low-level keyspace and the high-level combinations
  final_low_level_keys = keys(N0, m0)
  total_security = log2(final_low_level_keys) + security_from_high_level

  print(f"Best configuration is for #ell = {n_ells}")
  printstatus(f'[BEST] output', cost, N0, m0, 0) # numprimes1 is 0
  print(f"\tFinal low-level security: {log2(final_low_level_keys):.4f} bits")
  print(f"\tTotal combined security: {total_security:.4f} bits")
  overhead = cost_overhead(N0, m0, first_primes[:n_ells])
  print(f"\t+overhead: {overhead}")
  print(f"\tTotal cost (with overhead): {cost + overhead}")
  print("==================================================")



@memoized
def batchstart(batchsize):
  B = len(batchsize)
  return [sum(batchsize[:j]) for j in range(B)]


@memoized
def batchstop(batchsize):
  B = len(batchsize)
  return [sum(batchsize[:j+1]) for j in range(B)]

def wombat_config(N0,m0, primes):
  config = {}
  bounds = [sum(N0[:i+1]) for i in range((len(N0)))]
  config["WOMBATKEYS"] = sum(m0)
  config["batches"] = len(N0)
  config["batch_start"] = [0,]+bounds[:-1]
  config["batch_stop"] = [b-1 for b in bounds]
  keyb = [sum(m0[:i+1]) for i in range(len(m0))]

  config["batch_keybounds_start"] = [0,]+keyb[:-1]

  config["batch_keybounds_stop"] = [b-1 for b in keyb]
  bstart = batchstart(N0)
  bstop = batchstop(N0)

  config["batch_numkeys"] = m0
  config["batch_maxdac"] = [batch_daclen(primes[b1:b2]) for b1,b2 in zip(bstart ,bstop)]
  config["keys"] = log2(keys(N0, m0))
  return config




if __name__ == '__main__':
  # --- 使用您提供的特定分组 ---
  N0 = (10, 13, 15, 11, 13, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 11, 9, 11)
  m0 = (9, 9, 9, 6, 6, 5, 4, 4, 4, 3, 3, 2, 2, 2, 2, 2, 1, 0, 0)
  
  # --- 准备 costfunction 所需的参数 ---
  # 1. 计算所需的素数总数
  n_ells = sum(N0)
  
  # 2. 从预定义列表中获取素数
  primes0 = first_primes[:n_ells]
  primes1 = [] # 假设没有跳过的素数

  print(f"正在为给定的 N0 和 m0 分组计算成本和策略...")
  print(f"高层分组 (N0): {N0}")
  print(f"底层分组 (m0): {m0}")
  print(f"使用的素数数量: {n_ells}")
  print("-" * 40)

  # --- 模拟 costfunction 内部的逻辑来调用动态规划算法 ---
  
  bounds = [sum(N0[:i+1]) for i in range((len(N0)))]
  batch_stop =[b-1 for b in bounds]
  batch_start = [0,]+bounds[:-1]

  # 准备成本列表
  L_max = []
  L_min = []
  C_mul = []
  # 遍历每个分组，只处理 m0 > 0 的情况
  for b1, b2, k in zip(batch_start, batch_stop, m0):
      if k > 0:
          dac = batch_daccost(primes0[b1:b2+1])
          C_mul.extend([dac] * k)
          L_max.extend([primes0[i] for i in range(b2-k+1, b2+1)])
          L_min.extend([primes0[i] for i in range(b1, b1+k)])

  C_isog = []
  C_eval = []
  for min_p, max_p in zip(L_min, L_max):
    ic = costisog.isog_matryoshka(min_p, max_p, 0)
    ice = costisog.isog_matryoshka(min_p, max_p, 1) - ic
    C_isog.append(ic)
    C_eval.append(ice)

  # 算法需要反转的列表
  C_isog.reverse()
  C_mul.reverse()
  C_eval.reverse()
  L = L_max
  L.reverse()
  
  # --- 调用动态规划算法 ---
  # 这个函数将会直接打印出最终的策略和成本
  strategy, final_cost = dynamic_programming_algorithm(L, C_mul, C_isog, C_eval)