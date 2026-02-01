#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
if (args.length < 2) {
  console.error('Usage: generate-from-template.js <symbol-name> <svg-path> [template-svg] [assets-dir]');
  process.exit(1);
}

const symbolName = args[0];
const svgPath = args[1];
const assetsDir = args[3] || process.env.SFSYMBOL_ASSETS_DIR || 'Assets.xcassets/Symbols';
const skillTemplatePath = path.resolve(__dirname, '../assets/template.svg');

const findTemplateSvg = (symbolsDir) => {
  if (!fs.existsSync(symbolsDir)) {
    return null;
  }
  const entries = fs.readdirSync(symbolsDir, { withFileTypes: true });
  for (const entry of entries) {
    if (!entry.isDirectory() || !entry.name.endsWith('.symbolset')) {
      continue;
    }
    const symbolsetPath = path.join(symbolsDir, entry.name);
    const files = fs.readdirSync(symbolsetPath);
    const svgFile = files.find((file) => file.endsWith('.svg'));
    if (svgFile) {
      return path.join(symbolsetPath, svgFile);
    }
  }
  return null;
};

const templateSvgPath = args[2] || findTemplateSvg(assetsDir) || (fs.existsSync(skillTemplatePath) ? skillTemplatePath : null);

if (!fs.existsSync(svgPath)) {
  console.error(`SVG not found: ${svgPath}`);
  process.exit(1);
}

if (!templateSvgPath || !fs.existsSync(templateSvgPath)) {
  console.error('Template SVG not found. Pass a template SVG path, set SFSYMBOL_ASSETS_DIR, or ensure a .symbolset SVG exists in Assets.xcassets/Symbols.');
  process.exit(1);
}

const sourceSvg = fs.readFileSync(svgPath, 'utf8');
const templateSvg = fs.readFileSync(templateSvgPath, 'utf8');

const defaultFillRuleMatch = sourceSvg.match(/fill-rule:\s*([a-zA-Z]+)/) || sourceSvg.match(/fill-rule="([^"]+)"/);
const defaultClipRuleMatch = sourceSvg.match(/clip-rule:\s*([a-zA-Z]+)/) || sourceSvg.match(/clip-rule="([^"]+)"/);
const defaultFillRule = defaultFillRuleMatch ? defaultFillRuleMatch[1] : null;
const defaultClipRule = defaultClipRuleMatch ? defaultClipRuleMatch[1] : null;

const viewBoxMatch = sourceSvg.match(/viewBox="([^"]+)"/);
if (!viewBoxMatch) {
  console.error('Source SVG must include a viewBox.');
  process.exit(1);
}

const viewBoxParts = viewBoxMatch[1].trim().split(/\s+/).map(Number);
if (viewBoxParts.length !== 4 || viewBoxParts.some((value) => Number.isNaN(value))) {
  console.error(`Invalid viewBox: ${viewBoxMatch[1]}`);
  process.exit(1);
}

const [minX, minY, viewWidth, viewHeight] = viewBoxParts;
const targetSize = 110;

const pathRegex = /<path[^>]*>/g;
const rectRegex = /<rect[^>]*>/g;
const paths = [];
let match = null;

const getAttr = (tag, name) => {
  const attr = tag.match(new RegExp(`${name}="([^"]+)"`));
  return attr ? attr[1] : null;
};

while ((match = pathRegex.exec(sourceSvg)) !== null) {
  const pathTag = match[0];
  const dMatch = getAttr(pathTag, 'd');
  if (!dMatch) {
    continue;
  }
  const fillRuleMatch = getAttr(pathTag, 'fill-rule') || defaultFillRule;
  const clipRuleMatch = getAttr(pathTag, 'clip-rule') || defaultClipRule;
  paths.push({
    d: dMatch,
    fillRule: fillRuleMatch,
    clipRule: clipRuleMatch
  });
}

while ((match = rectRegex.exec(sourceSvg)) !== null) {
  const rectTag = match[0];
  const xValue = parseFloat(getAttr(rectTag, 'x') ?? '0');
  const yValue = parseFloat(getAttr(rectTag, 'y') ?? '0');
  const widthValue = parseFloat(getAttr(rectTag, 'width') ?? '0');
  const heightValue = parseFloat(getAttr(rectTag, 'height') ?? '0');
  if (!Number.isFinite(widthValue) || !Number.isFinite(heightValue) || widthValue <= 0 || heightValue <= 0) {
    continue;
  }
  const fillRuleMatch = getAttr(rectTag, 'fill-rule') || defaultFillRule;
  const clipRuleMatch = getAttr(rectTag, 'clip-rule') || defaultClipRule;
  const x2 = xValue + widthValue;
  const y2 = yValue + heightValue;
  const d = `M${xValue} ${yValue}H${x2}V${y2}H${xValue}Z`;
  paths.push({
    d,
    fillRule: fillRuleMatch,
    clipRule: clipRuleMatch
  });
}

if (paths.length === 0) {
  console.error('No <path> or <rect> elements found in source SVG.');
  process.exit(1);
}

const parseNumbers = (tokens, count) => {
  const values = [];
  for (let index = 0; index < count; index += 1) {
    const value = tokens.shift();
    if (value === undefined) {
      break;
    }
    values.push(parseFloat(value));
  }
  return values;
};

const updateBounds = (bounds, x, y) => {
  bounds.minX = Math.min(bounds.minX, x);
  bounds.maxX = Math.max(bounds.maxX, x);
  bounds.minY = Math.min(bounds.minY, y);
  bounds.maxY = Math.max(bounds.maxY, y);
};

const computePathBounds = (d) => {
  const tokens = d.match(/[a-zA-Z]|-?\d*\.?\d+(?:e[-+]?\d+)?/g);
  if (!tokens) {
    return null;
  }
  const bounds = {
    minX: Number.POSITIVE_INFINITY,
    maxX: Number.NEGATIVE_INFINITY,
    minY: Number.POSITIVE_INFINITY,
    maxY: Number.NEGATIVE_INFINITY
  };
  let currentX = 0;
  let currentY = 0;
  let startX = 0;
  let startY = 0;
  let command = null;

  while (tokens.length > 0) {
    const token = tokens.shift();
    if (!token) {
      continue;
    }
    if (/[a-zA-Z]/.test(token)) {
      command = token;
    } else if (command) {
      tokens.unshift(token);
    } else {
      continue;
    }

    const isRelative = command === command.toLowerCase();
    switch (command) {
      case 'M':
      case 'm': {
        const points = parseNumbers(tokens, 2);
        if (points.length < 2) {
          break;
        }
        const [x, y] = points;
        currentX = isRelative ? currentX + x : x;
        currentY = isRelative ? currentY + y : y;
        startX = currentX;
        startY = currentY;
        updateBounds(bounds, currentX, currentY);
        while (tokens.length >= 2 && !/[a-zA-Z]/.test(tokens[0])) {
          const line = parseNumbers(tokens, 2);
          if (line.length < 2) {
            break;
          }
          const [lx, ly] = line;
          currentX = isRelative ? currentX + lx : lx;
          currentY = isRelative ? currentY + ly : ly;
          updateBounds(bounds, currentX, currentY);
        }
        break;
      }
      case 'L':
      case 'l': {
        while (tokens.length >= 2 && !/[a-zA-Z]/.test(tokens[0])) {
          const line = parseNumbers(tokens, 2);
          if (line.length < 2) {
            break;
          }
          const [x, y] = line;
          currentX = isRelative ? currentX + x : x;
          currentY = isRelative ? currentY + y : y;
          updateBounds(bounds, currentX, currentY);
        }
        break;
      }
      case 'H':
      case 'h': {
        while (tokens.length > 0 && !/[a-zA-Z]/.test(tokens[0])) {
          const [x] = parseNumbers(tokens, 1);
          if (x === undefined) {
            break;
          }
          currentX = isRelative ? currentX + x : x;
          updateBounds(bounds, currentX, currentY);
        }
        break;
      }
      case 'V':
      case 'v': {
        while (tokens.length > 0 && !/[a-zA-Z]/.test(tokens[0])) {
          const [y] = parseNumbers(tokens, 1);
          if (y === undefined) {
            break;
          }
          currentY = isRelative ? currentY + y : y;
          updateBounds(bounds, currentX, currentY);
        }
        break;
      }
      case 'C':
      case 'c': {
        while (tokens.length >= 6 && !/[a-zA-Z]/.test(tokens[0])) {
          const [x1, y1, x2, y2, x, y] = parseNumbers(tokens, 6);
          if ([x1, y1, x2, y2, x, y].some((value) => value === undefined)) {
            break;
          }
          const control1X = isRelative ? currentX + x1 : x1;
          const control1Y = isRelative ? currentY + y1 : y1;
          const control2X = isRelative ? currentX + x2 : x2;
          const control2Y = isRelative ? currentY + y2 : y2;
          currentX = isRelative ? currentX + x : x;
          currentY = isRelative ? currentY + y : y;
          updateBounds(bounds, control1X, control1Y);
          updateBounds(bounds, control2X, control2Y);
          updateBounds(bounds, currentX, currentY);
        }
        break;
      }
      case 'S':
      case 's': {
        while (tokens.length >= 4 && !/[a-zA-Z]/.test(tokens[0])) {
          const [x2, y2, x, y] = parseNumbers(tokens, 4);
          if ([x2, y2, x, y].some((value) => value === undefined)) {
            break;
          }
          const control2X = isRelative ? currentX + x2 : x2;
          const control2Y = isRelative ? currentY + y2 : y2;
          currentX = isRelative ? currentX + x : x;
          currentY = isRelative ? currentY + y : y;
          updateBounds(bounds, control2X, control2Y);
          updateBounds(bounds, currentX, currentY);
        }
        break;
      }
      case 'Q':
      case 'q': {
        while (tokens.length >= 4 && !/[a-zA-Z]/.test(tokens[0])) {
          const [x1, y1, x, y] = parseNumbers(tokens, 4);
          if ([x1, y1, x, y].some((value) => value === undefined)) {
            break;
          }
          const controlX = isRelative ? currentX + x1 : x1;
          const controlY = isRelative ? currentY + y1 : y1;
          currentX = isRelative ? currentX + x : x;
          currentY = isRelative ? currentY + y : y;
          updateBounds(bounds, controlX, controlY);
          updateBounds(bounds, currentX, currentY);
        }
        break;
      }
      case 'T':
      case 't': {
        while (tokens.length >= 2 && !/[a-zA-Z]/.test(tokens[0])) {
          const [x, y] = parseNumbers(tokens, 2);
          if ([x, y].some((value) => value === undefined)) {
            break;
          }
          currentX = isRelative ? currentX + x : x;
          currentY = isRelative ? currentY + y : y;
          updateBounds(bounds, currentX, currentY);
        }
        break;
      }
      case 'A':
      case 'a': {
        while (tokens.length >= 7 && !/[a-zA-Z]/.test(tokens[0])) {
          const values = parseNumbers(tokens, 7);
          if (values.length < 7) {
            break;
          }
          const [rx, ry, xAxisRotation, largeArcFlag, sweepFlag, x, y] = values;
          if ([rx, ry, xAxisRotation, largeArcFlag, sweepFlag, x, y].some((value) => value === undefined)) {
            break;
          }
          currentX = isRelative ? currentX + x : x;
          currentY = isRelative ? currentY + y : y;
          updateBounds(bounds, currentX, currentY);
        }
        break;
      }
      case 'Z':
      case 'z': {
        currentX = startX;
        currentY = startY;
        updateBounds(bounds, currentX, currentY);
        break;
      }
      default:
        break;
    }
  }

  if (!Number.isFinite(bounds.minX)) {
    return null;
  }

  return bounds;
};

const combinedBounds = paths.reduce((result, pathEntry) => {
  const pathBounds = computePathBounds(pathEntry.d);
  if (!pathBounds) {
    return result;
  }
  if (!result) {
    return { ...pathBounds };
  }
  return {
    minX: Math.min(result.minX, pathBounds.minX),
    maxX: Math.max(result.maxX, pathBounds.maxX),
    minY: Math.min(result.minY, pathBounds.minY),
    maxY: Math.max(result.maxY, pathBounds.maxY)
  };
}, null);

const fallbackSize = Math.max(viewWidth, viewHeight);

const boundsToUse = combinedBounds || {
  minX,
  maxX: minX + viewWidth,
  minY,
  maxY: minY + viewHeight
};

const centerX = (boundsToUse.minX + boundsToUse.maxX) / 2;
const centerY = (boundsToUse.minY + boundsToUse.maxY) / 2;
const boundsWidth = boundsToUse.maxX - boundsToUse.minX;
const boundsHeight = boundsToUse.maxY - boundsToUse.minY;
const scale = targetSize / Math.max(boundsWidth || fallbackSize, boundsHeight || fallbackSize);

const matchNumber = (regex, label) => {
  const result = templateSvg.match(regex);
  if (!result) {
    return null;
  }
  const value = parseFloat(result[1]);
  if (Number.isNaN(value)) {
    console.warn(`Invalid ${label} value: ${result[1]}`);
    return null;
  }
  return value;
};

const leftMarginX = matchNumber(/id="left-margin-Regular-S"[^>]*x1="([^"]+)"/, 'left-margin-Regular-S');
const rightMarginX = matchNumber(/id="right-margin-Regular-S"[^>]*x1="([^"]+)"/, 'right-margin-Regular-S');
const baselineY = matchNumber(/id="Baseline-S"[^>]*y1="([^"]+)"/, 'Baseline-S');
const caplineY = matchNumber(/id="Capline-S"[^>]*y1="([^"]+)"/, 'Capline-S');

const transformMatch = templateSvg.match(/id="Regular-S"[^>]*transform="matrix\([^)]*\)"/);
let groupTranslateX = 0;
let groupTranslateY = 0;
if (transformMatch) {
  const numbers = transformMatch[0].match(/-?\d*\.?\d+/g)?.map(Number) ?? [];
  if (numbers.length >= 6) {
    groupTranslateX = numbers[4];
    groupTranslateY = numbers[5];
  }
}

const targetCenterX = leftMarginX !== null && rightMarginX !== null
  ? (leftMarginX + rightMarginX) / 2 - groupTranslateX
  : 0;
const targetCenterY = baselineY !== null && caplineY !== null
  ? (baselineY + caplineY) / 2 - groupTranslateY
  : 0;

const className = 'monochrome-0 multicolor-0:tintColor hierarchical-0:primary SFSymbolsPreviewWireframe';
const scaledValue = scale.toFixed(6);
const translateX = (-centerX * scale + targetCenterX).toFixed(4);
const translateY = (-centerY * scale + targetCenterY).toFixed(4);
const transform = `matrix(${scaledValue} 0 0 ${scaledValue} ${translateX} ${translateY})`;
const pathMarkup = paths
  .map(({ d, fillRule, clipRule }) => {
    const fillRuleAttr = fillRule ? ` fill-rule="${fillRule}"` : '';
    const clipRuleAttr = clipRule ? ` clip-rule="${clipRule}"` : '';
    return `   <path class="${className}" d="${d}" transform="${transform}"${fillRuleAttr}${clipRuleAttr}/>`;
  })
  .join('\n');
const replacementContent = `\n${pathMarkup}\n`;

const replaceGroup = (svgText, groupId) => {
  const groupRegex = new RegExp(`(<g id=\"${groupId}\"[^>]*>)([\\s\\S]*?)(</g>)`);
  if (!groupRegex.test(svgText)) {
    console.error(`Template missing group: ${groupId}`);
    process.exit(1);
  }
  return svgText.replace(groupRegex, `$1${replacementContent}$3`);
};

let outputSvg = templateSvg;
outputSvg = replaceGroup(outputSvg, 'Ultralight-S');
outputSvg = replaceGroup(outputSvg, 'Regular-S');
outputSvg = replaceGroup(outputSvg, 'Black-S');
outputSvg = outputSvg.replace(/Generated from [^<]+/g, `Generated from ${symbolName}`);

const symbolsetDir = path.join(assetsDir, `${symbolName}.symbolset`);
const svgFilename = `${symbolName}.svg`;

fs.mkdirSync(symbolsetDir, { recursive: true });
fs.writeFileSync(path.join(symbolsetDir, svgFilename), outputSvg);

const contentsJson = {
  info: { author: 'xcode', version: 1 },
  symbols: [{ filename: svgFilename, idiom: 'universal' }]
};

fs.writeFileSync(path.join(symbolsetDir, 'Contents.json'), JSON.stringify(contentsJson, null, 2));
console.log(`Created: ${symbolsetDir}`);
