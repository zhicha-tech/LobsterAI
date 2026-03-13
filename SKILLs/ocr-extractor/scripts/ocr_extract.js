/**
 * OCR 文本提取脚本
 * 调用 MinerU API 对文件进行 OCR 识别
 */

const https = require('https');
const fs = require('fs');
const path = require('path');
const os = require('os');

// 从用户目录的 .lawclaw.json 读取 MinerU token
function loadTokenFromLawclawJson() {
  const lawclawPath = path.join(os.homedir(), '.lawclaw.json');
  if (!fs.existsSync(lawclawPath)) {
    return null;
  }

  try {
    const content = fs.readFileSync(lawclawPath, 'utf8');
    const config = JSON.parse(content);
    // 支持两种配置路径: mineru.api_token 或 cloudPlatform.mineru.api_token
    return config?.cloudPlatform?.mineru?.api_token
      || null;
  } catch (e) {
    console.warn(`读取 .lawclaw.json 失败: ${e.message}`);
    return null;
  }
}

// 优先从 lawclaw.json 读取 token，否则从环境变量读取
const API_TOKEN = loadTokenFromLawclawJson() || process.env.YOUR_MINERU_TOKEN;
const API_BASE = 'https://mineru.net/api/v4';

/**
 * 发送 HTTP 请求
 * @param {string} url - 请求 URL
 * @param {string} method - HTTP 方法
 * @param {object} headers - 请求头
 * @param {object} data - 请求体数据
 * @returns {Promise<object>} 响应数据
 */
function makeRequest(url, method, headers, data) {
  return new Promise((resolve, reject) => {
    const postData = data ? JSON.stringify(data) : '';
    const requestHeaders = { ...headers };

    if (data) {
      requestHeaders['Content-Length'] = Buffer.byteLength(postData);
    }

    const parsedUrl = new URL(url);
    const options = {
      hostname: parsedUrl.hostname,
      port: 443,
      path: parsedUrl.pathname + parsedUrl.search,
      method: method,
      headers: requestHeaders
    };

    const req = https.request(options, (res) => {
      let responseData = '';

      res.on('data', (chunk) => {
        responseData += chunk;
      });

      res.on('end', () => {
        try {
          const parsedData = JSON.parse(responseData);
          resolve({ statusCode: res.statusCode, data: parsedData });
        } catch (e) {
          reject(new Error(`解析响应失败: ${e.message}, 原始数据: ${responseData}`));
        }
      });
    });

    req.on('error', (error) => {
      reject(new Error(`请求失败: ${error.message}`));
    });

    if (postData) {
      req.write(postData);
    }
    req.end();
  });
}

/**
 * 上传文件到 OSS
 * @param {string} uploadUrl - 上传 URL
 * @param {string} fileUrl - 源文件 URL
 * @param {Array} ossHeaders - OSS 请求头
 * @returns {Promise<void>}
 */
async function uploadFile(uploadUrl, fileUrl, ossHeaders) {
  return new Promise((resolve, reject) => {
    // 先下载文件到内存
    const parsedUrl = new URL(fileUrl);
    const options = {
      hostname: parsedUrl.hostname,
      port: 443,
      path: parsedUrl.pathname + parsedUrl.search,
      method: 'GET'
    };

    const req = https.request(options, (res) => {
      if (res.statusCode !== 200) {
        reject(new Error(`下载文件失败: HTTP ${res.statusCode}`));
        return;
      }

      const chunks = [];
      res.on('data', (chunk) => chunks.push(chunk));
      res.on('end', () => {
        const fileData = Buffer.concat(chunks);

        // 解析上传 URL
        const uploadParsed = new URL(uploadUrl);

        // 构建请求头
        const uploadHeaders = {};
        if (Array.isArray(ossHeaders)) {
          ossHeaders.forEach((h) => {
            const key = Object.keys(h)[0];
            const value = h[key];
            if (key && value !== undefined) {
              uploadHeaders[key] = value;
            }
          });
        }
        uploadHeaders['Content-Length'] = fileData.length;

        // 上传文件
        const uploadReq = https.request({
          hostname: uploadParsed.hostname,
          port: 443,
          path: uploadParsed.pathname + uploadParsed.search,
          method: 'PUT',
          headers: uploadHeaders
        }, (uploadRes) => {
          let responseData = '';
          uploadRes.on('data', (chunk) => responseData += chunk);
          uploadRes.on('end', () => {
            if (uploadRes.statusCode === 200 || uploadRes.statusCode === 201) {
              resolve();
            } else {
              reject(new Error(`上传文件失败: HTTP ${uploadRes.statusCode}, ${responseData}`));
            }
          });
        });

        uploadReq.on('error', (error) => {
          reject(new Error(`上传请求失败: ${error.message}`));
        });

        uploadReq.write(fileData);
        uploadReq.end();
      });
    });

    req.on('error', (error) => {
      reject(new Error(`下载文件失败: ${error.message}`));
    });

    req.end();
  });
}

/**
 * 下载并解压结果
 * @param {string} zipUrl - ZIP 文件 URL
 * @returns {Promise<string>} Markdown 内容
 */
async function downloadAndExtract(zipUrl) {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(zipUrl);
    const options = {
      hostname: parsedUrl.hostname,
      port: 443,
      path: parsedUrl.pathname + parsedUrl.search,
      method: 'GET'
    };

    const req = https.request(options, (res) => {
      if (res.statusCode !== 200) {
        reject(new Error(`下载结果失败: HTTP ${res.statusCode}`));
        return;
      }

      const chunks = [];
      res.on('data', (chunk) => chunks.push(chunk));
      res.on('end', () => {
        // 由于 Node.js 不内置 unzip，这里返回提示
        const zipData = Buffer.concat(chunks);
        const tempDir = path.join(__dirname, '..', 'temp');
        if (!fs.existsSync(tempDir)) {
          fs.mkdirSync(tempDir, { recursive: true });
        }

        const zipPath = path.join(tempDir, `result_${Date.now()}.zip`);
        fs.writeFileSync(zipPath, zipData);

        resolve(zipPath);
      });
    });

    req.on('error', (error) => {
      reject(new Error(`下载结果失败: ${error.message}`));
    });

    req.end();
  });
}

/**
 * 提交 OCR 任务
 * @param {string} fileUrl - 文件URL
 * @returns {Promise<object>} 结果
 */
async function processFile(fileUrl) {
  if (!API_TOKEN) {
    throw new Error('请配置 MinerU Token: 在 ~/.lawclaw.json 中设置 cloudPlatform.mineru.api_token');
  }

  const fileName = path.basename(fileUrl);
  const dataId = `convert_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;

  // 1. 申请上传地址
  console.log('正在申请上传地址...');
  const headers = {
    'Authorization': `Bearer ${API_TOKEN}`,
    'Content-Type': 'application/json'
  };

  const reqData = {
    enable_formula: true,
    language: 'ch',
    enable_table: true,
    files: [{
      name: fileName,
      is_ocr: true,
      data_id: dataId
    }]
  };

  const resp1 = await makeRequest(`${API_BASE}/file-urls/batch`, 'POST', headers, reqData);

  if (resp1.statusCode !== 200 && resp1.statusCode !== 201) {
    if (resp1.statusCode === 401 || resp1.statusCode === 403) {
      throw new Error(`Token 无效或已过期，请重新申请 Token: https://mineru.net/apiManage/token`);
    }
    throw new Error(`申请上传地址失败: HTTP ${resp1.statusCode}, ${JSON.stringify(resp1.data)}`);
  }

  const batchId = resp1.data.data?.batch_id;
  const fileUrls = resp1.data.data?.file_urls;
  const ossHeaders = resp1.data.data?.headers;
  const uploadUrl = Array.isArray(fileUrls) && fileUrls.length > 0 ? fileUrls[0] : '';

  if (!batchId || !uploadUrl) {
    throw new Error(`API 响应缺少必要字段: ${JSON.stringify(resp1.data)}`);
  }

  // 清理上传 URL
  let cleanUploadUrl = uploadUrl;
  try {
    cleanUploadUrl = JSON.parse(uploadUrl);
  } catch (e) {
    // 如果不是 JSON，直接使用
  }

  console.log(`batchId: ${batchId}`);
  console.log('正在上传文件...');

  // 2. 上传文件
  await uploadFile(cleanUploadUrl, fileUrl, ossHeaders);
  console.log('上传成功，开始处理...');

  // 3. 轮询转换结果
  const pollURL = `${API_BASE}/extract-results/batch/${batchId}`;
  const POLL_MAX = 60;
  const POLL_SLEEP = 5000;
  let pollCount = 0;
  let resultUrl = '';

  while (pollCount < POLL_MAX && !resultUrl) {
    await new Promise(resolve => setTimeout(resolve, POLL_SLEEP));
    pollCount++;

    const pollResp = await makeRequest(pollURL, 'GET', headers, null);
    const arr = pollResp.data.data?.extract_result || [];

    if (Array.isArray(arr) && arr.length > 0) {
      const doneItem = arr.find(x => x && x.state === 'done');
      const failItem = arr.find(x => x && x.state === 'failed');
      const first = arr[0] || {};

      if (doneItem && doneItem.full_zip_url) {
        resultUrl = doneItem.full_zip_url;
        console.log('处理完成！');
      } else if (failItem) {
        throw new Error(`MinerU 处理失败: ${failItem.err_msg || '未知错误'}`);
      } else if (pollCount % 5 === 0) {
        const curState = first.state || 'unknown';
        console.log(`处理状态: ${curState} (${pollCount}/${POLL_MAX})`);
      }
    }
  }

  if (!resultUrl) {
    throw new Error(`处理超时，已尝试 ${pollCount} 次`);
  }

  // 4. 返回结果 URL
  return {
    zipUrl: resultUrl,
    message: '处理完成，结果已准备好'
  };
}

// 主函数
async function main() {
  const fileUrl = process.argv[2];

  if (!fileUrl) {
    console.error('用法: node ocr_extract.js <文件URL>');
    console.error('示例: node ocr_extract.js "https://example.com/file.pdf"');
    process.exit(1);
  }

  console.log(`正在提取文本: ${fileUrl}\n`);

  try {
    const result = await processFile(fileUrl);

    console.log('\n=== OCR 提取完成 ===');
    console.log(`结果文件地址: ${result.zipUrl}`);
    console.log('\n注意: MinerU 返回的是 ZIP 文件，包含 Markdown 格式的提取结果。');
    console.log('请下载并解压该 ZIP 文件获取完整内容。');

    // 尝试下载结果文件
    console.log('\n正在下载结果文件...');
    const zipPath = await downloadAndExtract(result.zipUrl);
    console.log(`结果已保存到: ${zipPath}`);
    console.log('请手动解压该文件查看 Markdown 内容。');

  } catch (error) {
    console.error(`\n错误: ${error.message}`);
    process.exit(1);
  }
}

main();
