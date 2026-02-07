"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { supabase } from '@/lib/supabase';

export default function SignupPage() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');

  const handleEmailSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!email) {
      setError('Please enter your email');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    try {
      const { data, error: authError } = await supabase?.auth.signUp({
        email,
        password,
        options: { 
          data: { 
            name: name || email.split('@')[0],
            email_verified: false
          } 
        }
      }) ?? { data: null, error: new Error('Supabase not configured') };
      
      if (authError) {
        setError(authError.message || 'Signup failed');
        return;
      }
      
      if (data?.user) {
        setSuccess('✅ Account created! Please check your email to verify. Redirecting...');
        setTimeout(() => {
          router.push('/');
          router.refresh();
        }, 2000);
      }
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : 'Signup failed';
      setError(errorMsg);
      console.error('Signup error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignup = async () => {
    setError('');
    setSuccess('');
    setLoading(true);
    try {
      const redirectTo = typeof window !== 'undefined' ? `${window.location.origin}/auth/callback` : undefined;
      const { error: authError } = await supabase?.auth.signInWithOAuth({
        provider: 'google',
        options: { redirectTo }
      }) ?? { error: new Error('Supabase not configured') };
      if (authError) {
        setError(authError.message || 'Google sign-up failed');
        return;
      }
      setSuccess('✅ Redirecting to Google...');
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : 'Google sign-up failed';
      setError(errorMsg);
      console.error('Google signup error:', err);
    } finally {
      setLoading(false);
    }
  };

  const passwordStrength = password.length >= 8 ? '✓ Strong' : `${password.length}/8`;

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
      padding: '20px'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '400px',
        background: 'rgba(30,41,59,0.8)',
        borderRadius: '16px',
        padding: '32px',
        border: '1px solid rgba(255,255,255,0.1)'
      }}>
        <h1 style={{ color: '#fff', fontSize: '1.5rem', marginBottom: '8px' }}>Create account</h1>
        <p style={{ color: '#94a3b8', fontSize: '14px', marginBottom: '24px' }}>Join Sentinel to track expenses and save smarter</p>

        {error && (
          <div style={{ 
            background: 'rgba(239,68,68,0.2)', 
            color: '#fca5a5', 
            padding: '12px', 
            borderRadius: '8px', 
            marginBottom: '16px', 
            fontSize: '14px',
            border: '1px solid rgba(239,68,68,0.3)'
          }}>
            {error}
          </div>
        )}

        {success && (
          <div style={{ 
            background: 'rgba(34,197,94,0.2)', 
            color: '#86efac', 
            padding: '12px', 
            borderRadius: '8px', 
            marginBottom: '16px', 
            fontSize: '14px',
            border: '1px solid rgba(34,197,94,0.3)'
          }}>
            {success}
          </div>
        )}

        <form onSubmit={handleEmailSignup} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <input
            type="text"
            placeholder="Name (optional)"
            value={name}
            onChange={(e) => setName(e.target.value)}
            autoComplete="name"
            disabled={loading}
            style={{
              padding: '12px 16px',
              borderRadius: '8px',
              border: '1px solid rgba(255,255,255,0.2)',
              background: 'rgba(15,23,42,0.6)',
              color: '#fff',
              fontSize: '16px',
              opacity: loading ? 0.6 : 1
            }}
          />
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
            disabled={loading}
            style={{
              padding: '12px 16px',
              borderRadius: '8px',
              border: '1px solid rgba(255,255,255,0.2)',
              background: 'rgba(15,23,42,0.6)',
              color: '#fff',
              fontSize: '16px',
              opacity: loading ? 0.6 : 1
            }}
          />
          <div style={{ position: 'relative' }}>
            <input
              type="password"
              placeholder="Password (min 8 characters)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="new-password"
              minLength={8}
              disabled={loading}
              style={{
                width: '100%',
                padding: '12px 16px',
                borderRadius: '8px',
                border: '1px solid rgba(255,255,255,0.2)',
                background: 'rgba(15,23,42,0.6)',
                color: '#fff',
                fontSize: '16px',
                boxSizing: 'border-box',
                opacity: loading ? 0.6 : 1
              }}
            />
            {password && (
              <span style={{
                position: 'absolute',
                right: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                fontSize: '12px',
                color: password.length >= 8 ? '#86efac' : '#fbbf24'
              }}>
                {passwordStrength}
              </span>
            )}
          </div>
          <input
            type="password"
            placeholder="Confirm Password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            autoComplete="new-password"
            minLength={8}
            disabled={loading}
            style={{
              padding: '12px 16px',
              borderRadius: '8px',
              border: '1px solid rgba(255,255,255,0.2)',
              background: 'rgba(15,23,42,0.6)',
              color: '#fff',
              fontSize: '16px',
              opacity: loading ? 0.6 : 1
            }}
          />
          <button
            type="submit"
            disabled={loading || password !== confirmPassword || password.length < 8}
            style={{
              padding: '12px 24px',
              borderRadius: '8px',
              background: 'linear-gradient(90deg, #10b981, #059669)',
              color: '#fff',
              border: 'none',
              fontWeight: 600,
              cursor: loading || password !== confirmPassword || password.length < 8 ? 'not-allowed' : 'pointer',
              opacity: loading || password !== confirmPassword || password.length < 8 ? 0.7 : 1,
              transition: 'opacity 0.2s'
            }}
          >
            {loading ? 'Creating account...' : 'Sign up'}
          </button>
        </form>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', margin: '20px 0' }}>
          <div style={{ flex: 1, height: '1px', background: 'rgba(255,255,255,0.2)' }} />
          <span style={{ color: '#64748b', fontSize: '13px' }}>or</span>
          <div style={{ flex: 1, height: '1px', background: 'rgba(255,255,255,0.2)' }} />
        </div>

        <button
          onClick={handleGoogleSignup}
          disabled={loading || !supabase}
          style={{
            width: '100%',
            padding: '12px 24px',
            borderRadius: '8px',
            background: 'rgba(255,255,255,0.1)',
            color: '#fff',
            border: '1px solid rgba(255,255,255,0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            cursor: loading || !supabase ? 'not-allowed' : 'pointer',
            opacity: loading || !supabase ? 0.7 : 1
          }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24"><path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
          Continue with Google
        </button>

        <p style={{ color: '#94a3b8', fontSize: '14px', marginTop: '24px', textAlign: 'center' }}>
          Already have an account?{' '}
          <Link href="/login" style={{ color: '#60a5fa', textDecoration: 'none', fontWeight: 500 }}>Sign in</Link>
        </p>
      </div>

    </div>

  );
}
