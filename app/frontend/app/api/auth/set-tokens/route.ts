/**
 * API route to set JWT tokens in HTTP-only cookies
 */
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { access_token, refresh_token } = await request.json();

    if (!access_token || !refresh_token) {
      return NextResponse.json(
        { error: 'Tokens are required' },
        { status: 400 }
      );
    }

    const response = NextResponse.json({ success: true });

    // Determine domain for cookies (shared parent domain for subdomains)
    const hostname = request.headers.get('host') || '';
    let cookieDomain: string | undefined = undefined;
    
    // If on Rahti (rahtiapp.fi), set domain to share cookies across subdomains
    if (hostname.includes('rahtiapp.fi')) {
      cookieDomain = '.2.rahtiapp.fi'; // Shared domain for all .2.rahtiapp.fi subdomains
    }
    // For production with custom domains, you might use: cookieDomain = '.yourdomain.com'

    // Set access token cookie (8 hours for development/demo)
    const cookieOptions: any = {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax' as const,
      maxAge: 8 * 60 * 60, // 8 hours (480 minutes)
      path: '/',
    };
    
    if (cookieDomain) {
      cookieOptions.domain = cookieDomain;
    }

    response.cookies.set('access_token', access_token, cookieOptions);

    // Set refresh token cookie (30 days)
    response.cookies.set('refresh_token', refresh_token, {
      ...cookieOptions,
      maxAge: 30 * 24 * 60 * 60, // 30 days
    });

    return response;
  } catch (error) {
    console.error('Error setting tokens:', error);
    return NextResponse.json(
      { error: 'Failed to set tokens' },
      { status: 500 }
    );
  }
}

