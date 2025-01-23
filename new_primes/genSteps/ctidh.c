#include <assert.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include "fp.h"
#include "primes.h"
#include "csidh.h"
#include "cpucycles.h"

#define N primes_num 

// void action(public_key *out, public_key const *in, private_key const *priv)

// Public (Montgomery curve affine coefficient) and private (integer vector) keys generation
void internal_keygen(fp* pk, int8_t* sk)
{
	csidh_private((private_key*) sk);			// random private integer vector
	// csidh(pk, sk);		// Public Montgomery curve affine coefficient: [sk] * E_0
    action((public_key*)*pk,&base,(private_key*)sk);    
}

// Secret sharing derivation (Montgomery curve affine coefficient)
bool internal_derive(fp* ss, fp* const pk, int8_t* const sk)
{
	if (!validate((public_key*)pk)) return 0;	// validating the input Montgomery curve affine coefficiente (it must be supersingular!)
	//printf("Public key validation (running-time): %luM + %luS + %lua\n", fpmul, fpsqr, fpadd);
	action((public_key*)ss, (public_key*)*pk, (private_key*)sk);	// Secrect sharing Montgomery curve affine coefficient: [sk] * pk
	return 1;
}

static int dumb_fp_isequal(const uint8_t* a, const uint8_t* b, size_t size) {
	return memcmp(a, b, size) == 0;
}


// ----------------------------------- helpers for the interface between static and public API

#define SECSIDH_SUCCESS 0
#define SECSIDH_FAILURE -1


/* Safely clear a buffer b of size s */
static inline
void secsidh_clear(void *b, size_t s)
{
    /*
     * TODO: tricks might be needed to ensure the compiler does not
     *       strip this call away.
     *
     * Potentially this could be an externally provided function at some
     * point.
     */
    memset(b, 0, s);
}

/*
 * Converts the internal representation of a secret key into an octet
 * buffer.
 *
 * TODO: at some point this should take care of endianess issues.
 */
static inline
void secsidh_sk2oct(uint8_t *buf, const int8_t sk[N])
{
    memcpy(buf, sk, N*sizeof(int8_t));
}

/*
 * Converts the internal representation of a public key into an octet
 * buffer.
 *
 * TODO: at some point this should take care of endianess issues.
 */
static inline
void secsidh_pk2oct(uint8_t *buf, const fp pk[1])
{
    memcpy(buf, pk, 1*sizeof(fp));
}

/*
 * Converts the internal representation of a shared secret into an octet
 * buffer.
 *
 * TODO: at some point this should take care of endianess issues.
 */
static inline
void secsidh_ss2oct(uint8_t *buf, const fp ss[1])
{
    memcpy(buf, ss, 1*sizeof(fp));
}

/*
 * Converts the octet buffer representation of a public key into our
 * internal representation.
 *
 * TODO: at some point this should take care of endianess issues.
 */
static inline
void secsidh_oct2pk(fp pk[1], const uint8_t *buf)
{
    memcpy(pk, buf, 1*sizeof(fp));
}

/*
 * Converts the octet buffer representation of a secret key into our
 * internal representation.
 *
 * TODO: at some point this should take care of endianess issues.
 */
static inline
void secsidh_oct2sk(int8_t sk[N], const uint8_t *buf)
{
    memcpy(sk, buf, N*sizeof(int8_t));
}

// ----------------------------------- Interface between static and public API

int secsidh_keygen(uint8_t *pk, uint8_t *sk)
{
    fp ipk[2];
    int8_t isk[N];

    internal_keygen(ipk, isk);

    secsidh_pk2oct(pk, (const fp*)ipk);
    secsidh_sk2oct(sk, isk);
    secsidh_clear(isk, sizeof(isk));

    return SECSIDH_SUCCESS;
}

int secsidh_derive(uint8_t *ss, const uint8_t *peer_pk, const uint8_t *sk)
{
    int ret;
    fp ipeer_pk[2], iss[1];
    int8_t isk[N];

    secsidh_oct2pk(ipeer_pk, peer_pk);
    secsidh_oct2sk(isk, sk);

    ret = internal_derive(iss, ipeer_pk, isk) == 1 ? SECSIDH_SUCCESS : SECSIDH_FAILURE;


    secsidh_clear(isk, sizeof(isk));
    secsidh_ss2oct(ss, (const fp*)iss);
    secsidh_clear(iss, sizeof(iss));

    return ret;
}

int main(void)
{
    uint8_t a[sizeof(private_key)], A[sizeof(public_key)], ss_a[sizeof(public_key)];
    secsidh_keygen(A, a); 

    uint8_t b[sizeof(private_key)], B[sizeof(public_key)], ss_b[sizeof(public_key)];
    secsidh_keygen(B, b); 

    assert(secsidh_derive(ss_a, B, a) == 0);

    assert(secsidh_derive(ss_b, A, b) == 0);

	// =============================
	// Verifying same secret sharing
	assert( dumb_fp_isequal(ss_a, ss_b, sizeof(public_key)) );

	return 0;
}
