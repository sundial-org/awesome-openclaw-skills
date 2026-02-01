/**
 * Next.js API Route with better-auth
 *
 * This example demonstrates:
 * - PostgreSQL with Drizzle ORM
 * - Email/password + social auth
 * - Email verification
 * - Organizations plugin
 * - 2FA plugin
 * - Custom error handling
 */

import { betterAuth } from 'better-auth'
import { drizzle } from 'drizzle-orm/postgres-js'
import postgres from 'postgres'
import { twoFactor, organization } from 'better-auth/plugins'
import { sendEmail } from '@/lib/email' // Your email service

// Database connection
const client = postgres(process.env.DATABASE_URL!)
const db = drizzle(client)

// Initialize better-auth
export const auth = betterAuth({
  database: db,

  secret: process.env.BETTER_AUTH_SECRET!,

  baseURL: process.env.NEXT_PUBLIC_APP_URL!,

  // Email/password authentication
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: true,

    // Custom email sending
    sendVerificationEmail: async ({ user, url, token }) => {
      await sendEmail({
        to: user.email,
        subject: 'Verify your email',
        html: `
          <h1>Verify your email</h1>
          <p>Click the link below to verify your email address:</p>
          <a href="${url}">Verify Email</a>
          <p>Or enter this code: <strong>${token}</strong></p>
          <p>This link expires in 24 hours.</p>
        `
      })
    },

    // Password reset email
    sendResetPasswordEmail: async ({ user, url, token }) => {
      await sendEmail({
        to: user.email,
        subject: 'Reset your password',
        html: `
          <h1>Reset your password</h1>
          <p>Click the link below to reset your password:</p>
          <a href="${url}">Reset Password</a>
          <p>Or enter this code: <strong>${token}</strong></p>
          <p>This link expires in 1 hour.</p>
        `
      })
    }
  },

  // Social providers
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      scope: ['openid', 'email', 'profile']
    },
    github: {
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
      scope: ['user:email', 'read:user']
    },
    microsoft: {
      clientId: process.env.MICROSOFT_CLIENT_ID!,
      clientSecret: process.env.MICROSOFT_CLIENT_SECRET!,
      tenantId: process.env.MICROSOFT_TENANT_ID || 'common'
    }
  },

  // Session configuration
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // Update every 24 hours
    cookieCache: {
      enabled: true,
      maxAge: 60 * 5 // 5 minutes
    }
  },

  // Advanced features via plugins
  plugins: [
    // Two-factor authentication
    twoFactor({
      methods: ['totp', 'sms'],
      issuer: 'MyApp',
      sendOTP: async ({ user, otp, method }) => {
        if (method === 'sms') {
          // Send SMS with OTP (use Twilio, etc.)
          console.log(`Send SMS to ${user.phone}: ${otp}`)
        }
      }
    }),

    // Organizations and teams
    organization({
      roles: ['owner', 'admin', 'member'],
      permissions: {
        owner: ['*'], // All permissions
        admin: ['read', 'write', 'delete', 'invite'],
        member: ['read']
      },
      sendInvitationEmail: async ({ email, organizationName, inviteUrl }) => {
        await sendEmail({
          to: email,
          subject: `You've been invited to ${organizationName}`,
          html: `
            <h1>You've been invited!</h1>
            <p>Click the link below to join ${organizationName}:</p>
            <a href="${inviteUrl}">Accept Invitation</a>
          `
        })
      }
    })
  ],

  // Custom error handling
  onError: (error, req) => {
    console.error('Auth error:', error)
    // Log to your error tracking service (Sentry, etc.)
  },

  // Success callbacks
  onSuccess: async (user, action) => {
    console.log(`User ${user.id} performed action: ${action}`)
    // Log auth events for security monitoring
  }
})

// Type definitions for TypeScript
export type Session = typeof auth.$Infer.Session
export type User = typeof auth.$Infer.User
