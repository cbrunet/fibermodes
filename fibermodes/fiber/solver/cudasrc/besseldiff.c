
__device__ float jnp(int n, float z) {
    if (0 == n)
        return -jnf(1, z);
    else
        return (jnf(n-1, z) - jnf(n+1, z)) / 2.;
}

__device__ float ynp(int n, float z) {
    if (0 == n)
        return -ynf(1, z);
    else
        return (ynf(n-1, z) - ynf(n+1, z)) / 2.;
}

__device__ float ivp(int n, float z) {
    if (0 == n)
        return ivf(1, z);
    else
        return (ivf(n-1, z) + ivf(n+1, z)) / 2.;
}

__device__ float knp(int n, float z) {
    if (0 == n)
        return -knf(1, z);
    else
        return -(knf(n-1, z) + knf(n+1, z)) / 2.;
}
