import random
import sys

len_og = len([3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
            67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 
            139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 
            223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283,
            293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 
            383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 
            463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 
            569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 
            647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 
            743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 
            839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 
            941, 947, 953, 967, 971, 977, 983, 991, 997, 1009, 1013, 1019, 1021, 
            1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091, 1093, 1097,
            1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187, 1193, 
            1201, 1213, 1217, 1223, 1229, 1231, 1237, 1249, 1259, 1277, 1279, 1283, 
            1289, 1291, 1297, 1301, 1303, 1307, 1319, 1321, 1327, 1367, 1373, 1381, 
            1399, 1409, 1423, 1427, 1429, 1433, 1439,])

ells2048 = primes_first_n(len_og+1)[1:]


elli_canidates = list(set(primes_first_n(300)[1:]) - set(ells2048))
allprimes = list((set(primes_first_n(2000)[1:]) - set(ells2048)))
allprimes.sort()

def find_new_primes(cofactor, target_bits, base_ells, test_ells, k):
    primes = []
    for changed in range(2):
        tries = 0
        while tries < 25000:
            tries += 1
            tester = random.sample(test_ells, k)
            tester += random.sample(elli_canidates, changed)

            # selected same for ell_i and cofactor
            if len(tester) != changed+k:
                continue

            tester.sort()
            start_ells = base_ells     
            if changed > 0:
                start_ells = start_ells[:-changed]

            base = cofactor*prod(start_ells + tester)

            prime = base - 1
        
            pbits = len(prime.bits())


            if pbits != target_bits:
                continue
            
            if not is_prime(prime):
                continue
        

            print(f"\tprime found for {len(base_ells)} ells, cofactors {k}, swapped {changed}")
            #tester += [prime+1 // base]

            #result = base_ells + tester
            new_ells = start_ells + tester
            r = [new_ells[:len(base_ells)], new_ells[len(base_ells):]]
            primes += (r, k, changed)
            print(f"\t{r}")
            print()
            sys.stdout.flush()
            break

        
        if changed == 0 and len(primes) != 0:
            break
        

    return primes


def find_primes_2(cofactor, target_bits, base_ells):
    n = 2^(cofactor*64)*prod(base_ells)
    for addtwo in reversed(range(64)):
        base = n*2^addtwo

        pbits = len(base.bits())
        needed = target_bits-pbits-1
        
        if needed <= 0:
            continue
        
        start = 2^needed
        for f in range(start,10000):    
            prime = (base * f) - 1
        
            pbits = len(prime.bits())

            if pbits != target_bits:
                continue

            if is_prime(prime):
                print(f"2^({cofactor}*64)* 2^{addtwo}*{factor(f)} *{base_ells}")
                return
            




for n_ells in reversed(range(150, 232)):
    ells =primes_first_n(n_ells+1)[1:]
    max_exp = 1
    p = 1
    for i in range(2, 15):
        p_ = prod(ells)* 2^(i*64)
        if p_ > 2^2047:
            break
        max_exp = i
        p = p_
    print(f"{len(ells)} : 2^({max_exp}*64)*prod(ell) @ {len(p.bits())} bits")
    sys.stdout.flush()

    results = find_primes_2(max_exp, 2047, ells)
       
