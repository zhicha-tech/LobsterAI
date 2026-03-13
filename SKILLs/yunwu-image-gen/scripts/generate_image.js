const fs = require('fs');
const path = require('path');
const os = require('os');


const config = JSON.parse(fs.readFileSync(path.join(os.homedir(), ".lawclaw.json")))
const apiKey = config?.cloudPlatform?.yunwu?.apiKey

// Yunwu AI API configuration
const YUNWU_CONFIG = {
    baseUrl: 'https://yunwu.ai/',
    endpoint: 'v1beta/models/gemini-3-pro-image-preview:generateContent',
    apiKey: apiKey
};

// Supported aspect ratios
const ASPECT_RATIOS = {
    '1:1': '1:1',
    '16:9': '16:9',
    '9:16': '9:16',
    '4:3': '4:3',
    '3:4': '3:4',
    '2.35:1': '16:9',  // Mapping to closest supported ratio
    '21:9': '16:9'
};

// Supported image sizes
const IMAGE_SIZES = ['1K', '2K', '4K'];

/**
 * Generate image using Yunwu AI API (Gemini)
 * @param {string} prompt - Image generation prompt
 * @param {Object} options - Generation options
 * @param {string} options.outputPath - Path to save the generated image
 * @param {string} options.aspectRatio - Aspect ratio (1:1, 16:9, 9:16, 4:3, 3:4)
 * @param {string} options.imageSize - Image size (1K, 2K, 4K)
 * @param {string[]} options.responseModalities - Response modalities (default: ["TEXT", "IMAGE"])
 * @returns {Promise<string>} Path to the generated image
 */
async function generateImage(prompt, options = {}) {
    const {
        outputPath,
        aspectRatio = '9:16',
        imageSize = '1K',
        responseModalities = ['TEXT', 'IMAGE']
    } = options;

    if (!YUNWU_CONFIG.apiKey) {
        throw new Error('YUNWU_API_KEY environment variable is not set');
    }

    if (!prompt || typeof prompt !== 'string') {
        throw new Error('Prompt is required and must be a string');
    }

    // Validate aspect ratio
    const validAspectRatio = ASPECT_RATIOS[aspectRatio] || '9:16';

    // Validate image size
    const validImageSize = IMAGE_SIZES.includes(imageSize) ? imageSize : '1K';

    try {
        const endpoint = `${YUNWU_CONFIG.baseUrl}${YUNWU_CONFIG.endpoint}`;

        const requestBody = {
            contents: [{
                parts: [{ text: prompt }]
            }],
            responseModalities: responseModalities,
            imageConfig: {
                aspectRatio: validAspectRatio,
                imageSize: validImageSize
            }
        };

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${YUNWU_CONFIG.apiKey}`
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API request failed: ${response.status} - ${errorText}`);
        }

        const result = await response.json();

        if (!result.candidates || result.candidates.length === 0) {
            throw new Error('No image generated from API');
        }

        // Extract image data from response - check all parts for inlineData
        const parts = result.candidates[0]?.content?.parts || [];
        const imagePart = parts.find(part => part.inlineData && part.inlineData.data);

        if (!imagePart) {
            throw new Error('No image data found in API response');
        }

        const imageData = imagePart.inlineData.data;

        // Save image
        // 如果没有提供输出路径，使用临时目录创建绝对路径
        let filePath = outputPath;
        if (!filePath) {
            const tmpDir = os.tmpdir();
            filePath = path.join(tmpDir, `yunwu-image-${Date.now()}.png`);
        }
        // 确保返回绝对路径
        if (!path.isAbsolute(filePath)) {
            filePath = path.resolve(filePath);
        }
        const buffer = Buffer.from(imageData, 'base64');
        fs.writeFileSync(filePath, buffer);

        // 返回 file:/// 协议格式的 URL
        const normalizedPath = filePath.replace(/\\/g, '/');
        if (/^[A-Za-z]:/.test(normalizedPath)) {
            // Windows 路径: C:/... -> file:///C:/...
            return `file:///${normalizedPath}`;
        } else if (normalizedPath.startsWith('/')) {
            // Unix 路径: /Users/... -> file:///Users/...
            return `file://${normalizedPath}`;
        }
        return `file://${normalizedPath}`;
    } catch (error) {
        throw new Error(`Failed to generate image: ${error.message}`);
    }
}

/**
 * Map cover ratio to API aspect ratio
 * @param {string} ratio - Cover ratio (e.g., '2.35:1', '16:9', '1:1')
 * @returns {string} API supported aspect ratio
 */
function mapCoverRatioToAspectRatio(ratio) {
    const ratioMap = {
        '2.35:1': '16:9',
        '21:9': '16:9',
        '16:9': '16:9',
        '9:16': '9:16',
        '4:3': '4:3',
        '3:4': '3:4',
        '1:1': '1:1'
    };
    return ratioMap[ratio] || '16:9';
}

/**
 * Generate cover image prompt from title
 * @param {string} title - Article title
 * @param {Object} options - Additional options
 * @param {string} options.style - Image style (default: 'modern')
 * @param {string} options.ratio - Image ratio (default: '2.35:1')
 * @returns {string} Cover image prompt
 */
function generateCoverPrompt(title, options = {}) {
    const { style = 'modern', ratio = '2.35:1' } = options;

    return `请生成一张爆款公众号封面图。
要求：
1. 比例 ${ratio}（横版封面）
2. 视觉冲击力强，吸引点击
3. 标题文字清晰醒目，放在画面中央
4. 配色鲜明，符合文章主题
5. 背景简洁不杂乱
6. 风格：${style}

文章标题：${title}`;
}

/**
 * Generate cover image for article
 * @param {string} title - Article title
 * @param {Object} options - Generation options
 * @param {string} options.outputPath - Path to save the generated image
 * @param {string} options.style - Image style
 * @param {string} options.ratio - Image ratio (e.g., '2.35:1', '16:9', '1:1')
 * @param {string} options.imageSize - Image size (1K, 2K, 4K)
 * @returns {Promise<string>} Path to the generated cover image
 */
async function generateCoverImage(title, options = {}) {
    const { outputPath, style, ratio = '2.35:1', imageSize = '2K' } = options;
    const prompt = generateCoverPrompt(title, { style, ratio });

    // Map cover ratio to API aspect ratio
    const aspectRatio = mapCoverRatioToAspectRatio(ratio);

    return await generateImage(prompt, {
        outputPath,
        aspectRatio,
        imageSize
    });
}

/**
 * Extract title from markdown content
 * @param {string} markdown - Markdown content
 * @returns {string} Extracted title
 */
function extractTitleFromMarkdown(markdown) {
    // Try YAML frontmatter first
    const frontmatterMatch = markdown.match(/^---\s*\ntitle:\s*(.+?)\s*\n---/s);
    if (frontmatterMatch) {
        return frontmatterMatch[1].trim().replace(/^['"]|['"]$/g, '');
    }

    // Try to find first # heading
    const headingMatch = markdown.match(/^#\s+(.+)$/m);
    if (headingMatch) {
        return headingMatch[1].trim();
    }

    // Try first line if no heading found
    const firstLine = markdown.split('\n')[0].trim();
    if (firstLine && !firstLine.startsWith('#')) {
        return firstLine;
    }

    return '未命名文章';
}

/**
 * Generate cover image from markdown content
 * @param {string} markdown - Article markdown content
 * @param {Object} options - Generation options
 * @param {string} options.outputPath - Path to save the generated image
 * @param {string} options.style - Image style
 * @param {string} options.ratio - Image ratio
 * @param {string} options.imageSize - Image size (1K, 2K, 4K)
 * @returns {Promise<string>} Path to the generated cover image
 */
async function generateCoverFromMarkdown(markdown, options = {}) {
    const title = extractTitleFromMarkdown(markdown);
    return await generateCoverImage(title, options);
}

/**
 * Get supported aspect ratios
 * @returns {string[]} List of supported aspect ratios
 */
function getSupportedAspectRatios() {
    return Object.keys(ASPECT_RATIOS);
}

/**
 * Get supported image sizes
 * @returns {string[]} List of supported image sizes
 */
function getSupportedImageSizes() {
    return [...IMAGE_SIZES];
}

module.exports = {
    generateImage,
    generateCoverImage,
    generateCoverFromMarkdown,
    generateCoverPrompt,
    extractTitleFromMarkdown,
    mapCoverRatioToAspectRatio,
    getSupportedAspectRatios,
    getSupportedImageSizes,
    YUNWU_CONFIG
};

// CLI usage
if (require.main === module) {
    const args = process.argv.slice(2);
    const command = args[0];

    if (command === 'generate' && args[1]) {
        const options = {
            outputPath: args[2],
            aspectRatio: args[3] || '9:16',
            imageSize: args[4] || '1K'
        };
        generateImage(args[1], options)
            .then(path => {
                console.log(`Image generated: ${path}`);
                process.exit(0);
            })
            .catch(err => {
                console.error(err.message);
                process.exit(1);
            });
    } else if (command === 'cover' && args[1]) {
        const options = {
            outputPath: args[2],
            ratio: args[3] || '2.35:1',
            imageSize: args[4] || '2K'
        };
        generateCoverImage(args[1], options)
            .then(path => {
                console.log(`Cover image generated: ${path}`);
                process.exit(0);
            })
            .catch(err => {
                console.error(err.message);
                process.exit(1);
            });
    } else if (command === 'ratios') {
        console.log('Supported aspect ratios:');
        console.log(getSupportedAspectRatios().join(', '));
        process.exit(0);
    } else if (command === 'sizes') {
        console.log('Supported image sizes:');
        console.log(getSupportedImageSizes().join(', '));
        process.exit(0);
    } else {
        console.log(`
Usage:
  node generate_image.js generate "prompt" [outputPath] [aspectRatio] [imageSize]
  node generate_image.js cover "title" [outputPath] [ratio] [imageSize]
  node generate_image.js ratios
  node generate_image.js sizes

Options:
  aspectRatio: 1:1, 16:9, 9:16, 4:3, 3:4 (default: 9:16)
  ratio: 2.35:1, 16:9, 9:16, 4:3, 3:4, 1:1 (default: 2.35:1)
  imageSize: 1K, 2K, 4K (default: 1K for generate, 2K for cover)

Environment:
  YUNWU_API_KEY - Required API key for Yunwu AI
        `);
        process.exit(1);
    }
}
