#ifndef FP_CTIDH_H
#define FP_CTIDH_H

#include "fp.h"
// #include "fp_namespace.h"

static void fp_cswap_ctidh(fp *x, fp *y, long long c) {
   fp_cswap(*x, *y, c);
}


#endif
