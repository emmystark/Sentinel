(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/sep/Sentinel/frontend/src/lib/supabase.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "supabase",
    ()=>supabase
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = /*#__PURE__*/ __turbopack_context__.i("[project]/sep/Sentinel/frontend/node_modules/next/dist/build/polyfills/process.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f40$supabase$2f$supabase$2d$js$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/sep/Sentinel/frontend/node_modules/@supabase/supabase-js/dist/index.mjs [app-client] (ecmascript) <locals>");
;
const supabaseUrl = ("TURBOPACK compile-time value", "https://sujjlcdrihmffpttdbpr.supabase.co") || '';
const supabaseAnonKey = ("TURBOPACK compile-time value", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN1ampsY2RyaWhtZmZwdHRkYnByIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDQ4NzM2OCwiZXhwIjoyMDg2MDYzMzY4fQ.aoaiBjpDPpxhQLSP3NG95MoJ22guQm2Fnw0YsopldTo") || '';
const supabase = ("TURBOPACK compile-time truthy", 1) ? (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f40$supabase$2f$supabase$2d$js$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["createClient"])(supabaseUrl, supabaseAnonKey) : "TURBOPACK unreachable";
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/sep/Sentinel/frontend/src/app/login/page.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>LoginPage
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/sep/Sentinel/frontend/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/sep/Sentinel/frontend/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/sep/Sentinel/frontend/node_modules/next/navigation.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/sep/Sentinel/frontend/node_modules/next/dist/client/app-dir/link.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$src$2f$lib$2f$supabase$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/sep/Sentinel/frontend/src/lib/supabase.ts [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
;
function LoginPage() {
    _s();
    const router = (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"])();
    const [email, setEmail] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])('');
    const [password, setPassword] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])('');
    const [error, setError] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])('');
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [success, setSuccess] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])('');
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
            const { data, error: authError } = await __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$src$2f$lib$2f$supabase$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["supabase"]?.auth.signInWithPassword({
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
            const redirectTo = ("TURBOPACK compile-time truthy", 1) ? `${window.location.origin}/auth/callback` : "TURBOPACK unreachable";
            const { error: authError_0 } = await __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$src$2f$lib$2f$supabase$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["supabase"]?.auth.signInWithOAuth({
                provider: 'google',
                options: {
                    redirectTo
                }
            }) ?? {
                error: new Error('Supabase not configured')
            };
            if (authError_0) {
                setError(authError_0.message || 'Google sign-in failed');
                return;
            }
            setSuccess('Redirecting to Google...');
        } catch (err_0) {
            const errorMsg_0 = err_0 instanceof Error ? err_0.message : 'Google sign-in failed';
            setError(errorMsg_0);
            console.error('Google login error:', err_0);
        } finally{
            setLoading(false);
        }
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        style: {
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
            padding: '20px'
        },
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            style: {
                width: '100%',
                maxWidth: '400px',
                background: 'rgba(30,41,59,0.8)',
                borderRadius: '16px',
                padding: '32px',
                border: '1px solid rgba(255,255,255,0.1)'
            },
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h1", {
                    style: {
                        color: '#fff',
                        fontSize: '1.5rem',
                        marginBottom: '8px'
                    },
                    children: "Sign in to Sentinel"
                }, void 0, false, {
                    fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                    lineNumber: 102,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                    style: {
                        color: '#94a3b8',
                        fontSize: '14px',
                        marginBottom: '24px'
                    },
                    children: "Track expenses and reach your savings goals"
                }, void 0, false, {
                    fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                    lineNumber: 107,
                    columnNumber: 9
                }, this),
                error && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        background: 'rgba(239,68,68,0.2)',
                        color: '#fca5a5',
                        padding: '12px',
                        borderRadius: '8px',
                        marginBottom: '16px',
                        fontSize: '14px',
                        border: '1px solid rgba(239,68,68,0.3)'
                    },
                    children: error
                }, void 0, false, {
                    fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                    lineNumber: 113,
                    columnNumber: 19
                }, this),
                success && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        background: 'rgba(34,197,94,0.2)',
                        color: '#86efac',
                        padding: '12px',
                        borderRadius: '8px',
                        marginBottom: '16px',
                        fontSize: '14px',
                        border: '1px solid rgba(34,197,94,0.3)'
                    },
                    children: success
                }, void 0, false, {
                    fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                    lineNumber: 125,
                    columnNumber: 21
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                    onSubmit: handleEmailLogin,
                    style: {
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '16px'
                    },
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                            type: "email",
                            placeholder: "Email",
                            value: email,
                            onChange: (e_0)=>setEmail(e_0.target.value),
                            required: true,
                            autoComplete: "email",
                            disabled: loading,
                            style: {
                                padding: '12px 16px',
                                borderRadius: '8px',
                                border: '1px solid rgba(255,255,255,0.2)',
                                background: 'rgba(15,23,42,0.6)',
                                color: '#fff',
                                fontSize: '16px',
                                opacity: loading ? 0.6 : 1
                            }
                        }, void 0, false, {
                            fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                            lineNumber: 142,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                            type: "password",
                            placeholder: "Password",
                            value: password,
                            onChange: (e_1)=>setPassword(e_1.target.value),
                            required: true,
                            autoComplete: "current-password",
                            minLength: 6,
                            disabled: loading,
                            style: {
                                padding: '12px 16px',
                                borderRadius: '8px',
                                border: '1px solid rgba(255,255,255,0.2)',
                                background: 'rgba(15,23,42,0.6)',
                                color: '#fff',
                                fontSize: '16px',
                                opacity: loading ? 0.6 : 1
                            }
                        }, void 0, false, {
                            fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                            lineNumber: 151,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            type: "submit",
                            disabled: loading,
                            style: {
                                padding: '12px 24px',
                                borderRadius: '8px',
                                background: 'linear-gradient(90deg, #3b82f6, #2563eb)',
                                color: '#fff',
                                border: 'none',
                                fontWeight: 600,
                                cursor: loading ? 'not-allowed' : 'pointer',
                                opacity: loading ? 0.7 : 1,
                                transition: 'opacity 0.2s'
                            },
                            children: loading ? 'Signing in...' : 'Sign in'
                        }, void 0, false, {
                            fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                            lineNumber: 160,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                    lineNumber: 137,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        display: 'flex',
                        alignItems: 'center',
                        gap: '16px',
                        margin: '20px 0'
                    },
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                flex: 1,
                                height: '1px',
                                background: 'rgba(255,255,255,0.2)'
                            }
                        }, void 0, false, {
                            fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                            lineNumber: 181,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                            style: {
                                color: '#64748b',
                                fontSize: '13px'
                            },
                            children: "or"
                        }, void 0, false, {
                            fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                            lineNumber: 186,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                flex: 1,
                                height: '1px',
                                background: 'rgba(255,255,255,0.2)'
                            }
                        }, void 0, false, {
                            fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                            lineNumber: 190,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                    lineNumber: 175,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                    onClick: handleGoogleLogin,
                    disabled: loading || !__TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$src$2f$lib$2f$supabase$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["supabase"],
                    style: {
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
                        cursor: loading || !__TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$src$2f$lib$2f$supabase$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["supabase"] ? 'not-allowed' : 'pointer',
                        opacity: loading || !__TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$src$2f$lib$2f$supabase$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["supabase"] ? 0.7 : 1
                    },
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("svg", {
                            width: "20",
                            height: "20",
                            viewBox: "0 0 24 24",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("path", {
                                    fill: "currentColor",
                                    d: "M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                                }, void 0, false, {
                                    fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                                    lineNumber: 211,
                                    columnNumber: 59
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("path", {
                                    fill: "currentColor",
                                    d: "M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                                }, void 0, false, {
                                    fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                                    lineNumber: 211,
                                    columnNumber: 211
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("path", {
                                    fill: "currentColor",
                                    d: "M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                                }, void 0, false, {
                                    fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                                    lineNumber: 211,
                                    columnNumber: 377
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("path", {
                                    fill: "currentColor",
                                    d: "M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                                }, void 0, false, {
                                    fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                                    lineNumber: 211,
                                    columnNumber: 535
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                            lineNumber: 211,
                            columnNumber: 11
                        }, this),
                        "Continue with Google"
                    ]
                }, void 0, true, {
                    fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                    lineNumber: 197,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                    style: {
                        color: '#94a3b8',
                        fontSize: '14px',
                        marginTop: '24px',
                        textAlign: 'center'
                    },
                    children: [
                        "Don't have an account?",
                        ' ',
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
                            href: "/signup",
                            style: {
                                color: '#60a5fa',
                                textDecoration: 'none',
                                fontWeight: 500
                            },
                            children: "Sign up"
                        }, void 0, false, {
                            fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                            lineNumber: 222,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
                    lineNumber: 215,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
            lineNumber: 94,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/sep/Sentinel/frontend/src/app/login/page.tsx",
        lineNumber: 86,
        columnNumber: 10
    }, this);
}
_s(LoginPage, "v1BI8DOJQuSzYfv+CKM5/A6YFIg=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$sep$2f$Sentinel$2f$frontend$2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"]
    ];
});
_c = LoginPage;
var _c;
__turbopack_context__.k.register(_c, "LoginPage");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
]);

//# sourceMappingURL=sep_Sentinel_frontend_src_7b6edfdc._.js.map