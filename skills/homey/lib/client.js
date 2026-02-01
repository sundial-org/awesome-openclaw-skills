const { AthomCloudAPI, HomeyAPI } = require('homey-api');
const fuzzy = require('./fuzzy');
const { cliError } = require('./errors');
const { resolveByIdOrName } = require('./resolve');

/**
 * Homey API client wrapper
 */
class HomeyClient {
  /**
   * @param {{mode?: 'local'|'cloud', token?: string, address?: string}} opts
   */
  constructor(opts = {}) {
    this.mode = opts.mode || 'cloud';

    if (this.mode === 'local') {
      this.localAddress = opts.address || null;
      this.localToken = opts.token || null;
      this.cloudToken = null;
    } else {
      this.cloudToken = opts.token || null;
      this.localAddress = null;
      this.localToken = null;
    }

    this.api = null;
    this.homeyApi = null;
    this.homey = null;
  }

  /**
   * Connect to Homey (local or cloud)
   */
  async connect() {
    if (this.mode === 'local') {
      if (!this.localAddress) {
        throw cliError('NO_TOKEN', 'HOMEY_ADDRESS is required for local mode');
      }
      if (!this.localToken) {
        throw cliError('NO_TOKEN', 'HOMEY_LOCAL_TOKEN is required for local mode');
      }

      this.homeyApi = await HomeyAPI.createLocalAPI({
        address: this.localAddress,
        token: this.localToken,
      });

      // Local API does not have a "cloud homey" wrapper.
      this.homey = {
        id: this.homeyApi.id,
        name: this.homeyApi.name,
      };

      return this.homeyApi;
    }

    // Cloud mode
    if (!this.cloudToken) {
      throw cliError('NO_TOKEN', 'HOMEY_TOKEN is required for cloud mode');
    }

    // Wrap the user-provided token as an OAuth bearer token.
    const token = new AthomCloudAPI.Token({
      token_type: 'bearer',
      access_token: this.cloudToken,
      refresh_token: null,
      expires_in: 0,
      grant_type: 'personal_access_token',
    });

    this.api = new AthomCloudAPI({
      token,
      // PATs can't be refreshed by the SDK.
      autoRefreshTokens: false,
    });

    const user = await this.api.getAuthenticatedUser();
    this.homey = await user.getFirstHomey();
    this.homeyApi = await this.homey.authenticate();

    return this.homeyApi;
  }

  async _ensureConnected() {
    if (!this.homeyApi) await this.connect();
  }

  _pickDevice(id, device, options = {}) {
    const capabilitiesObj = device.capabilitiesObj || {};
    const values = Object.fromEntries(
      Object.entries(capabilitiesObj).map(([capabilityId, cap]) => [capabilityId, cap?.value])
    );

    const picked = {
      id,
      name: device.name,
      // Both are useful: zoneId for lookups, zoneName for display
      zoneId: device.zone || null,
      zoneName: device.zoneName || null,
      zone: device.zoneName || device.zone || null,
      class: device.class,
      driverId: device.driverId || null,
      uri: device.uri || null,
      capabilities: device.capabilities || [],
      capabilitiesObj,
      values,
      available: device.available,
      ready: device.ready,
    };

    if (options.raw) {
      picked.raw = device;
    }

    return picked;
  }

  _pickFlow(id, flow, options = {}) {
    const picked = {
      id,
      name: flow.name,
      enabled: flow.enabled,
      folder: flow.folder || null,
    };

    if (options.raw) {
      picked.raw = flow;
    }

    return picked;
  }

  /**
   * Get all devices
   * @returns {Promise<Array>} Array of devices
   */
  async getDevices(options = {}) {
    await this._ensureConnected();

    const devicesObj = await this.homeyApi.devices.getDevices();
    return Object.entries(devicesObj).map(([id, device]) => this._pickDevice(id, device, options));
  }

  /**
   * Get device by ID or name (fuzzy)
   * @param {string} nameOrId Device name or ID
   * @returns {Promise<object>} Device object
   */
  async getDevice(nameOrId, options = {}) {
    await this._ensureConnected();

    const devicesObj = await this.homeyApi.devices.getDevices();

    const resolved = resolveByIdOrName(nameOrId, devicesObj, {
      typeLabel: 'device',
      threshold: options.threshold,
      getName: (d) => d.name,
    });

    return this._pickDevice(resolved.id, resolved.value, options);
  }

  /**
   * Set device capability value
   * @param {string} deviceId Device ID
   * @param {string} capability Capability ID
   * @param {any} value Value to set
   */
  async setCapability(deviceId, capability, value) {
    await this._ensureConnected();

    const device = await this.homeyApi.devices.getDevice({ id: deviceId });
    await device.setCapabilityValue({
      capabilityId: capability,
      value,
    });
  }

  /**
   * Get device capability value
   * @param {string} deviceId Device ID
   * @param {string} capability Capability ID
   * @returns {Promise<any>} Capability value
   */
  async getCapability(deviceId, capability) {
    await this._ensureConnected();

    const device = await this.homeyApi.devices.getDevice({ id: deviceId });
    return device.capabilitiesObj[capability]?.value;
  }

  /**
   * Get all flows
   * @returns {Promise<Array>} Array of flows
   */
  async getFlows(options = {}) {
    await this._ensureConnected();

    const flowsObj = await this.homeyApi.flow.getFlows();
    return Object.entries(flowsObj).map(([id, flow]) => this._pickFlow(id, flow, options));
  }

  /**
   * Search devices by query (returns multiple matches)
   */
  async searchDevices(query, options = {}) {
    await this._ensureConnected();

    const devicesObj = await this.homeyApi.devices.getDevices();
    const entries = Object.entries(devicesObj).map(([id, device]) => ({
      id,
      name: device.name,
      device,
    }));

    const q = String(query || '').trim();
    if (!q) {
      return Object.entries(devicesObj).map(([id, device]) => this._pickDevice(id, device, options));
    }

    const matches = fuzzy.fuzzySearch(q, entries, options.limit ?? 50);
    return matches.map(m => this._pickDevice(m.id, m.device, options));
  }

  /**
   * Search flows by query (returns multiple matches)
   */
  async searchFlows(query, options = {}) {
    await this._ensureConnected();

    const flowsObj = await this.homeyApi.flow.getFlows();
    const entries = Object.entries(flowsObj).map(([id, flow]) => ({
      id,
      name: flow.name,
      flow,
    }));

    const q = String(query || '').trim();
    if (!q) {
      return Object.entries(flowsObj).map(([id, flow]) => this._pickFlow(id, flow, options));
    }

    const matches = fuzzy.fuzzySearch(q, entries, options.limit ?? 50);
    return matches.map(m => this._pickFlow(m.id, m.flow, options));
  }

  /**
   * Trigger a flow by ID or name
   * @param {string} nameOrId Flow name or ID
   */
  async triggerFlow(nameOrId, options = {}) {
    await this._ensureConnected();

    const flowsObj = await this.homeyApi.flow.getFlows();

    const resolved = resolveByIdOrName(nameOrId, flowsObj, {
      typeLabel: 'flow',
      threshold: options.threshold,
      getName: (f) => f.name,
    });

    await resolved.value.trigger();
    return this._pickFlow(resolved.id, resolved.value, options);
  }

  /**
   * Get all zones
   * @returns {Promise<Array>} Array of zones
   */
  async getZones(options = {}) {
    await this._ensureConnected();

    const zonesObj = await this.homeyApi.zones.getZones();
    return Object.entries(zonesObj).map(([id, zone]) => {
      const picked = {
        id,
        name: zone.name,
        parent: zone.parent,
        icon: zone.icon,
      };
      if (options.raw) picked.raw = zone;
      return picked;
    });
  }

  /**
   * Get Homey status/info
   * @returns {Promise<object>} Homey info
   */
  async getStatus() {
    await this._ensureConnected();

    const system = await this.homeyApi.system.getInfo();

    const name = this.homey?.name || this.homeyApi?.name || system?.name || system?.hostname || 'Homey';
    const homeyId = this.homey?.id || this.homeyApi?.id || null;

    let addressHost = null;
    if (this.mode === 'local' && this.localAddress) {
      try {
        addressHost = new URL(this.localAddress).hostname;
      } catch {
        addressHost = null;
      }
    }

    return {
      name,
      platform: system?.platform || (this.mode === 'local' ? 'local' : 'cloud'),
      platformVersion: system?.platformVersion || (this.mode === 'local' ? 2 : null),
      hostname: system?.hostname || addressHost,
      // Backwards compatible field name (also set for local mode).
      cloudId: homeyId,
      // Preferred generic name.
      homeyId,
      connected: true,
      connectionMode: this.mode,
      ...(this.mode === 'local' ? { address: this.localAddress } : {}),
    };
  }
}

module.exports = HomeyClient;
