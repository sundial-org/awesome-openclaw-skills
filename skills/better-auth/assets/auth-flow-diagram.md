# better-auth Authentication Flow Diagrams

Visual representations of common authentication flows using better-auth.

---

## 1. Email/Password Sign-Up Flow

```
┌─────────┐                 ┌─────────┐                 ┌──────────┐
│ Client  │                 │ Worker  │                 │    D1    │
└────┬────┘                 └────┬────┘                 └────┬─────┘
     │                           │                           │
     │  POST /api/auth/signup    │                           │
     │  { email, password }      │                           │
     ├──────────────────────────>│                           │
     │                           │  Hash password (bcrypt)   │
     │                           │                           │
     │                           │  INSERT INTO users        │
     │                           ├──────────────────────────>│
     │                           │                           │
     │                           │  Generate verification    │
     │                           │  token                    │
     │                           │                           │
     │                           │  INSERT INTO              │
     │                           │  verification_tokens      │
     │                           ├──────────────────────────>│
     │                           │                           │
     │                           │  Send verification email  │
     │                           │  (via email service)      │
     │                           │                           │
     │  { success: true }        │                           │
     │<──────────────────────────┤                           │
     │                           │                           │
     │                           │                           │
     │  User clicks email link   │                           │
     │                           │                           │
     │  GET /api/auth/verify?    │                           │
     │      token=xyz            │                           │
     ├──────────────────────────>│                           │
     │                           │  Verify token             │
     │                           ├──────────────────────────>│
     │                           │                           │
     │                           │  UPDATE users SET         │
     │                           │  email_verified = true    │
     │                           ├──────────────────────────>│
     │                           │                           │
     │  Redirect to dashboard    │                           │
     │<──────────────────────────┤                           │
     │                           │                           │
```

---

## 2. Social Sign-In Flow (Google OAuth)

```
┌─────────┐       ┌─────────┐       ┌──────────┐       ┌─────────┐
│ Client  │       │ Worker  │       │    D1    │       │ Google  │
└────┬────┘       └────┬────┘       └────┬─────┘       └────┬────┘
     │                 │                  │                  │
     │  Click "Sign    │                  │                  │
     │  in with        │                  │                  │
     │  Google"        │                  │                  │
     │                 │                  │                  │
     │  POST /api/     │                  │                  │
     │  auth/signin/   │                  │                  │
     │  google         │                  │                  │
     ├────────────────>│                  │                  │
     │                 │  Generate OAuth  │                  │
     │                 │  state + PKCE    │                  │
     │                 │                  │                  │
     │  Redirect to    │                  │                  │
     │  Google OAuth   │                  │                  │
     │<────────────────┤                  │                  │
     │                 │                  │                  │
     │                 │                  │                  │
     │  User authorizes on Google         │                  │
     ├───────────────────────────────────────────────────────>│
     │                 │                  │                  │
     │                 │                  │  User approves  │
     │<───────────────────────────────────────────────────────┤
     │                 │                  │                  │
     │  Redirect to    │                  │                  │
     │  callback with  │                  │                  │
     │  code           │                  │                  │
     │                 │                  │                  │
     │  GET /api/auth/ │                  │                  │
     │  callback/      │                  │                  │
     │  google?code=   │                  │                  │
     ├────────────────>│                  │                  │
     │                 │  Exchange code   │                  │
     │                 │  for tokens      │                  │
     │                 ├─────────────────────────────────────>│
     │                 │                  │                  │
     │                 │  { access_token, │                  │
     │                 │    id_token }    │                  │
     │                 │<─────────────────────────────────────┤
     │                 │                  │                  │
     │                 │  Fetch user info │                  │
     │                 ├─────────────────────────────────────>│
     │                 │                  │                  │
     │                 │  { email, name,  │                  │
     │                 │    picture }     │                  │
     │                 │<─────────────────────────────────────┤
     │                 │                  │                  │
     │                 │  Find or create  │                  │
     │                 │  user            │                  │
     │                 ├─────────────────>│                  │
     │                 │                  │                  │
     │                 │  Store account   │                  │
     │                 │  (provider data) │                  │
     │                 ├─────────────────>│                  │
     │                 │                  │                  │
     │                 │  Create session  │                  │
     │                 ├─────────────────>│                  │
     │                 │                  │                  │
     │  Set session    │                  │                  │
     │  cookie +       │                  │                  │
     │  redirect       │                  │                  │
     │<────────────────┤                  │                  │
     │                 │                  │                  │
```

---

## 3. Session Verification Flow

```
┌─────────┐              ┌─────────┐              ┌──────────┐
│ Client  │              │ Worker  │              │    KV    │
└────┬────┘              └────┬────┘              └────┬─────┘
     │                        │                        │
     │  GET /api/protected    │                        │
     │  Cookie: session=xyz   │                        │
     ├───────────────────────>│                        │
     │                        │  Extract session ID    │
     │                        │  from cookie           │
     │                        │                        │
     │                        │  GET session from KV   │
     │                        ├───────────────────────>│
     │                        │                        │
     │                        │  { userId, expiresAt } │
     │                        │<───────────────────────┤
     │                        │                        │
     │                        │  Check expiration      │
     │                        │                        │
     │  If valid:             │                        │
     │  { data: ... }         │                        │
     │<───────────────────────┤                        │
     │                        │                        │
     │  If invalid:           │                        │
     │  401 Unauthorized      │                        │
     │<───────────────────────┤                        │
     │                        │                        │
```

---

## 4. Password Reset Flow

```
┌─────────┐              ┌─────────┐              ┌──────────┐
│ Client  │              │ Worker  │              │    D1    │
└────┬────┘              └────┬────┘              └────┬─────┘
     │                        │                        │
     │  POST /api/auth/       │                        │
     │  forgot-password       │                        │
     │  { email }             │                        │
     ├───────────────────────>│                        │
     │                        │  Find user by email    │
     │                        ├───────────────────────>│
     │                        │                        │
     │                        │  Generate reset token  │
     │                        │                        │
     │                        │  INSERT INTO           │
     │                        │  verification_tokens   │
     │                        ├───────────────────────>│
     │                        │                        │
     │                        │  Send reset email      │
     │                        │                        │
     │  { success: true }     │                        │
     │<───────────────────────┤                        │
     │                        │                        │
     │                        │                        │
     │  User clicks email     │                        │
     │  link                  │                        │
     │                        │                        │
     │  GET /reset-password?  │                        │
     │      token=xyz         │                        │
     ├───────────────────────>│                        │
     │                        │  Verify token          │
     │                        ├───────────────────────>│
     │                        │                        │
     │  Show reset form       │                        │
     │<───────────────────────┤                        │
     │                        │                        │
     │  POST /api/auth/       │                        │
     │  reset-password        │                        │
     │  { token, password }   │                        │
     ├───────────────────────>│                        │
     │                        │  Hash new password     │
     │                        │                        │
     │                        │  UPDATE users          │
     │                        ├───────────────────────>│
     │                        │                        │
     │                        │  DELETE token          │
     │                        ├───────────────────────>│
     │                        │                        │
     │  Redirect to login     │                        │
     │<───────────────────────┤                        │
     │                        │                        │
```

---

## 5. Two-Factor Authentication (2FA) Flow

```
┌─────────┐              ┌─────────┐              ┌──────────┐
│ Client  │              │ Worker  │              │    D1    │
└────┬────┘              └────┬────┘              └────┬─────┘
     │                        │                        │
     │  POST /api/auth/       │                        │
     │  signin                │                        │
     │  { email, password }   │                        │
     ├───────────────────────>│                        │
     │                        │  Verify credentials    │
     │                        ├───────────────────────>│
     │                        │                        │
     │                        │  Check if 2FA enabled  │
     │                        ├───────────────────────>│
     │                        │                        │
     │  { requires2FA: true } │                        │
     │<───────────────────────┤                        │
     │                        │                        │
     │  Show 2FA input        │                        │
     │                        │                        │
     │  POST /api/auth/       │                        │
     │  verify-2fa            │                        │
     │  { code: "123456" }    │                        │
     ├───────────────────────>│                        │
     │                        │  Get 2FA secret        │
     │                        ├───────────────────────>│
     │                        │                        │
     │                        │  Verify TOTP code      │
     │                        │                        │
     │  If valid:             │                        │
     │  Create session        │                        │
     │  + redirect            │                        │
     │<───────────────────────┤                        │
     │                        │                        │
```

---

## 6. Organization/Team Flow

```
┌─────────┐              ┌─────────┐              ┌──────────┐
│ Client  │              │ Worker  │              │    D1    │
└────┬────┘              └────┬────┘              └────┬─────┘
     │                        │                        │
     │  POST /api/org/create  │                        │
     │  { name, slug }        │                        │
     ├───────────────────────>│                        │
     │                        │  Verify session        │
     │                        │                        │
     │                        │  INSERT INTO orgs      │
     │                        ├───────────────────────>│
     │                        │                        │
     │                        │  INSERT INTO           │
     │                        │  org_members           │
     │                        │  (user as owner)       │
     │                        ├───────────────────────>│
     │                        │                        │
     │  { org: { ... } }      │                        │
     │<───────────────────────┤                        │
     │                        │                        │
     │                        │                        │
     │  POST /api/org/invite  │                        │
     │  { orgId, email,       │                        │
     │    role }              │                        │
     ├───────────────────────>│                        │
     │                        │  Check permissions     │
     │                        ├───────────────────────>│
     │                        │                        │
     │                        │  Generate invite token │
     │                        │                        │
     │                        │  INSERT INTO           │
     │                        │  org_invitations       │
     │                        ├───────────────────────>│
     │                        │                        │
     │                        │  Send invite email     │
     │                        │                        │
     │  { success: true }     │                        │
     │<───────────────────────┤                        │
     │                        │                        │
```

---

## Database Schema Overview

```
┌──────────────────────┐
│       users          │
├──────────────────────┤
│ id (PK)              │
│ email (UNIQUE)       │
│ email_verified       │
│ name                 │
│ image                │
│ role                 │
│ created_at           │
│ updated_at           │
└──────────┬───────────┘
           │
           │ 1:N
           │
┌──────────┴───────────┐        ┌──────────────────────┐
│     sessions         │        │      accounts        │
├──────────────────────┤        ├──────────────────────┤
│ id (PK)              │        │ id (PK)              │
│ user_id (FK)         │◄───────┤ user_id (FK)         │
│ expires_at           │        │ provider             │
│ ip_address           │        │ provider_account_id  │
│ user_agent           │        │ access_token         │
│ created_at           │        │ refresh_token        │
└──────────────────────┘        │ expires_at           │
                                │ created_at           │
                                └──────────────────────┘

┌──────────────────────┐
│  verification_tokens │
├──────────────────────┤
│ identifier           │
│ token                │
│ expires              │
│ created_at           │
└──────────────────────┘

┌──────────────────────┐        ┌──────────────────────┐
│   organizations      │        │ organization_members │
├──────────────────────┤        ├──────────────────────┤
│ id (PK)              │        │ id (PK)              │
│ name                 │        │ organization_id (FK) │◄──┐
│ slug (UNIQUE)        │◄───────┤ user_id (FK)         │   │
│ logo                 │        │ role                 │   │
│ created_at           │        │ created_at           │   │
│ updated_at           │        └──────────────────────┘   │
└──────────────────────┘                                    │
                                                            │
┌──────────────────────┐                                    │
│organization_invites  │                                    │
├──────────────────────┤                                    │
│ id (PK)              │                                    │
│ organization_id (FK) │────────────────────────────────────┘
│ email                │
│ role                 │
│ invited_by (FK)      │
│ token                │
│ expires_at           │
│ created_at           │
└──────────────────────┘
```

---

These diagrams illustrate the complete authentication flows supported by better-auth. Use them as reference when implementing auth in your application.
