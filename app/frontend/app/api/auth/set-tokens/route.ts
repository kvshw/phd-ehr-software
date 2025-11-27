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

    // Set access token cookie (8 hours for development/demo)
    response.cookies.set('access_token', access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 8 * 60 * 60, // 8 hours (480 minutes)
      path: '/',
    });

    // Set refresh token cookie (30 days)
    response.cookies.set('refresh_token', refresh_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 30 * 24 * 60 * 60, // 30 days
      path: '/',
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

