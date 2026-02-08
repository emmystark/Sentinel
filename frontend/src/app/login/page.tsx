"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { supabase } from '@/lib/supabase';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    if (!email || !password) {
      setError('Please enter email and password');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    try {
      const { data, error: authError } = await supabase?.auth.signInWithPassword({ 
        email, 
        password 
      }) ?? { data: null, error: new Error('Supabase not configured') };
      
      if (authError) {
        setError(authError.message || 'Login failed. Please check your credentials.');
        return;
      }
      
      if (data?.user) {
        setSuccess('Login successful! Redirecting...');
        setTimeout(() => {
          router.push('/');
          router.refresh();
        }, 1000);
      }
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : 'Login failed';
      setError(errorMsg);
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
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
        setError(authError.message || 'Google sign-in failed');
        return;
      }
      setSuccess('Redirecting to Google...');
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : 'Google sign-in failed';
      setError(errorMsg);
      console.error('Google login error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!mounted) return null;

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(-45deg, #1e3c72, #2a5298, #1a1a2e, #16213e)',
      backgroundSize: '400% 400%',
      animation: 'gradient 15s ease infinite',
      padding: '20px',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Animated background elements */}
      <div style={{
        position: 'absolute',
        top: '-50%',
        left: '-50%',
        width: '200%',
        height: '200%',
        background: 'radial-gradient(circle, rgba(59,130,246,0.1) 0%, transparent 70%)',
        animation: 'float 20s ease-in-out infinite',
        pointerEvents: 'none'
      }} />

      <style>{`
        @keyframes gradient {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        
        @keyframes float {
          0%, 100% { transform: translate(0, 0); }
          50% { transform: translate(30px, 30px); }
        }
        
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes shimmer {
          0% { background-position: -1000px 0; }
          100% { background-position: 1000px 0; }
        }
        
        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .login-card {
          animation: slideUp 0.6s ease-out;
        }

        .logo-badge {
          animation: slideUp 0.8s ease-out 0.1s both;
        }

        .login-title {
          animation: slideUp 0.8s ease-out 0.2s both;
        }

        .login-subtitle {
          animation: slideUp 0.8s ease-out 0.3s both;
        }

        .form-container {
          animation: slideUp 0.8s ease-out 0.4s both;
        }

        input:focus {
          outline: none;
          border-color: #3b82f6 !important;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
          background: rgba(15, 23, 42, 0.8) !important;
        }

        button:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
        }

        button:active:not(:disabled) {
          transform: translateY(0);
        }
      `}</style>

      {/* Main card */}
      <div className="login-card" style={{
        width: '100%',
        maxWidth: '450px',
        background: 'rgba(15, 23, 42, 0.7)',
        backdropFilter: 'blur(10px)',
        borderRadius: '20px',
        padding: '48px 40px',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3), 0 0 1px rgba(255, 255, 255, 0.05) inset',
        position: 'relative',
        zIndex: 10
      }}>
        {/* Logo and branding */}
        <div style={{ marginBottom: '36px', textAlign: 'center' }}>
          <img src="./logo.png" style={{
            width: '48px',
            height: '48px',
            background: 'white',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px',
            fontWeight: 'bold',
            color: '#fff',
            fontSize: '20px'
          }} alt="" />

          <h1 className="login-title" style={{
            color: '#fff',
            fontSize: '32px',
            marginBottom: '8px',
            fontWeight: '800',
            background: 'linear-gradient(135deg, #fff 0%, #e0e7ff 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>Sentinel</h1>

          <p className="login-subtitle" style={{
            color: '#94a3b8',
            fontSize: '16px',
            margin: 0,
            fontWeight: '400',
            letterSpacing: '0.3px'
          }}>Smart financial management</p>
        </div>

        {/* Sign in header */}
        <h2 style={{
          color: '#e2e8f0',
          fontSize: '20px',
          marginBottom: '28px',
          fontWeight: '600',
          textAlign: 'center'
        }}>Sign in to your account</h2>

        {/* Error message */}
        {error && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.15)',
            color: '#fca5a5',
            padding: '14px 16px',
            borderRadius: '12px',
            marginBottom: '16px',
            fontSize: '14px',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            animation: 'slideUp 0.3s ease-out'
          }}>
            {error}
          </div>
        )}

        {/* Success message */}
        {success && (
          <div style={{
            background: 'rgba(34, 197, 94, 0.15)',
            color: '#86efac',
            padding: '14px 16px',
            borderRadius: '12px',
            marginBottom: '16px',
            fontSize: '14px',
            border: '1px solid rgba(34, 197, 94, 0.3)',
            animation: 'slideUp 0.3s ease-out'
          }}>
            {success}
          </div>
        )}

        {/* Form */}
        <form className="form-container" onSubmit={handleEmailLogin} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div>
            <label style={{
              display: 'block',
              color: '#cbd5e1',
              fontSize: '13px',
              fontWeight: '500',
              marginBottom: '8px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              opacity: 0.8
            }}>Email Address</label>
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              disabled={loading}
              style={{
                width: '100%',
                padding: '14px 16px',
                borderRadius: '12px',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                background: 'rgba(15, 23, 42, 0.5)',
                color: '#fff',
                fontSize: '15px',
                fontFamily: 'inherit',
                transition: 'all 0.2s ease',
                opacity: loading ? 0.6 : 1,
                boxSizing: 'border-box'
              }}
            />
          </div>

          <div>
            <label style={{
              display: 'block',
              color: '#cbd5e1',
              fontSize: '13px',
              fontWeight: '500',
              marginBottom: '8px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              opacity: 0.8
            }}>Password</label>
            <input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              minLength={6}
              disabled={loading}
              style={{
                width: '100%',
                padding: '14px 16px',
                borderRadius: '12px',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                background: 'rgba(15, 23, 42, 0.5)',
                color: '#fff',
                fontSize: '15px',
                fontFamily: 'inherit',
                transition: 'all 0.2s ease',
                opacity: loading ? 0.6 : 1,
                boxSizing: 'border-box'
              }}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              padding: '14px 24px',
              marginTop: '8px',
              borderRadius: '12px',
              background: 'linear-gradient(90deg, #3b82f6, #2563eb)',
              color: '#fff',
              border: 'none',
              fontWeight: '600',
              fontSize: '16px',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.8 : 1,
              transition: 'all 0.3s ease',
              position: 'relative',
              overflow: 'hidden',
              boxShadow: '0 4px 16px rgba(59, 130, 246, 0.2)'
            }}
          >
            {loading ? (
              <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                <span style={{
                  display: 'inline-block',
                  width: '14px',
                  height: '14px',
                  border: '2px solid rgba(255,255,255,0.3)',
                  borderTop: '2px solid #fff',
                  borderRadius: '50%',
                  animation: 'spin 0.8s linear infinite'
                }} />
                Signing in...
              </span>
            ) : (
              'Sign in'
            )}
          </button>
        </form>

        {/* Divider */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', margin: '24px 0' }}>
          <div style={{ flex: 1, height: '1px', background: 'rgba(255, 255, 255, 0.1)' }} />
          <span style={{ color: '#64748b', fontSize: '12px', fontWeight: '500', textTransform: 'uppercase', letterSpacing: '0.5px' }}>New to Sentinel?</span>
          <div style={{ flex: 1, height: '1px', background: 'rgba(255, 255, 255, 0.1)' }} />
        </div>

        {/* Sign up link */}
        <p style={{ color: '#cbd5e1', fontSize: '15px', textAlign: 'center', margin: 0 }}>
          <Link href="/signup" style={{
            color: '#60a5fa',
            textDecoration: 'none',
            fontWeight: '600',
            transition: 'all 0.2s ease',
            borderBottom: '2px solid rgba(96, 165, 250, 0.3)',
            paddingBottom: '2px'
          }}>
            Create an account
          </Link>
        </p>

        {/* Footer text */}
        <p style={{
          color: '#64748b',
          fontSize: '12px',
          marginTop: '20px',
          textAlign: 'center'
        }}>
          By signing in, you agree to our{' '}
          <a href="#" style={{ color: '#94a3b8', textDecoration: 'none' }}>Terms of Service</a>
        </p>
      </div>
    </div>
  );
}
