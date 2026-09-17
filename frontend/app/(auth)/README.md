# Authentication Routes

This folder contains sign-in and identity verification pages. `(auth)` is a Next.js route group and does not appear in the public URL.

## Files

```text
(auth)/
├── login/page.tsx             Sign-in
├── signup/page.tsx            Account creation
├── otp/page.tsx               One-time password verification
├── two-factor/page.tsx        Second-factor verification
└── README.md                  This documentation
```

## Authentication Flow

### Sign up

```text
/signup
    -> submit name, email/phone, and password
    -> FastAPI validates input and creates a pending account
    -> OTP is sent
    -> /otp verifies the code
    -> account becomes active
    -> customer is signed in and redirected to the storefront
```

### Sign in

```text
/login
    -> submit credentials
    -> FastAPI verifies the password
    -> if 2FA is enabled, redirect to /two-factor
    -> otherwise create a secure session
    -> redirect to the requested page or home
```

### Verification

- `/otp` verifies a time-limited one-time password.
- `/two-factor` verifies the second authentication factor for an existing account.
- Codes must expire, be rate-limited, and never be logged or returned in API responses.

## Route Responsibilities

| Route | Responsibility |
| --- | --- |
| `/login` | Authenticate an existing customer or administrator |
| `/signup` | Validate and begin account registration |
| `/otp` | Verify phone/email ownership with an OTP |
| `/two-factor` | Complete multi-factor authentication |

## Security Rules

- Hash passwords in the backend; never store plain text passwords.
- Use secure, HTTP-only, same-site session cookies where possible.
- Rate-limit login, signup, OTP, and 2FA attempts.
- Return generic credential errors to avoid account enumeration.
- Validate all values at the API boundary.
- Keep payment, database, Redis, and signing secrets server-side.

## Component Ownership

Authentication UI belongs under `components/auth/`. Session state belongs under `context/AuthContext/` and `hooks/useAuth.ts`. Auth requests belong in `services/api/auth.api.ts`; shared input and validation helpers belong under `components/shared/` and `lib/utils/`.
