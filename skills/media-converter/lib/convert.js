const Jimp = require('jimp');
const path = require('path');

/**
 * Convert a GIF to a static PNG (first frame)
 * @param {string} inputPath 
 * @returns {Promise<string>} Path to the new PNG file
 */
async function gifToPng(inputPath) {
    try {
        const image = await Jimp.read(inputPath);
        
        // Construct new path
        const dir = path.dirname(inputPath);
        const name = path.basename(inputPath, path.extname(inputPath));
        const outputPath = path.join(dir, `${name}_converted.png`);
        
        await image.writeAsync(outputPath);
        return outputPath;
    } catch (error) {
        throw new Error(`Failed to convert GIF to PNG: ${error.message}`);
    }
}

module.exports = { gifToPng };
