
#include <math_constants.h>

#define ETA0 376.73031346177066f

#define THREADIDX ((blockDim.x * blockDim.y * threadIdx.z) + (blockDim.x * threadIdx.y) + threadIdx.x)
#define BLOCKIDX ((gridDim.x * blockIdx.y) + blockIdx.x)
#define IDX THREADIDX
// ((BLOCKIDX * blockDim.x * blockDim.y * blockDim.z) + THREADIDX)
#define IJ(i, j) ((blockDim.x * blockDim.y * threadIdx.z) + (blockDim.x * i) + j)
#define IZ(i) (blockDim.y * threadIdx.z + i)

#define F(fct, nu, u, r, rho) (fct(nu, u * r / rho) / fct(nu, u))
#define FP(fct, fctp, nu, u, r, rho) (fctp(nu, u * r / rho) / fct(nu, u))

#define J(nu, u, r, rho) F(jnf, nu, u, r, rho)
#define Y(nu, u, r, rho) F(ynf, nu, u, r, rho)
#define I(nu, u, r, rho) F(ivf, nu, u, r, rho)
#define K(nu, u, r, rho) F(knf, nu, u, r, rho)

#define JP(nu, u, r, rho) FP(jnf, jnp, nu, u, r, rho)
#define YP(nu, u, r, rho) FP(ynf, ynp, nu, u, r, rho)
#define IP(nu, u, r, rho) FP(ivf, ivp, nu, u, r, rho)
#define KP(nu, u, r, rho) FP(knf, knp, nu, u, r, rho)


__device__ void solve(float *x) {
    extern __shared__ float ab[];

    int i, j;
    int pidx, rpidx, ridx;
    float temp, temp2;

    for (i=0; i<blockDim.y; ++i) {
        /* find max pivot */
        if (threadIdx.y == i) {
            temp = 0.;
            for (j=i; j<blockDim.y; ++j) {
                if ( (temp2 = fabs(ab[IJ(j,i)])) > temp) {
                    temp = temp2;
                    pidx = j;
                }
            }
        }

        /* swap rows */
        __syncthreads();
        if (threadIdx.y == i && pidx != i) {
            ridx = IJ(pidx,threadIdx.x);
            temp = ab[IDX];
            ab[IDX] = ab[ridx];
            ab[ridx] = temp;
        }

        ridx = IJ(i,threadIdx.x);
        pidx = IJ(i,i);
        rpidx = IJ(threadIdx.y,i);

        /* row operations */
        __syncthreads();
        if (threadIdx.y != i) {
            if (threadIdx.x > i) {
                ab[IDX] -= ab[ridx] * ab[rpidx] / ab[pidx];
            }
            else if (threadIdx.x == i) {
                ab[IDX] = 0.;
            }
        }

        /* normalize row */
        __syncthreads();
        if (threadIdx.y == i) {
            if (threadIdx.x > i) {
                ab[IDX] /= ab[pidx];
            }
            else if (threadIdx.x == i) {
                ab[IDX] = 1.;
            }
        }
    }

    /* copy from ab to x */
    __syncthreads();
    for (i=0; i<8; ++i) {
        x[i] = ab[(i / 4) * (blockDim.x * blockDim.y) + blockDim.y + (i % 4)];
    }
}


__device__ float _chareq(float neff, float k0,
                         float *r, float *n, unsigned int N,
                         unsigned int nu) {
    extern __shared__ float ab[];
    unsigned int i;
    float *w, *u;
    float x[8];

    w = (float *) malloc(N*sizeof(float));
    u = (float *) malloc(N*sizeof(float));

    for (i=0; i<N; ++i) {
        w[i] = sqrtf(fabsf(n[i]*n[i] - neff*neff));
        if (0. == w[i]) {
            free(w);
            free(u);
            return CUDART_INF_F;
        }
        u[i] = k0 * r[(i+1 == N)?(i-1):i] * w[i];
        if (neff > n[i]) {
            w[i] = -w[i];
        }
    }

    /* First layer */
    if (4 == threadIdx.x) {
        switch (threadIdx.y) {
            case 0:
            case 1:
                ab[IDX] = (threadIdx.y == threadIdx.z)?1.:0.;
                break;
            case 2:
                if (threadIdx.z == 0) {
                    ab[IDX] = neff * nu / (u[0] * w[0]);
                }
                else {
                    if (neff < n[0]) {
                        ab[IDX] = -JP(nu, u[0], 1, 1) * ETA0 / w[0];
                    }
                    else {
                        ab[IDX] = -IP(nu, u[0], 1, 1) * ETA0 / w[0];
                    }
                }
                break;
            case 3:
                if (threadIdx.z == 0) {
                    if (neff < n[0]) {
                        ab[IDX] = JP(nu, u[0], 1, 1) * n[0] * n[0] / (ETA0 * w[0]);
                    }
                    else {
                        ab[IDX] = IP(nu, u[0], 1, 1) * n[0] * n[0] / (ETA0 * w[0]);
                    }
                }
                else {
                    ab[IDX] = -neff * nu / (u[0] * w[0]);
                }
                break;
        }
    }

    /* For each intermediate layer */
    for (i=1; i<N-1; ++i) {
        /* Fill matrix */
        switch (threadIdx.x) {
            case 0:
                switch (threadIdx.y) {
                    case 0:
                        ab[IDX] = (neff < n[i]) ? J(nu, u[i], r[i-1], r[i]): 
                                                  I(nu, u[i], r[i-1], r[i]);
                        break;
                    case 1:
                        ab[IDX] = (neff < n[i]) ? Y(nu, u[i], r[i-1], r[i]): 
                                                  K(nu, u[i], r[i-1], r[i]);
                        break;
                    case 2:
                    case 3:
                        ab[IDX] = 0.;
                        break;
                }
                break;
            case 1:
                switch (threadIdx.y) {
                    case 0:
                    case 1:
                        ab[IDX] = 0.;
                        break;
                    case 2:
                        ab[IDX] = (neff < n[i]) ? J(nu, u[i], r[i-1], r[i]): 
                                                  I(nu, u[i], r[i-1], r[i]);
                        break;
                    case 3:
                        ab[IDX] = (neff < n[i]) ? Y(nu, u[i], r[i-1], r[i]): 
                                                  K(nu, u[i], r[i-1], r[i]);
                        break;
                }
                break;
            case 2:
                switch (threadIdx.y) {
                    case 0:
                        ab[IDX] = ((neff < n[i]) ? J(nu, u[i], r[i-1], r[i]): 
                                                   I(nu, u[i], r[i-1], r[i])) *
                                    neff * nu * r[i] / (u[i] * r[i-1] * w[i]);
                        break;
                    case 1:
                        ab[IDX] = ((neff < n[i]) ? Y(nu, u[i], r[i-1], r[i]): 
                                                   K(nu, u[i], r[i-1], r[i])) *
                                    neff * nu * r[i] / (u[i] * r[i-1] * w[i]);
                        break;
                    case 2:
                        ab[IDX] = -((neff < n[i]) ? JP(nu, u[i], r[i-1], r[i]): 
                                                    IP(nu, u[i], r[i-1], r[i])) *
                                    ETA0 / w[i];
                        break;
                    case 3:
                        ab[IDX] = -((neff < n[i]) ? YP(nu, u[i], r[i-1], r[i]): 
                                                    KP(nu, u[i], r[i-1], r[i])) *
                                    ETA0 / w[i];
                        break;
                }
                break;
            case 3:
                switch (threadIdx.y) {
                    case 0:
                        ab[IDX] = ((neff < n[i]) ? JP(nu, u[i], r[i-1], r[i]): 
                                                   IP(nu, u[i], r[i-1], r[i])) *
                                    n[i] * n[i] / (ETA0 * w[i]);
                        break;
                    case 1:
                        ab[IDX] = ((neff < n[i]) ? YP(nu, u[i], r[i-1], r[i]): 
                                                   KP(nu, u[i], r[i-1], r[i])) *
                                    n[i] * n[i] / (ETA0 * w[i]);
                        break;
                    case 2:
                        ab[IDX] = -((neff < n[i]) ? J(nu, u[i], r[i-1], r[i]): 
                                                    I(nu, u[i], r[i-1], r[i])) *
                                    neff * nu * r[i] / (u[i] * r[i-1] * w[i]);
                        break;
                    case 3:
                        ab[IDX] = -((neff < n[i]) ? Y(nu, u[i], r[i-1], r[i]): 
                                                    K(nu, u[i], r[i-1], r[i])) *
                                    neff * nu * r[i] / (u[i] * r[i-1] * w[i]);
                        break;
                }
                break;
        }

        /* Solve system */
        __syncthreads();
        solve(x);

        /* Get E and H values */
        if (4 == threadIdx.x) {
            switch (threadIdx.y) {
                case 0:
                    ab[IDX] = x[IZ(0)] + x[IZ(1)];
                    break;
                case 1:
                    ab[IDX] = x[IZ(2)] + x[IZ(3)];
                    break;
                case 2:
                    if (neff < n[i])
                        ab[IDX] = ((neff * nu / (u[i] * w[i])) * (x[IZ(0)] + x[IZ(1)])) - 
                                  ((ETA0 / w[i]) * (x[IZ(2)] * JP(nu, u[i], 1, 1) + 
                                                    x[IZ(3)] * YP(nu, u[i], 1, 1)));
                    else
                        ab[IDX] = ((neff * nu / (u[i] * w[i])) * (x[IZ(0)] + x[IZ(1)])) - 
                                  ((ETA0 / w[i]) * (x[IZ(2)] * IP(nu, u[i], 1, 1) + 
                                                    x[IZ(3)] * KP(nu, u[i], 1, 1)));
                    break;
                case 3:
                    if (neff < n[i])
                        ab[IDX] = ((n[i] * n[i] / (ETA0 * w[i])) * 
                                        (x[IZ(0)] * JP(nu, u[i], 1, 1) + 
                                         x[IZ(1)] * YP(nu, u[i], 1, 1))) - 
                                  ((neff * nu / (u[i] * w[i])) * (x[IZ(2)] + x[IZ(3)]));
                    else
                        ab[IDX] = ((n[i] * n[i] / (ETA0 * w[i])) * 
                                        (x[IZ(0)] * IP(nu, u[i], 1, 1) + 
                                         x[IZ(1)] * KP(nu, u[i], 1, 1))) - 
                                  ((neff * nu / (u[i] * w[i])) * (x[IZ(2)] + x[IZ(3)]));
                    break;                
            }
        }

    }

    __syncthreads();

    /* Find values for last layer */
    if (neff < n[i]) {
        /* Leaky mode */
    }
    else {
        /* Guided mode */
        if (4 == threadIdx.x) {
            if (2 == threadIdx.y) {
                ab[IDX] -= (neff * nu / (u[N-1] * w[N-1])) * ab[IJ(0,4)] -
                            ((ETA0 / w[N-1]) * ab[IJ(1,4)] * KP(nu, u[N-1], 1, 1));
            }
            else if (3 == threadIdx.y) {
                ab[IDX] -= (n[N-1] * n[N-1] / (ETA0 * w[N-1])) * ab[IJ(0,4)] * KP(nu, u[N-1], 1, 1) -
                            (neff * nu / (u[N-1] * w[N-1])) * ab[IJ(1,4)];
            }
        }
    }

    free(w);
    free(u);

    __syncthreads();

    return ab[((blockDim.x * 2) + 4)] * ab[((blockDim.x * blockDim.y) + (blockDim.x * 3) + 4)] -
           ab[((blockDim.x * blockDim.y) + (blockDim.x * 2) + 4)] * ab[((blockDim.x * 3) + 4)];
}

__global__ void chareq(float *neff, float k0,
                       float *r, float *n, unsigned int N, unsigned int *nu,
                       float *x) {
    float xx;

    xx = _chareq(neff[blockIdx.x], k0, r, n, N, nu[blockIdx.y]);
    if (0 == threadIdx.x == threadIdx.y == threadIdx.z) {
        x[BLOCKIDX] = xx;
    }
}
