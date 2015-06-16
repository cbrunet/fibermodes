
__device__ float ivf( float v, float x )
{
    int sign;
    float t, ax;

    /* If v is a negative integer, invoke symmetry */
    t = floorf(v);
    if( v < 0.0 )
        {
        if( t == v )
            {
            v = -v; /* symmetry */
            t = -t;
            }
        }
    /* If x is negative, require v to be an integer */
    sign = 1;
    if( x < 0.0 )
        {
        if( t != v )
            {
            /* mtherr( "ivf", DOMAIN ); */
            return( 0.0 );
            }
        if( v != 2.0 * floorf(v/2.0) )
            sign = -1;
        }

    /* Avoid logarithm singularity */
    if( x == 0.0 )
        {
        if( v == 0.0 )
            return( 1.0 );
        if( v < 0.0 )
            {
            /* mtherr( "ivf", OVERFLOW ); */
            return( MAXNUMF );
            }
        else
            return( 0.0 );
        }

    ax = fabsf(x);
    t = v * logf( 0.5 * ax )  -  x;
    t = sign * expf(t) / tgammaf( v + 1.0 );
    ax = v + 0.5;
    return( t * hypergf( ax,  2.0 * ax,  2.0 * x ) );
}
