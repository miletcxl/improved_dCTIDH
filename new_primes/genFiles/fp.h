#ifndef FP_H
#define FP_H

#include "uintbig.h"
#include "fp_namespace.h"

/* fp is in the Montgomery domain, so interpreting that
   as an integer should never make sense.
   enable compiler warnings when mixing up uintbig and fp. */
// typedef struct fp {
//     uintbig x;
// } fp;

typedef uint64_t fp[UINTBIG_LIMBS];

extern const fp fp_0;
extern const fp fp_1;
extern const fp fp_2;
extern const fp fp_p;

void fp_cswap(fp x, fp y, long long c); /* c is 0 or 1 */
void fp_cmov(fp *x, const fp *y, long long c); /* c is 0 or 1 */

void fp_add2(fp *x, fp const *y);
void fp_sub2(fp *x, fp const *y);
void fp_mul2(fp *x, fp const *y);

void fp_add3(fp *x, fp const *y, fp const *z);
void fp_sub3(fp *x, fp const *y, fp const *z);
void fp_mul3(fp *x, fp const *y, fp const *z);

void fp_sq1(fp *x);
void fp_sq2(fp *x, fp const *y);

extern long long fp_mulsq_count;
extern long long fp_sq_count;
extern long long fp_addsub_count;

static inline void fp_sq1_rep(fp *x,long long n)
{
  while (n > 0) {
    --n;
    fp_sq1(x);
  }
}

static inline void fp_neg1(fp *x)
{
  fp_sub3(x,&fp_0,x);
}

static inline void fp_neg2(fp *x,const fp *y)
{
  fp_sub3(x,&fp_0,y);
}

static inline void fp_double1(fp *x)
{
  fp_add2(x,x);
}

static inline void fp_double2(fp *x,const fp *y)
{
  fp_add3(x,y,y);
}

static inline void fp_quadruple2(fp *x,const fp *y)
{
  fp_double2(x,y);
  fp_double1(x);
}

void  fp_copy(fp b, const fp a);

static inline void fp_quadruple1(fp *x)
{
  fp_double1(x);
  fp_double1(x);
}

static inline long long fp_iszero(const fp *x)
{
  return uintbig_iszero((uintbig*)x);
}

// static inline long long fp_iszero(fp x)
// {
// //   return uintbig_iszero(&x->x);

// 	int i;
// 	uint64_t c = 0;
// 	for (i=UINTBIG_LIMBS-1; i >= 0; i--) 
// 		c |= x[i];
// 	return (c == 0);

// }

static inline long long fp_isequal(const fp *x,const fp *y)
{
  return uintbig_isequal( (uintbig*)x, (uintbig*)y);

	// int i;
	// uint64_t r = 0, t;

	// for (i = 0; i < UINTBIG_LIMBS; i++)
	// {
	// 	t = 0;
	// 	unsigned char *ta = (unsigned char *)x[i];
	// 	unsigned char *tb = (unsigned char *)y[i];
	// 	t = (ta[0] ^ tb[0]) | (ta[1] ^ tb[1]) | (ta[2] ^ tb[2]) |  (ta[3] ^ tb[3]) | (ta[4] ^ tb[4]) | (ta[5] ^ tb[5]) | (ta[6] ^ tb[6]) |  (ta[7] ^ tb[7]);

	// 	t = (-t);
	// 	t = t >> 63;
	// 	r |= t;
	// };

	// return (uint64_t)(1 - r);

}


// static inline long long fp_isequal(const fp *x,const fp *y)
// {
// //   return uintbig_isequal(&x->x,&y->x);
//     return fp_isequal(x, y);
// }

void fp_inv(fp *x);


// static inline uint64_t fp_issmaller(fp const a, fp const b)
// {
// 	int i;
// 	int64_t r = 0, ab, c;

// 	for (i = 0; i < UINTBIG_LIMBS; i++)
// 	{

// 		ab = a[i] ^ b[i];
// 		c = a[i] - b[i];
// 		c ^= ab & (c ^ a[i]);
// 		c = (c >> 63);
// 		r |= c;
// 	};

// 	return 1 - (uint64_t)(r + 1);
// }

// if x is a square: replace x by principal sqrt and return 1
// else: return 0
long long fp_sqrt(fp *x);

#include "randombytes.h"
// #include "crypto_declassify.h"

static inline void fp_random(fp *x)
{
  for (;;) {
    randombytes(x,sizeof(fp));

    uintbig diff;
    long long accept = uintbig_sub(&diff, (uintbig*)x,&uintbig_p);
        // long long accept = fp_issmaller(*x,p);  

    // crypto_declassify(&accept,sizeof accept);
    if (accept) return;
  }
}

#endif
