---
name: jb-ruleset-timeline-ui
description: Visual timeline explorer for Juicebox project ruleset history. Shows configuration evolution, upcoming changes, and enables ruleset comparison.
---

# Juicebox V5 Ruleset Timeline UI

Visual timeline explorer for Juicebox project ruleset history. Shows the evolution of project configurations over time.

## Uses Shared Components

This skill uses components from `/shared/`:

| Component | Purpose |
|-----------|---------|
| `styles.css` | Dark theme, cards, buttons, badges |
| `wallet-utils.js` | Chain config, formatting utilities |
| `chain-config.json` | RPC URLs, contract addresses |
| `abis/JBController.json` | Ruleset query functions |

## Overview

This skill generates vanilla JS/HTML interfaces for visualizing:
- Complete ruleset history for any project
- Timeline of configuration changes
- Upcoming queued rulesets
- Ruleset approval status
- Parameter comparisons between rulesets

## Ruleset Timeline UI Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Juicebox Ruleset Timeline</title>
  <link rel="stylesheet" href="/shared/styles.css">
  <style>
    /* Timeline-specific styles */
    .project-header { display: none; }
    .project-header.visible { display: block; }
    .project-name { font-size: 1.5rem; font-weight: 600; color: var(--text-secondary); }
    .project-id { color: var(--text-muted); margin-top: 5px; }

    .timeline-container { position: relative; padding-left: 40px; }
    .timeline-line { position: absolute; left: 15px; top: 0; bottom: 0; width: 2px; background: linear-gradient(180deg, var(--jb-yellow) 0%, var(--border-color) 100%); }

    .ruleset-card { position: relative; border-left: 3px solid var(--border-color); margin-bottom: var(--space-md); }
    .ruleset-card.current { border-left-color: var(--success); background: linear-gradient(90deg, var(--success-bg) 0%, var(--bg-secondary) 20%); }
    .ruleset-card.upcoming { border-left-color: var(--jb-yellow); background: linear-gradient(90deg, rgba(255,204,0,0.1) 0%, var(--bg-secondary) 20%); }
    .ruleset-card.past { opacity: 0.7; }

    .timeline-dot { position: absolute; left: -33px; top: 20px; width: 16px; height: 16px; border-radius: 50%; background: var(--border-color); border: 3px solid var(--bg-secondary); }
    .ruleset-card.current .timeline-dot { background: var(--success); }
    .ruleset-card.upcoming .timeline-dot { background: var(--jb-yellow); }

    .ruleset-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--space-md); }
    .ruleset-title { font-size: 1.1rem; font-weight: 600; color: var(--text-secondary); }
    .ruleset-status { padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
    .ruleset-status.current { background: var(--success-bg); color: var(--success); }
    .ruleset-status.upcoming { background: rgba(255,204,0,0.2); color: var(--jb-yellow); }
    .ruleset-status.past { background: rgba(136,136,136,0.2); color: var(--text-muted); }
    .ruleset-status.pending { background: var(--warning-bg); color: var(--warning); }

    .ruleset-dates { display: flex; gap: 20px; margin-bottom: var(--space-md); font-size: 13px; color: var(--text-muted); }
    .params-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: var(--space-md); }
    .param-item { background: var(--bg-tertiary); padding: 12px; border-radius: var(--radius-md); }
    .param-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; }
    .param-value { font-size: 14px; font-weight: 600; color: var(--text-secondary); }
    .param-value.changed { color: var(--jb-yellow); }

    .expand-btn { background: none; border: 1px solid var(--border-color); color: var(--text-muted); padding: 8px 16px; border-radius: 6px; cursor: pointer; margin-top: var(--space-md); font-size: 13px; }
    .expand-btn:hover { border-color: var(--jb-yellow); color: var(--jb-yellow); }
    .expanded-details { display: none; margin-top: var(--space-md); padding-top: var(--space-md); border-top: 1px solid var(--border-color); }
    .expanded-details.visible { display: block; }

    .legend { display: flex; gap: 20px; margin-bottom: var(--space-md); font-size: 13px; }
    .legend-item { display: flex; align-items: center; gap: 8px; }
    .legend-dot { width: 12px; height: 12px; border-radius: 50%; }
    .legend-dot.current { background: var(--success); }
    .legend-dot.upcoming { background: var(--jb-yellow); }
    .legend-dot.past { background: #666; }

    .compare-btn { background: var(--bg-tertiary); border: 1px solid var(--border-color); color: var(--text-primary); padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; margin-left: 10px; }
    .compare-btn:hover { border-color: var(--jb-yellow); }

    .compare-modal { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.8); z-index: 1000; padding: 20px; overflow-y: auto; }
    .compare-modal.visible { display: flex; justify-content: center; align-items: flex-start; }
    .compare-content { background: var(--bg-secondary); border-radius: var(--radius-lg); padding: 20px; max-width: 900px; width: 100%; margin-top: 40px; }
    .compare-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-md); }
    .close-btn { background: none; border: none; color: var(--text-muted); font-size: 24px; cursor: pointer; }
    .compare-table { width: 100%; border-collapse: collapse; }
    .compare-table th, .compare-table td { padding: 12px; text-align: left; border-bottom: 1px solid var(--border-color); }
    .compare-table th { color: var(--text-muted); font-weight: 500; }
    .compare-table td.changed { color: var(--jb-yellow); }
  </style>
</head>
<body>
  <div class="container">
    <h1>Ruleset Timeline</h1>

    <div class="card">
      <div class="row">
        <input type="number" id="projectId" placeholder="Project ID" min="1" style="flex: 1;">
        <select id="chainSelect" style="width: 150px;">
          <option value="1">Ethereum</option>
          <option value="10">Optimism</option>
          <option value="8453">Base</option>
          <option value="42161">Arbitrum</option>
          <option value="11155111">Sepolia</option>
        </select>
        <button onclick="loadTimeline()">Load Timeline</button>
      </div>
    </div>

    <div class="card project-header" id="projectHeader">
      <div class="project-name" id="projectName">-</div>
      <div class="project-id" id="projectIdDisplay">-</div>
    </div>

    <div class="legend" id="legend" style="display: none;">
      <div class="legend-item"><div class="legend-dot current"></div><span>Current Ruleset</span></div>
      <div class="legend-item"><div class="legend-dot upcoming"></div><span>Queued/Upcoming</span></div>
      <div class="legend-item"><div class="legend-dot past"></div><span>Past Rulesets</span></div>
    </div>

    <div id="timelineContainer"><div class="loading">Enter a project ID to load timeline</div></div>
  </div>

  <div class="compare-modal" id="compareModal">
    <div class="compare-content">
      <div class="compare-header">
        <h2>Compare Rulesets</h2>
        <button class="close-btn" onclick="closeCompare()">&times;</button>
      </div>
      <div id="compareBody"></div>
    </div>
  </div>

  <script type="module">
    import { createPublicClient, http, getContract, zeroAddress } from 'https://esm.sh/viem';
    import { CHAIN_CONFIGS, loadChainConfig } from '/shared/wallet-utils.js';

    const CONTROLLER_ABI = [
      { name: 'currentRulesetOf', type: 'function', stateMutability: 'view', inputs: [{ name: 'projectId', type: 'uint256' }], outputs: [{ name: 'ruleset', type: 'tuple', components: [{ name: 'cycleNumber', type: 'uint256' }, { name: 'id', type: 'uint256' }, { name: 'basedOnId', type: 'uint256' }, { name: 'start', type: 'uint256' }, { name: 'duration', type: 'uint256' }, { name: 'weight', type: 'uint256' }, { name: 'weightCutPercent', type: 'uint256' }, { name: 'approvalHook', type: 'address' }, { name: 'metadata', type: 'uint256' }] }, { name: 'metadata', type: 'tuple', components: [{ name: 'reservedRate', type: 'uint256' }, { name: 'cashOutTaxRate', type: 'uint256' }, { name: 'baseCurrency', type: 'uint256' }, { name: 'pausePay', type: 'bool' }, { name: 'pauseCashOut', type: 'bool' }, { name: 'pauseTransfers', type: 'bool' }, { name: 'allowOwnerMinting', type: 'bool' }, { name: 'allowTerminalMigration', type: 'bool' }, { name: 'allowSetTerminals', type: 'bool' }, { name: 'allowSetController', type: 'bool' }, { name: 'allowAddAccountingContexts', type: 'bool' }, { name: 'allowAddPriceFeed', type: 'bool' }, { name: 'ownerMustSendPayouts', type: 'bool' }, { name: 'holdFees', type: 'bool' }, { name: 'useTotalSurplusForCashOuts', type: 'bool' }, { name: 'useDataHookForPay', type: 'bool' }, { name: 'useDataHookForCashOut', type: 'bool' }, { name: 'dataHook', type: 'address' }, { name: 'metadata', type: 'uint256' }] }] },
      { name: 'upcomingRulesetOf', type: 'function', stateMutability: 'view', inputs: [{ name: 'projectId', type: 'uint256' }], outputs: [{ name: 'ruleset', type: 'tuple', components: [{ name: 'cycleNumber', type: 'uint256' }, { name: 'id', type: 'uint256' }, { name: 'basedOnId', type: 'uint256' }, { name: 'start', type: 'uint256' }, { name: 'duration', type: 'uint256' }, { name: 'weight', type: 'uint256' }, { name: 'weightCutPercent', type: 'uint256' }, { name: 'approvalHook', type: 'address' }, { name: 'metadata', type: 'uint256' }] }, { name: 'metadata', type: 'tuple', components: [{ name: 'reservedRate', type: 'uint256' }, { name: 'cashOutTaxRate', type: 'uint256' }, { name: 'baseCurrency', type: 'uint256' }, { name: 'pausePay', type: 'bool' }, { name: 'pauseCashOut', type: 'bool' }, { name: 'pauseTransfers', type: 'bool' }, { name: 'allowOwnerMinting', type: 'bool' }, { name: 'allowTerminalMigration', type: 'bool' }, { name: 'allowSetTerminals', type: 'bool' }, { name: 'allowSetController', type: 'bool' }, { name: 'allowAddAccountingContexts', type: 'bool' }, { name: 'allowAddPriceFeed', type: 'bool' }, { name: 'ownerMustSendPayouts', type: 'bool' }, { name: 'holdFees', type: 'bool' }, { name: 'useTotalSurplusForCashOuts', type: 'bool' }, { name: 'useDataHookForPay', type: 'bool' }, { name: 'useDataHookForCashOut', type: 'bool' }, { name: 'dataHook', type: 'address' }, { name: 'metadata', type: 'uint256' }] }] },
      { name: 'latestQueuedRulesetOf', type: 'function', stateMutability: 'view', inputs: [{ name: 'projectId', type: 'uint256' }], outputs: [{ name: 'ruleset', type: 'tuple', components: [{ name: 'cycleNumber', type: 'uint256' }, { name: 'id', type: 'uint256' }, { name: 'basedOnId', type: 'uint256' }, { name: 'start', type: 'uint256' }, { name: 'duration', type: 'uint256' }, { name: 'weight', type: 'uint256' }, { name: 'weightCutPercent', type: 'uint256' }, { name: 'approvalHook', type: 'address' }, { name: 'metadata', type: 'uint256' }] }, { name: 'metadata', type: 'tuple', components: [{ name: 'reservedRate', type: 'uint256' }, { name: 'cashOutTaxRate', type: 'uint256' }, { name: 'baseCurrency', type: 'uint256' }, { name: 'pausePay', type: 'bool' }, { name: 'pauseCashOut', type: 'bool' }, { name: 'pauseTransfers', type: 'bool' }, { name: 'allowOwnerMinting', type: 'bool' }, { name: 'allowTerminalMigration', type: 'bool' }, { name: 'allowSetTerminals', type: 'bool' }, { name: 'allowSetController', type: 'bool' }, { name: 'allowAddAccountingContexts', type: 'bool' }, { name: 'allowAddPriceFeed', type: 'bool' }, { name: 'ownerMustSendPayouts', type: 'bool' }, { name: 'holdFees', type: 'bool' }, { name: 'useTotalSurplusForCashOuts', type: 'bool' }, { name: 'useDataHookForPay', type: 'bool' }, { name: 'useDataHookForCashOut', type: 'bool' }, { name: 'dataHook', type: 'address' }, { name: 'metadata', type: 'uint256' }] }, { name: 'approvalStatus', type: 'uint256' }] },
      { name: 'allRulesetsOf', type: 'function', stateMutability: 'view', inputs: [{ name: 'projectId', type: 'uint256' }, { name: 'startingId', type: 'uint256' }, { name: 'size', type: 'uint256' }], outputs: [{ name: '', type: 'tuple[]', components: [{ name: 'ruleset', type: 'tuple', components: [{ name: 'cycleNumber', type: 'uint256' }, { name: 'id', type: 'uint256' }, { name: 'basedOnId', type: 'uint256' }, { name: 'start', type: 'uint256' }, { name: 'duration', type: 'uint256' }, { name: 'weight', type: 'uint256' }, { name: 'weightCutPercent', type: 'uint256' }, { name: 'approvalHook', type: 'address' }, { name: 'metadata', type: 'uint256' }] }, { name: 'metadata', type: 'tuple', components: [{ name: 'reservedRate', type: 'uint256' }, { name: 'cashOutTaxRate', type: 'uint256' }, { name: 'baseCurrency', type: 'uint256' }, { name: 'pausePay', type: 'bool' }, { name: 'pauseCashOut', type: 'bool' }, { name: 'pauseTransfers', type: 'bool' }, { name: 'allowOwnerMinting', type: 'bool' }, { name: 'allowTerminalMigration', type: 'bool' }, { name: 'allowSetTerminals', type: 'bool' }, { name: 'allowSetController', type: 'bool' }, { name: 'allowAddAccountingContexts', type: 'bool' }, { name: 'allowAddPriceFeed', type: 'bool' }, { name: 'ownerMustSendPayouts', type: 'bool' }, { name: 'holdFees', type: 'bool' }, { name: 'useTotalSurplusForCashOuts', type: 'bool' }, { name: 'useDataHookForPay', type: 'bool' }, { name: 'useDataHookForCashOut', type: 'bool' }, { name: 'dataHook', type: 'address' }, { name: 'metadata', type: 'uint256' }] }] }] }
    ];

    let allRulesets = [];
    let currentRulesetId = null;

    // Expose functions globally
    window.loadTimeline = loadTimeline;
    window.toggleDetails = toggleDetails;
    window.compareRulesets = compareRulesets;
    window.closeCompare = closeCompare;

    async function loadTimeline() {
      const projectId = document.getElementById('projectId').value;
      const chainId = parseInt(document.getElementById('chainSelect').value);

      if (!projectId) { alert('Please enter a project ID'); return; }

      const container = document.getElementById('timelineContainer');
      container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading ruleset history...</div>';

      try {
        const config = await loadChainConfig();
        const chainConfig = config.chains[chainId];
        const chain = CHAIN_CONFIGS[chainId];

        const client = createPublicClient({ chain, transport: http(chainConfig.rpc) });
        const controllerAddress = chainConfig.contracts.JBController;

        const controller = getContract({ address: controllerAddress, abi: CONTROLLER_ABI, client });

        // Load project name
        document.getElementById('projectName').textContent = `Project ${projectId}`;
        document.getElementById('projectIdDisplay').textContent = `ID: ${projectId} on ${chainConfig.name}`;
        document.getElementById('projectHeader').classList.add('visible');

        // Load current ruleset
        const [currentRuleset, currentMetadata] = await controller.read.currentRulesetOf([BigInt(projectId)]);
        currentRulesetId = currentRuleset.id.toString();

        // Load upcoming and queued rulesets
        let upcomingRuleset = null, queuedRuleset = null;
        try {
          const [upcoming, upcomingMeta] = await controller.read.upcomingRulesetOf([BigInt(projectId)]);
          if (upcoming.id.toString() !== currentRulesetId) {
            upcomingRuleset = { ruleset: upcoming, metadata: upcomingMeta, status: 'upcoming' };
          }
        } catch (e) {}

        try {
          const [queued, queuedMeta, approvalStatus] = await controller.read.latestQueuedRulesetOf([BigInt(projectId)]);
          const queuedId = queued.id.toString();
          if (queuedId !== currentRulesetId && (!upcomingRuleset || queuedId !== upcomingRuleset.ruleset.id.toString())) {
            queuedRuleset = { ruleset: queued, metadata: queuedMeta, approvalStatus, status: 'pending' };
          }
        } catch (e) {}

        // Load historical rulesets
        const historicalRulesets = await controller.read.allRulesetsOf([BigInt(projectId), 0n, 50n]);

        // Combine and sort
        allRulesets = [];
        if (queuedRuleset) allRulesets.push(queuedRuleset);
        if (upcomingRuleset) allRulesets.push(upcomingRuleset);
        allRulesets.push({ ruleset: currentRuleset, metadata: currentMetadata, status: 'current' });

        for (const rs of historicalRulesets) {
          if (rs.ruleset.id.toString() !== currentRulesetId) {
            if (!allRulesets.find(r => r.ruleset.id.toString() === rs.ruleset.id.toString())) {
              allRulesets.push({ ...rs, status: 'past' });
            }
          }
        }

        allRulesets.sort((a, b) => Number(b.ruleset.start) - Number(a.ruleset.start));
        renderTimeline();
        document.getElementById('legend').style.display = 'flex';

      } catch (error) {
        console.error(error);
        container.innerHTML = `<div class="empty">Error loading rulesets: ${error.message}</div>`;
      }
    }

    function renderTimeline() {
      const container = document.getElementById('timelineContainer');
      if (allRulesets.length === 0) {
        container.innerHTML = '<div class="empty">No rulesets found for this project</div>';
        return;
      }

      let html = '<div class="timeline-container"><div class="timeline-line"></div>';

      allRulesets.forEach((rs, index) => {
        const { ruleset, metadata, status, approvalStatus } = rs;
        const startDate = new Date(Number(ruleset.start) * 1000);
        const endDate = ruleset.duration > 0n ? new Date((Number(ruleset.start) + Number(ruleset.duration)) * 1000) : null;
        const statusLabel = status === 'pending' ? getApprovalStatusLabel(approvalStatus) : status;

        html += `
          <div class="card ruleset-card ${status}">
            <div class="timeline-dot"></div>
            <div class="ruleset-header">
              <div>
                <div class="ruleset-title">Ruleset #${ruleset.cycleNumber.toString()}
                  ${index < allRulesets.length - 1 ? `<button class="compare-btn" onclick="compareRulesets(${index}, ${index + 1})">Compare with previous</button>` : ''}
                </div>
              </div>
              <span class="ruleset-status ${status}">${statusLabel}</span>
            </div>
            <div class="ruleset-dates">
              <span>Start: ${startDate.toLocaleString()}</span>
              ${endDate ? `<span>End: ${endDate.toLocaleString()}</span>` : '<span>Duration: Indefinite</span>'}
              ${ruleset.duration > 0n ? `<span>Cycle: ${formatDuration(Number(ruleset.duration))}</span>` : ''}
            </div>
            <div class="params-grid">
              <div class="param-item"><div class="param-label">Weight</div><div class="param-value">${formatWeight(ruleset.weight)}</div></div>
              <div class="param-item"><div class="param-label">Weight Cut %</div><div class="param-value">${(Number(ruleset.weightCutPercent) / 10000000).toFixed(2)}%</div></div>
              <div class="param-item"><div class="param-label">Reserved Rate</div><div class="param-value">${(Number(metadata.reservedRate) / 100).toFixed(2)}%</div></div>
              <div class="param-item"><div class="param-label">Cash Out Tax</div><div class="param-value">${(Number(metadata.cashOutTaxRate) / 100).toFixed(2)}%</div></div>
            </div>
            <button class="expand-btn" onclick="toggleDetails(${index})">Show more details</button>
            <div class="expanded-details" id="details-${index}">
              <div class="params-grid">
                <div class="param-item"><div class="param-label">Pause Pay</div><div class="param-value">${metadata.pausePay ? 'Yes' : 'No'}</div></div>
                <div class="param-item"><div class="param-label">Pause Cash Out</div><div class="param-value">${metadata.pauseCashOut ? 'Yes' : 'No'}</div></div>
                <div class="param-item"><div class="param-label">Owner Minting</div><div class="param-value">${metadata.allowOwnerMinting ? 'Allowed' : 'Disabled'}</div></div>
                <div class="param-item"><div class="param-label">Terminal Migration</div><div class="param-value">${metadata.allowTerminalMigration ? 'Allowed' : 'Disabled'}</div></div>
                <div class="param-item"><div class="param-label">Set Terminals</div><div class="param-value">${metadata.allowSetTerminals ? 'Allowed' : 'Disabled'}</div></div>
                <div class="param-item"><div class="param-label">Set Controller</div><div class="param-value">${metadata.allowSetController ? 'Allowed' : 'Disabled'}</div></div>
                <div class="param-item"><div class="param-label">Hold Fees</div><div class="param-value">${metadata.holdFees ? 'Yes' : 'No'}</div></div>
                <div class="param-item"><div class="param-label">Data Hook (Pay)</div><div class="param-value">${metadata.useDataHookForPay ? 'Enabled' : 'Disabled'}</div></div>
                <div class="param-item"><div class="param-label">Data Hook (Cash Out)</div><div class="param-value">${metadata.useDataHookForCashOut ? 'Enabled' : 'Disabled'}</div></div>
                ${metadata.dataHook !== zeroAddress ? `<div class="param-item"><div class="param-label">Data Hook</div><div class="param-value mono" style="font-size: 11px;">${metadata.dataHook}</div></div>` : ''}
                ${ruleset.approvalHook !== zeroAddress ? `<div class="param-item"><div class="param-label">Approval Hook</div><div class="param-value mono" style="font-size: 11px;">${ruleset.approvalHook}</div></div>` : ''}
              </div>
            </div>
          </div>`;
      });

      html += '</div>';
      container.innerHTML = html;
    }

    function toggleDetails(index) {
      const details = document.getElementById(`details-${index}`);
      details.classList.toggle('visible');
      const btn = details.previousElementSibling;
      btn.textContent = details.classList.contains('visible') ? 'Hide details' : 'Show more details';
    }

    function compareRulesets(index1, index2) {
      const rs1 = allRulesets[index1], rs2 = allRulesets[index2];
      const fields = [
        { key: 'weight', label: 'Weight', format: formatWeight },
        { key: 'weightCutPercent', label: 'Weight Cut %', format: v => (Number(v) / 10000000).toFixed(2) + '%' },
        { key: 'duration', label: 'Duration', format: v => Number(v) === 0 ? 'Indefinite' : formatDuration(Number(v)) },
        { key: 'reservedRate', label: 'Reserved Rate', format: v => (Number(v) / 100).toFixed(2) + '%', metadata: true },
        { key: 'cashOutTaxRate', label: 'Cash Out Tax', format: v => (Number(v) / 100).toFixed(2) + '%', metadata: true },
        { key: 'pausePay', label: 'Pause Pay', format: v => v ? 'Yes' : 'No', metadata: true },
        { key: 'pauseCashOut', label: 'Pause Cash Out', format: v => v ? 'Yes' : 'No', metadata: true },
        { key: 'allowOwnerMinting', label: 'Owner Minting', format: v => v ? 'Allowed' : 'Disabled', metadata: true },
      ];

      let html = `<table class="compare-table"><thead><tr><th>Parameter</th><th>Ruleset #${rs1.ruleset.cycleNumber.toString()}</th><th>Ruleset #${rs2.ruleset.cycleNumber.toString()}</th></tr></thead><tbody>`;

      fields.forEach(field => {
        const val1 = field.metadata ? rs1.metadata[field.key] : rs1.ruleset[field.key];
        const val2 = field.metadata ? rs2.metadata[field.key] : rs2.ruleset[field.key];
        const f1 = field.format(val1), f2 = field.format(val2);
        html += `<tr><td>${field.label}</td><td class="${f1 !== f2 ? 'changed' : ''}">${f1}</td><td>${f2}</td></tr>`;
      });

      html += '</tbody></table>';
      document.getElementById('compareBody').innerHTML = html;
      document.getElementById('compareModal').classList.add('visible');
    }

    function closeCompare() { document.getElementById('compareModal').classList.remove('visible'); }

    function formatWeight(weight) {
      const tokens = Number(weight) / 1e18;
      if (tokens >= 1000000) return (tokens / 1000000).toFixed(2) + 'M';
      if (tokens >= 1000) return (tokens / 1000).toFixed(2) + 'K';
      return tokens.toFixed(4);
    }

    function formatDuration(seconds) {
      if (seconds < 3600) return Math.round(seconds / 60) + ' minutes';
      if (seconds < 86400) return Math.round(seconds / 3600) + ' hours';
      if (seconds < 604800) return Math.round(seconds / 86400) + ' days';
      return Math.round(seconds / 604800) + ' weeks';
    }

    function getApprovalStatusLabel(status) {
      const labels = { 0: 'Empty', 1: 'Upcoming', 2: 'Active', 3: 'ApprovalExpected', 4: 'Approved', 5: 'Failed' };
      return labels[Number(status)] || 'pending';
    }

    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeCompare(); });
    document.getElementById('compareModal').addEventListener('click', (e) => { if (e.target.id === 'compareModal') closeCompare(); });
  </script>
</body>
</html>
```

## Key Features

### Timeline Visualization
- Vertical timeline with visual indicators
- Color-coded status (current, upcoming, past)
- Chronological ordering

### Ruleset Comparison
- Side-by-side parameter comparison
- Highlights changed values
- Compare any two rulesets

### Detailed Information
- Expandable details for each ruleset
- All metadata fields displayed
- Approval hook status

## Data Sources

The timeline uses on-chain data via:
- `currentRulesetOf()` - Active ruleset
- `upcomingRulesetOf()` - Next ruleset
- `latestQueuedRulesetOf()` - Queued with approval status
- `allRulesetsOf()` - Historical rulesets

## Related Skills

- `/jb-explorer-ui` - Contract read/write interface
- `/jb-event-explorer-ui` - Event history
- `/jb-query` - Query project data via CLI
