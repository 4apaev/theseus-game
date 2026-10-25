import Foundation
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

let args = CommandLine.arguments
let spec = try JSONSerialization.jsonObject(with: Data(contentsOf: URL(fileURLWithPath: args[1]))) as! [String: Any]
let w = spec["w"] as! Int
let h = spec["h"] as! Int
let context = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8, bytesPerRow: w * 4, space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
let project = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
context.setFillColor(CGColor(red: 0.025, green: 0.045, blue: 0.085, alpha: 1))
context.fill(CGRect(x: 0, y: 0, width: w, height: h))
context.interpolationQuality = .high
for layer in spec["layers"] as! [[String: Any]] {
    let file = layer["file"] as! String
    let url = file.hasPrefix("/") ? URL(fileURLWithPath: file) : project.appendingPathComponent(file)
    let source = CGImageSourceCreateWithURL(url as CFURL, nil)!
    let image = CGImageSourceCreateImageAtIndex(source, 0, nil)!
    let x = layer["x"] as! Double
    let y = layer["y"] as! Double
    let width = layer["w"] as! Double
    let height = layer["h"] as! Double
    context.draw(image, in: CGRect(x: x, y: Double(h) - y - height, width: width, height: height))
}
let dest = CGImageDestinationCreateWithURL(URL(fileURLWithPath: args[2]) as CFURL, UTType.png.identifier as CFString, 1, nil)!
CGImageDestinationAddImage(dest, context.makeImage()!, nil)
if !CGImageDestinationFinalize(dest) { fatalError("png export failed") }
