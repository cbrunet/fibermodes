
/*                          hyp2f0()    */

__device__ float hyp2f0f(float a, float b, float x, int type, float *err)
{
    float a0, alast, t, tlast, maxt;
    float n, an, bn, u, sum, temp;

    an = a;
    bn = b;
    a0 = 1.0;
    alast = 1.0;
    sum = 0.0;
    n = 1.0;
    t = 1.0;
    tlast = 1.0e9;
    maxt = 0.0;

    do
        {
        if( an == 0 )
            goto pdone;
        if( bn == 0 )
            goto pdone;

        u = an * (bn * x / n);

        /* check for blowup */
        temp = fabsf(u);
        if( (temp > 1.0 ) && (maxt > (MAXNUMF/temp)) )
            goto error;

        a0 *= u;
        t = fabsf(a0);

        /* terminating condition for asymptotic series */
        if( t > tlast )
            goto ndone;

        tlast = t;
        sum += alast;   /* the sum is one term behind */
        alast = a0;

        if( n > 200 )
            goto ndone;

        an += 1.0;
        bn += 1.0;
        n += 1.0;
        if( t > maxt )
            maxt = t;
        }
    while( t > MACHEPF );


    pdone:  /* series converged! */

    /* estimate error due to roundoff and cancellation */
    *err = fabsf(  MACHEPF * (n + maxt)  );

    alast = a0;
    goto done;

    ndone:  /* series did not converge */

    /* The following "Converging factors" are supposed to improve accuracy,
     * but do not actually seem to accomplish very much. */

    n -= 1.0;
    x = 1.0/x;

    switch( type )  /* "type" given as subroutine argument */
    {
    case 1:
        alast *= ( 0.5 + (0.125 + 0.25*b - 0.5*a + 0.25*x - 0.25*n)/x );
        break;

    case 2:
        alast *= 2.0/3.0 - b + 2.0*a + x - n;
        break;

    default:
        ;
    }

    /* estimate error due to roundoff, cancellation, and nonconvergence */
    *err = MACHEPF * (n + maxt)  +  fabsf( a0 );


    done:
    sum += alast;
    return( sum );

    /* series blew up: */
    error:
    *err = MAXNUMF;
    /* mtherr( "hypergf", TLOSS ); */
    return( sum );
}

__device__ float hy1f1af( float a, float b, float x, float *err )
{
    float h1, h2, t, u, temp, acanc, asum, err1, err2;

    if( x == 0 )
        {
        acanc = 1.0;
        asum = MAXNUMF;
        goto adone;
        }
    temp = logf( fabsf(x) );
    t = x + temp * (a-b);
    u = -temp * a;

    if( b > 0 )
        {
        temp = lgammaf(b);
        t += temp;
        u += temp;
        }

    h1 = hyp2f0f( a, a-b+1, -1.0/x, 1, &err1 );

    temp = expf(u) / tgammaf(b-a);
    h1 *= temp;
    err1 *= temp;

    h2 = hyp2f0f( b-a, 1.0-a, 1.0/x, 2, &err2 );

    if( a < 0 )
        temp = expf(t) / tgammaf(a);
    else
        temp = expf( t - lgammaf(a) );

    h2 *= temp;
    err2 *= temp;

    if( x < 0.0 )
        asum = h1;
    else
        asum = h2;

    acanc = fabsf(err1) + fabsf(err2);


    if( b < 0 )
        {
        temp = tgammaf(b);
        asum *= temp;
        acanc *= fabsf(temp);
        }


    if( asum != 0.0 )
        acanc /= fabsf(asum);

    acanc *= 30.0;  /* fudge factor, since error of asymptotic formula
             * often seems this much larger than advertised */

    adone:


    *err = acanc;
    return( asum );
}

/* Power series summation for confluent hypergeometric function     */
__device__ float hy1f1pf( float a, float b, float x, float *err )
{
    float n, a0, sum, t, u, temp;
    float an, bn, maxt, pcanc;

    /* set up for power series summation */
    an = a;
    bn = b;
    a0 = 1.0;
    sum = 1.0;
    n = 1.0;
    t = 1.0;
    maxt = 0.0;

    while( t > MACHEPF )
        {
        if( bn == 0 )           /* check bn first since if both */
            {
            /* mtherr( "hypergf", SING ); */
            return( MAXNUMF );  /* an and bn are zero it is */
            }
        if( an == 0 )           /* a singularity        */
            return( sum );
        if( n > 200 )
            goto pdone;
        u = x * ( an / (bn * n) );

        /* check for blowup */
        temp = fabsf(u);
        if( (temp > 1.0 ) && (maxt > (MAXNUMF/temp)) )
            {
            pcanc = 1.0;    /* estimate 100% error */
            goto blowup;
            }

        a0 *= u;
        sum += a0;
        t = fabsf(a0);
        if( t > maxt )
            maxt = t;
    /*
        if( (maxt/fabsf(sum)) > 1.0e17 )
            {
            pcanc = 1.0;
            goto blowup;
            }
    */
        an += 1.0;
        bn += 1.0;
        n += 1.0;
        }

    pdone:

    /* estimate error due to roundoff and cancellation */
    if( sum != 0.0 )
        maxt /= fabsf(sum);
    maxt *= MACHEPF;    /* this way avoids multiply overflow */
    pcanc = fabsf( MACHEPF * n  +  maxt );

    blowup:

    *err = pcanc;

    return( sum );
}

__device__ float hypergf( float a, float b, float x ) {
    float asum, psum, acanc, pcanc, temp;

    /* See if a Kummer transformation will help */
    temp = b - a;
    if( fabsf(temp) < 0.001 * fabsf(a) )
        return( expf(x) * hypergf( temp, b, -x )  );

    psum = hy1f1pf( a, b, x, &pcanc );
    if( pcanc < 1.0e-6 )
        goto done;

    /* try asymptotic series */

    asum = hy1f1af( a, b, x, &acanc );

    /* Pick the result with less estimated error */

    if( acanc < pcanc )
        {
        pcanc = acanc;
        psum = asum;
        }

    done:
    /* if( pcanc > 1.0e-3 )
        mtherr( "hyperg", PLOSS ); */

    return( psum );
}
