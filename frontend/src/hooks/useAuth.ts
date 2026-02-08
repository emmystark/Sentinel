"use client";

import { useState, useEffect } from 'react';
import { User } from '@supabase/supabase-js';
import { supabase } from '@/lib/supabase';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!supabase) {
      setLoading(false);
      return;
    }
    
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
      setAccessToken(session?.access_token ?? null);
      setLoading(false);
    });
    
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
      setAccessToken(session?.access_token ?? null);
    });
    
    return () => subscription.unsubscribe();
  }, []);

  const signOut = async () => {
    await supabase?.auth.signOut();
  };

  return { user, loading, signOut, userId: user?.id ?? null, accessToken };
}
