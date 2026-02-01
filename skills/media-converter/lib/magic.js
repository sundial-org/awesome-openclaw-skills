const fs = require('fs');

/**
 * Detects MIME type from file magic bytes
 * @param {string} filePath 
 * @returns {string|null} Detected MIME type or null
 */
function detectMime(filePath) {
    const buffer = Buffer.alloc(12); // Read first 12 bytes
    const fd = fs.openSync(filePath, 'r');
    fs.readSync(fd, buffer, 0, 12, 0);
    fs.closeSync(fd);

    const hex = buffer.toString('hex').toUpperCase();

    // JPEG
    if (hex.startsWith('FFD8FF')) return 'image/jpeg';
    
    // PNG
    if (hex.startsWith('89504E470D0A1A0A')) return 'image/png';
    
    // GIF
    if (hex.startsWith('47494638')) return 'image/gif'; // GIF87a or GIF89a
    
    // WEBP (RIFF....WEBP)
    if (hex.startsWith('52494646') && hex.slice(16, 24) === '57454250') return 'image/webp';
    
    // MP4 (ftypisom, ftypmp42, etc - usually starts at offset 4)
    // Common signature: ....ftyp
    const sub = buffer.subarray(4, 8).toString('ascii');
    if (sub === 'ftyp') return 'video/mp4';

    return null; // Unknown
}

module.exports = { detectMime };
