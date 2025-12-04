/**
 * API route to refresh access token using refresh token from cookies
 */
import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    // Get refresh token from cookies
    const refreshToken = request.cookies.get('refresh_token')?.value;

    if (!refreshToken) {
      return NextResponse.json(
        { error: 'No refresh token found' },
        { status: 401 }
      );
    }

    // Call backend refresh endpoint
    const response = await fetch(`${API_URL}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        refresh_token: refreshToken,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Refresh failed' }));
      return NextResponse.json(
        { error: error.detail || 'Token refresh failed' },
        { status: response.status }
      );
    }

    const tokens = await response.json();

    // Update tokens in cookies
    const nextResponse = NextResponse.json({ success: true });

    // Determine domain for cookies (shared parent domain for subdomains)
    const hostname = request.headers.get('host') || '';
    let cookieDomain: string | undefined = undefined;
    
    // If on Rahti (rahtiapp.fi), set domain to share cookies across subdomains
    if (hostname.includes('rahtiapp.fi')) {
      cookieDomain = '.2.rahtiapp.fi'; // Shared domain for all .2.rahtiapp.fi subdomains
    }

    const cookieOptions: any = {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax' as const,
      path: '/',
    };
    
    if (cookieDomain) {
      cookieOptions.domain = cookieDomain;
    }

    // Set access token cookie (8 hours)
    nextResponse.cookies.set('access_token', tokens.access_token, {
      ...cookieOptions,
      maxAge: 8 * 60 * 60, // 8 hours (480 minutes)
    });

    // Update refresh token if provided (some implementations rotate refresh tokens)
    if (tokens.refresh_token) {
      nextResponse.cookies.set('refresh_token', tokens.refresh_token, {
        ...cookieOptions,
        maxAge: 30 * 24 * 60 * 60, // 30 days
      });
    }

    return nextResponse;
  } catch (error) {
    console.error('Error refreshing token:', error);
    return NextResponse.json(
      { error: 'Failed to refresh token' },
      { status: 500 }
    );
  }
}

