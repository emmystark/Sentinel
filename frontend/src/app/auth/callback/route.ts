import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get('code');

  if (code && supabaseUrl && supabaseAnonKey) {
    const supabase = createClient(supabaseUrl, supabaseAnonKey);
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    if (!error) {
      // Redirect to the correct frontend URL
      // Prioritize environment variable, fall back to the origin of the request
      const redirectUrl = process.env.NEXT_PUBLIC_FRONTEND_URL || 
                          (origin.includes('localhost') ? 'http://localhost:3001' : origin);
      return NextResponse.redirect(redirectUrl);
    }
  }
  
  const redirectUrl = process.env.NEXT_PUBLIC_FRONTEND_URL || 
                      (origin.includes('localhost') ? 'http://localhost:3001' : origin);
  return NextResponse.redirect(`${redirectUrl}/login?error=auth`);
}
