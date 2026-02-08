module.exports = [
"[externals]/next/dist/compiled/next-server/app-page-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-page-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/action-async-storage.external.js [external] (next/dist/server/app-render/action-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/action-async-storage.external.js", () => require("next/dist/server/app-render/action-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-unit-async-storage.external.js [external] (next/dist/server/app-render/work-unit-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-unit-async-storage.external.js", () => require("next/dist/server/app-render/work-unit-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-async-storage.external.js [external] (next/dist/server/app-render/work-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-async-storage.external.js", () => require("next/dist/server/app-render/work-async-storage.external.js"));

module.exports = mod;
}),
"[project]/sep/Sentinel/frontend/src/lib/supabase.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "supabase",
    ()=>supabase
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f40$supabase$2f$supabase$2d$js$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/sep/Sentinel/frontend/node_modules/@supabase/supabase-js/dist/index.mjs [app-ssr] (ecmascript) <locals>");
;
const supabaseUrl = ("TURBOPACK compile-time value", "https://sujjlcdrihmffpttdbpr.supabase.co") || '';
const supabaseAnonKey = ("TURBOPACK compile-time value", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN1ampsY2RyaWhtZmZwdHRkYnByIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDQ4NzM2OCwiZXhwIjoyMDg2MDYzMzY4fQ.aoaiBjpDPpxhQLSP3NG95MoJ22guQm2Fnw0YsopldTo") || '';
const supabase = ("TURBOPACK compile-time truthy", 1) ? (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f40$supabase$2f$supabase$2d$js$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createClient"])(supabaseUrl, supabaseAnonKey) : "TURBOPACK unreachable";
}),
"[project]/sep/Sentinel/frontend/src/app/login/page.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>LoginPage
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/sep/Sentinel/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/sep/Sentinel/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/sep/Sentinel/frontend/node_modules/next/navigation.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/sep/Sentinel/frontend/node_modules/next/dist/client/app-dir/link.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$src$2f$lib$2f$supabase$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/sep/Sentinel/frontend/src/lib/supabase.ts [app-ssr] (ecmascript)");
"use client";
;
;
;
;
;
function LoginPage() {
    const router = (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useRouter"])();
    const [email, setEmail] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])('');
    const [password, setPassword] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])('');
    const [error, setError] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])('');
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const [success, setSuccess] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])('');
    const [mounted, setMounted] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        setMounted(true);
    }, []);
    const handleEmailLogin = async (e)=>{
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
            const { data, error: authError } = await __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$src$2f$lib$2f$supabase$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["supabase"]?.auth.signInWithPassword({
                email,
                password
            }) ?? {
                data: null,
                error: new Error('Supabase not configured')
            };
            if (authError) {
                setError(authError.message || 'Login failed. Please check your credentials.');
                return;
            }
            if (data?.user) {
                setSuccess('Login successful! Redirecting...');
                setTimeout(()=>{
                    router.push('/');
                    router.refresh();
                }, 1000);
            }
        } catch (err) {
            const errorMsg = err instanceof Error ? err.message : 'Login failed';
            setError(errorMsg);
            console.error('Login error:', err);
        } finally{
            setLoading(false);
        }
    };
    const handleGoogleLogin = async ()=>{
        setError('');
        setSuccess('');
        setLoading(true);
        try {
            const redirectTo = ("TURBOPACK compile-time falsy", 0) ? "TURBOPACK unreachable" : undefined;
            const { error: authError } = await __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$src$2f$lib$2f$supabase$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["supabase"]?.auth.signInWithOAuth({
                provider: 'google',
                options: {
                    redirectTo
                }
            }) ?? {
                error: new Error('Supabase not configured')
            };
            if (authError) {
                setError(authError.message || 'Google sign-in failed');
                return;
            }
            setSuccess('Redirecting to Google...');
        } catch (err) {
            const errorMsg = err instanceof Error ? err.message : 'Google sign-in failed';
            setError(errorMsg);
            console.error('Google login error:', err);
        } finally{
            setLoading(false);
        }
    };
    if (!mounted) return null;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        style: {
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
        },
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    position: 'absolute',
                    top: '-50%',
                    left: '-50%',
                    width: '200%',
                    height: '200%',
                    background: 'radial-gradient(circle, rgba(59,130,246,0.1) 0%, transparent 70%)',
                    animation: 'float 20s ease-in-out infinite',
                    pointerEvents: 'none'
                }
            }, void 0, false, {
                fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                lineNumber: 104,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("style", {
                children: `
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
      `
            }, void 0, false, {
                fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                lineNumber: 115,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "login-card",
                style: {
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
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            marginBottom: '36px',
                            textAlign: 'center'
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("img", {
                                src: "./logo.png",
                                style: {
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
                                },
                                alt: ""
                            }, void 0, false, {
                                fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                                lineNumber: 199,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h1", {
                                className: "login-title",
                                style: {
                                    color: '#fff',
                                    fontSize: '32px',
                                    marginBottom: '8px',
                                    fontWeight: '800',
                                    background: 'linear-gradient(135deg, #fff 0%, #e0e7ff 100%)',
                                    WebkitBackgroundClip: 'text',
                                    WebkitTextFillColor: 'transparent',
                                    backgroundClip: 'text'
                                },
                                children: "Sentinel"
                            }, void 0, false, {
                                fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                                lineNumber: 213,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                className: "login-subtitle",
                                style: {
                                    color: '#94a3b8',
                                    fontSize: '16px',
                                    margin: 0,
                                    fontWeight: '400',
                                    letterSpacing: '0.3px'
                                },
                                children: "Smart financial management"
                            }, void 0, false, {
                                fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                                lineNumber: 224,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                        lineNumber: 198,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h2", {
                        style: {
                            color: '#e2e8f0',
                            fontSize: '20px',
                            marginBottom: '28px',
                            fontWeight: '600',
                            textAlign: 'center'
                        },
                        children: "Sign in to your account"
                    }, void 0, false, {
                        fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                        lineNumber: 234,
                        columnNumber: 9
                    }, this),
                    error && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            background: 'rgba(239, 68, 68, 0.15)',
                            color: '#fca5a5',
                            padding: '14px 16px',
                            borderRadius: '12px',
                            marginBottom: '16px',
                            fontSize: '14px',
                            border: '1px solid rgba(239, 68, 68, 0.3)',
                            animation: 'slideUp 0.3s ease-out'
                        },
                        children: error
                    }, void 0, false, {
                        fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                        lineNumber: 244,
                        columnNumber: 11
                    }, this),
                    success && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            background: 'rgba(34, 197, 94, 0.15)',
                            color: '#86efac',
                            padding: '14px 16px',
                            borderRadius: '12px',
                            marginBottom: '16px',
                            fontSize: '14px',
                            border: '1px solid rgba(34, 197, 94, 0.3)',
                            animation: 'slideUp 0.3s ease-out'
                        },
                        children: success
                    }, void 0, false, {
                        fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                        lineNumber: 260,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                        className: "form-container",
                        onSubmit: handleEmailLogin,
                        style: {
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '14px'
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                        style: {
                                            display: 'block',
                                            color: '#cbd5e1',
                                            fontSize: '13px',
                                            fontWeight: '500',
                                            marginBottom: '8px',
                                            textTransform: 'uppercase',
                                            letterSpacing: '0.5px',
                                            opacity: 0.8
                                        },
                                        children: "Email Address"
                                    }, void 0, false, {
                                        fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                                        lineNumber: 277,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                        type: "email",
                                        placeholder: "you@example.com",
                                        value: email,
                                        onChange: (e)=>setEmail(e.target.value),
                                        required: true,
                                        autoComplete: "email",
                                        disabled: loading,
                                        style: {
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
                                        }
                                    }, void 0, false, {
                                        fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                                        lineNumber: 287,
                                        columnNumber: 13
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                                lineNumber: 276,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                        style: {
                                            display: 'block',
                                            color: '#cbd5e1',
                                            fontSize: '13px',
                                            fontWeight: '500',
                                            marginBottom: '8px',
                                            textTransform: 'uppercase',
                                            letterSpacing: '0.5px',
                                            opacity: 0.8
                                        },
                                        children: "Password"
                                    }, void 0, false, {
                                        fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                                        lineNumber: 312,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                        type: "password",
                                        placeholder: "••••••••",
                                        value: password,
                                        onChange: (e)=>setPassword(e.target.value),
                                        required: true,
                                        autoComplete: "current-password",
                                        minLength: 6,
                                        disabled: loading,
                                        style: {
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
                                        }
                                    }, void 0, false, {
                                        fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                                        lineNumber: 322,
                                        columnNumber: 13
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                                lineNumber: 311,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "submit",
                                disabled: loading,
                                style: {
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
                                },
                                children: loading ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    style: {
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        gap: '8px'
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            style: {
                                                display: 'inline-block',
                                                width: '14px',
                                                height: '14px',
                                                border: '2px solid rgba(255,255,255,0.3)',
                                                borderTop: '2px solid #fff',
                                                borderRadius: '50%',
                                                animation: 'spin 0.8s linear infinite'
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                                            lineNumber: 369,
                                            columnNumber: 17
                                        }, this),
                                        "Signing in..."
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                                    lineNumber: 368,
                                    columnNumber: 15
                                }, this) : 'Sign in'
                            }, void 0, false, {
                                fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                                lineNumber: 347,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                        lineNumber: 275,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: 'flex',
                            alignItems: 'center',
                            gap: '16px',
                            margin: '24px 0'
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    flex: 1,
                                    height: '1px',
                                    background: 'rgba(255, 255, 255, 0.1)'
                                }
                            }, void 0, false, {
                                fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                                lineNumber: 388,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    color: '#64748b',
                                    fontSize: '12px',
                                    fontWeight: '500',
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.5px'
                                },
                                children: "New to Sentinel?"
                            }, void 0, false, {
                                fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                                lineNumber: 389,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    flex: 1,
                                    height: '1px',
                                    background: 'rgba(255, 255, 255, 0.1)'
                                }
                            }, void 0, false, {
                                fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                                lineNumber: 390,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                        lineNumber: 387,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                        style: {
                            color: '#cbd5e1',
                            fontSize: '15px',
                            textAlign: 'center',
                            margin: 0
                        },
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                            href: "/signup",
                            style: {
                                color: '#60a5fa',
                                textDecoration: 'none',
                                fontWeight: '600',
                                transition: 'all 0.2s ease',
                                borderBottom: '2px solid rgba(96, 165, 250, 0.3)',
                                paddingBottom: '2px'
                            },
                            children: "Create an account"
                        }, void 0, false, {
                            fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                            lineNumber: 395,
                            columnNumber: 11
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                        lineNumber: 394,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                        style: {
                            color: '#64748b',
                            fontSize: '12px',
                            marginTop: '20px',
                            textAlign: 'center'
                        },
                        children: [
                            "By signing in, you agree to our",
                            ' ',
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("a", {
                                href: "#",
                                style: {
                                    color: '#94a3b8',
                                    textDecoration: 'none'
                                },
                                children: "Terms of Service"
                            }, void 0, false, {
                                fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                                lineNumber: 415,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                        lineNumber: 408,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                lineNumber: 185,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
        lineNumber: 91,
        columnNumber: 5
    }, this);
}
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__33b3a680._.js.map