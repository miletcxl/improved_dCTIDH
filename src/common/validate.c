#include <string.h>
#include <assert.h>

#include "../CTIDH/ctidh.h"
#include "primes.h"
#include "mont.h"
#include "elligator.h"
// #include "fp2.h"

#ifdef ENABLE_CT_TESTING
#include <valgrind/memcheck.h>
#endif

// static void fp2_print(fp2 a){
//     printf("0x%016lX,", A[i]);
    
//     fp_print(a.re);
//     fp_print(a.im);
// }


// For computing [(p + 1) / l_i]P, i:=0, ..., (N - 1)
void cofactor_multiples(proj P[], proj const A, size_t lower, size_t upper)
{
    assert(lower < upper);
    if (upper - lower == 1)
        return;

    int i;
    size_t mid = lower + (upper - lower + 1) / 2;

    // proj_copy(P[mid], (const fp*)P[lower]);
    fp_copy(P[mid].x, P[lower].x);
    fp_copy(P[mid].z, P[lower].z);

    for (i = lower; i < (int)mid; i++)
        xMUL_dac(&P[mid], &A, 1, &P[mid], primes_dac[i], primes_daclen[i], primes_daclen[i]);
    // xmul(P[mid], i, (const fp*)P[mid], A);

    for (i = (int)mid; i < (int)upper; i++)
        xMUL_dac(&P[lower], &A, 1, &P[lower], primes_dac[i], primes_daclen[i], primes_daclen[i]);
    // xmul(P[lower], i, (const fp*)P[lower], A);

    cofactor_multiples(P, A, lower, mid);
    cofactor_multiples(P, A, mid, upper);
}


static void clearpublicprimes_vali(proj *P, const proj *A24)
{
  // clear powers of 2
  for (int64_t i = 0; i < two_cofactor; i++)
  {
    xDBL(P, P, A24, 0);
  }
}

static void multiples_vali(proj Q[], proj const P, proj const A)
{
  int j;

  proj_copy(&Q[0], &P);
  for (j = 0; j < (int)primes_num; j++)
  {
    if (primes[j] == 3 || primes[j] == 5 || primes[j] == 7)
      continue;

    xMUL_dac(&Q[0], &A, 1, &Q[0], primes_dac[j], primes_daclen[j], primes_daclen[j]);
  }

  //  --- multiplying by 3
  xMUL_dac(&Q[1], &A, 1, &Q[0], 0, 0, 0);
  xMUL_dac(&Q[1], &A, 1, &Q[1], 0, 0, 0);
  //  --- multiplying by 5
  xMUL_dac(&Q[0], &A, 1, &Q[0], 0, 1, 1);
  xMUL_dac(&Q[0], &A, 1, &Q[0], 0, 1, 1);
  xMUL_dac(&Q[2], &A, 1, &Q[1], 0, 1, 1);
  xMUL_dac(&Q[2], &A, 1, &Q[2], 0, 1, 1);

  //  --- multiplying by 7
  xMUL_dac(&Q[0], &A, 1, &Q[0], 2, 2, 2);
  xMUL_dac(&Q[0], &A, 1, &Q[0], 2, 2, 2);
  xMUL_dac(&Q[1], &A, 1, &Q[1], 2, 2, 2);
  xMUL_dac(&Q[1], &A, 1, &Q[1], 2, 2, 2);
}

// wombat validate by checking full order point
bool validate(public_key const *in){
    proj A, A24;
    fp_copy(A.x, in->A);
    fp_copy(A.z, fp_1);
    xA24(&A24, &A);

    proj Tp, Tm, Pp[primes_num], Aux_Tp[3], Pm[primes_num], Aux_Tm[3];

    uint8_t boolp = 0, boolm = 0;

#ifdef ENABLE_CT_TESTING
    VALGRIND_MAKE_MEM_DEFINED(Aux_Tp, sizeof(proj) * 3);
    VALGRIND_MAKE_MEM_DEFINED(Aux_Tm, sizeof(proj) * 3);
    VALGRIND_MAKE_MEM_DEFINED(&A, sizeof(proj));
    VALGRIND_MAKE_MEM_DEFINED(&boolp, sizeof(uint8_t));
    VALGRIND_MAKE_MEM_DEFINED(&boolm, sizeof(uint8_t));
    VALGRIND_MAKE_MEM_DEFINED(&Tp, sizeof(proj));
    VALGRIND_MAKE_MEM_DEFINED(Pp, sizeof(proj) * primes_num);
    VALGRIND_MAKE_MEM_DEFINED(Pm, sizeof(proj) * primes_num);
#endif
    fp seed;
    fp_set(seed, in->seed);
    fp_enc(seed, seed);
    elligator_seeded(&Tp, &Tm, &A, (const fp *)seed);

    clearpublicprimes_vali(&Tp, &A);
    clearpublicprimes_vali(&Tm, &A);

#ifdef ENABLE_CT_TESTING
    memset(Aux_Tp, 0, sizeof(proj) * 3);
#endif
    multiples_vali(Aux_Tp, Tp, A);

#ifdef ENABLE_CT_TESTING
    memset(Aux_Tm, 0, sizeof(proj) * 3);
#endif
    multiples_vali(Aux_Tm, Tm, A);

    // Checking if Tp is an order (p+1)/(2^e)
    proj_copy(&Pp[0], &Tp);
    cofactor_multiples(Pp, A, 0, primes_num);
    boolp = 1;
    boolp &= (1 - fp_iszero(Pp[0].z)) | (1 - fp_iszero(Aux_Tp[0].z));
    boolp &= (1 - fp_iszero(Pp[1].z)) | (1 - fp_iszero(Aux_Tp[1].z));
    boolp &= (1 - fp_iszero(Pp[2].z)) | (1 - fp_iszero(Aux_Tp[2].z));
    for (int j = 3; j < (int)primes_num; j++)
        boolp &= (1 - fp_iszero(Pp[j].z));


    // ---> This can be removed for wd1 style
    // Checking if Tm is an order (p+1)/(2^e)
    proj_copy(&Pm[0], &Tm);
    cofactor_multiples(Pm, A, 0, primes_num);

    boolm = 1;
    boolm &= (1 - fp_iszero(Pm[0].z)) | (1 - fp_iszero(Aux_Tm[0].z));
    boolm &= (1 - fp_iszero(Pm[1].z)) | (1 - fp_iszero(Aux_Tm[1].z));
    boolm &= (1 - fp_iszero(Pm[2].z)) | (1 - fp_iszero(Aux_Tm[2].z));
    for (int j = 3; j < (int)primes_num; j++)
        boolm &= (1 - fp_iszero(Pm[j].z));


    
    return boolp & boolm;
}
