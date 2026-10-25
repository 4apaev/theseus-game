import fs from 'node:fs'
import zlib from 'node:zlib'

const paeth = (a, b, c) => {
    const p = a + b - c
    const da = Math.abs(p - a), db = Math.abs(p - b), dc = Math.abs(p - c)
    return da <= db && da <= dc ? a : db <= dc ? b : c
}

for (const file of process.argv.slice(2)) {
    const buf = fs.readFileSync(file)
    let width, height, depth, type
    const parts = []
    for (let pos = 8; pos < buf.length;) {
        const len = buf.readUInt32BE(pos)
        const tag = buf.toString('ascii', pos + 4, pos + 8)
        const data = buf.subarray(pos + 8, pos + 8 + len)
        if (tag === 'IHDR') {
            width = data.readUInt32BE(0)
            height = data.readUInt32BE(4)
            depth = data[8]
            type = data[9]
            if (data[12]) throw Error('interlaced png unsupported')
        }
        if (tag === 'IDAT') parts.push(data)
        pos += len + 12
    }
    if (depth !== 8 || type !== 6) throw Error('expected rgba8: ' + file)
    const stride = width * 4
    const raw = zlib.inflateSync(Buffer.concat(parts))
    const pixels = Buffer.alloc(height * stride)
    for (let y = 0; y < height; y++) {
        const filter = raw[y * (stride + 1)]
        for (let x = 0; x < stride; x++) {
            const i = y * stride + x
            const a = x >= 4 ? pixels[i - 4] : 0
            const b = y ? pixels[i - stride] : 0
            const c = y && x >= 4 ? pixels[i - stride - 4] : 0
            const predict = [0, a, b, Math.floor((a + b) / 2), paeth(a, b, c)][filter]
            pixels[i] = (raw[y * (stride + 1) + 1 + x] + predict) & 255
        }
    }
    const histogram = new Array(256).fill(0)
    const bounds = [width, height, 0, 0]
    for (let y = 0; y < height; y++) for (let x = 0; x < width; x++) {
        const alpha = pixels[(y * width + x) * 4 + 3]
        histogram[alpha]++
        if (alpha > 127) {
            bounds[0] = Math.min(bounds[0], x)
            bounds[1] = Math.min(bounds[1], y)
            bounds[2] = Math.max(bounds[2], x)
            bounds[3] = Math.max(bounds[3], y)
        }
    }
    const samples = [[0, 0], [width - 1, 0], [0, height - 1], [width - 1, height - 1], [500, 30], [50, 150]]
        .filter(([x, y]) => x < width && y < height)
        .map(([x, y]) => [x, y, ...pixels.subarray((y * width + x) * 4, (y * width + x) * 4 + 4)])
    const footY = Math.max(bounds[1], bounds[3] - 4)
    const footXs = []
    for (let x = bounds[0]; x <= bounds[2]; x++) {
        if (pixels[(footY * width + x) * 4 + 3] > 127) footXs.push(x)
    }
    const foot = [footXs[Math.floor(footXs.length / 2)] ?? Math.round((bounds[0] + bounds[2]) / 2), footY]
    console.log(JSON.stringify({ foot, file, width, height, transparent: histogram[0], solid: histogram[254] + histogram[255], soft: histogram.slice(1, 254).reduce((a, b) => a + b, 0), bounds, samples }))
    if (!histogram[0]) process.exitCode = 1
}
