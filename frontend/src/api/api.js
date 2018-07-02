export const test = 'http://127.0.0.1:8000';
// export const test = 'http://192.168.193.130:8000';
// export const test = 'http://120.79.232.23:8000';

/**
 * 真正的请求
 * @param url 请求地址
 * @param options 请求参数
 * @param method 请求方式
 * @param header 头文件
 */
function commonFetcdh(url, options, header='', method = 'GET') {
    let initObj = {};
    if (method === 'GET') { // 如果是GET请求，拼接url
        url += '?' + searchStr;
        initObj = {
            method: method,
        }
    } else {
        initObj = {
            method: method,
            headers: header,
            body: options
        }
    }
    fetch(url, initObj).then((res) => {
        return res.json()
    }).then((res) => {
        return res
    })
}

/**
 * GET请求
 * @param url 请求地址
 * @param options 请求参数
 */
function GET(url, options) {
    return commonFetcdh(url, options, 'GET')
}

/**
 * POST请求
 * @param url 请求地址
 * @param options 请求参数
 * @param header 头文件
 */
function POST(url, options, header) {
    return commonFetcdh(url, options, header,'POST')
}
export { //很关键
    POST,GET
}