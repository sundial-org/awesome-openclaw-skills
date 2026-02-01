/**
 * OneMolt - One Molt Per Human
 *
 * Cryptographically prove your openclaw identity using Ed25519 digital
 * signatures combined with WorldID proof-of-personhood.
 *
 * This plugin provides identity verification for molt bots, ensuring
 * each bot is operated by a verified unique human (Sybil resistance).
 */

import type { PluginContext, PluginExports } from 'openclaw';

export interface OneMoltConfig {
  identityServer?: string;
}

const DEFAULT_IDENTITY_SERVER = 'https://onemolt.ai';

export default function onemolt(ctx: PluginContext<OneMoltConfig>): PluginExports {
  const config = ctx.config ?? {};
  const identityServer = config.identityServer ?? DEFAULT_IDENTITY_SERVER;

  // Set environment variable for the shell scripts
  process.env.IDENTITY_SERVER = identityServer;

  return {
    name: 'onemolt',

    async onLoad() {
      ctx.log.info(`OneMolt loaded with identity server: ${identityServer}`);
    },

    async onUnload() {
      ctx.log.info('OneMolt unloaded');
    }
  };
}
