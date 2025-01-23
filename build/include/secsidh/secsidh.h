#ifndef _SECSIDH_CONFIG_H_
#define _SECSIDH_CONFIG_H_

#include <secsidh/secsidhconfig.h>
#include <stdint.h>

#ifdef SECSIDH_ENABLE_CTIDH511

#define SECSIDH_CTIDH511_PK_SIZE 128
#define SECSIDH_CTIDH511_SK_SIZE 74
#define SECSIDH_CTIDH511_SS_SIZE 64

int secsidh_CTIDH511_keygen(uint8_t *pk, uint8_t *sk);
int secsidh_CTIDH511_derive(uint8_t *ss, const uint8_t *pk, const uint8_t *sk);

#endif

#ifdef SECSIDH_ENABLE_CTIDH512

#define SECSIDH_CTIDH512_PK_SIZE 72
#define SECSIDH_CTIDH512_SK_SIZE 88
#define SECSIDH_CTIDH512_SS_SIZE 64

int secsidh_CTIDH512_keygen(uint8_t *pk, uint8_t *sk);
int secsidh_CTIDH512_derive(uint8_t *ss, const uint8_t *pk, const uint8_t *sk);

#endif


#ifdef SECSIDH_ENABLE_CTIDH2047m1l226

#define SECSIDH_CTIDH2047m1l226_PK_SIZE 264
#define SECSIDH_CTIDH2047m1l226_SK_SIZE 170
#define SECSIDH_CTIDH2047m1l226_SS_SIZE 256

int secsidh_CTIDH2047m1l226_keygen(uint8_t *pk, uint8_t *sk);
int secsidh_CTIDH2047m1l226_derive(uint8_t *ss, const uint8_t *pk, const uint8_t *sk);

#endif

#ifdef SECSIDH_ENABLE_CTIDH2047m4l207

#define SECSIDH_CTIDH2047m4l207_PK_SIZE 264
#define SECSIDH_CTIDH2047m4l207_SK_SIZE 170
#define SECSIDH_CTIDH2047m4l207_SS_SIZE 256

int secsidh_CTIDH2047m4l207_keygen(uint8_t *pk, uint8_t *sk);
int secsidh_CTIDH2047m4l207_derive(uint8_t *ss, const uint8_t *pk, const uint8_t *sk);

#endif

#ifdef SECSIDH_ENABLE_CTIDH2047m7l188

#define SECSIDH_CTIDH2047m7l188_PK_SIZE 264
#define SECSIDH_CTIDH2047m7l188_SK_SIZE 178
#define SECSIDH_CTIDH2047m7l188_SS_SIZE 256

int secsidh_CTIDH2047m7l188_keygen(uint8_t *pk, uint8_t *sk);
int secsidh_CTIDH2047m7l188_derive(uint8_t *ss, const uint8_t *pk, const uint8_t *sk);

#endif


#endif
