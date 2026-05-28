import Foundation
import ReplayKit
import UIKit

/// Captures the screen using ReplayKit, compresses each frame as JPEG,
/// and sends it over UDP via `UDPSender`.
class ScreenCaptureManager: NSObject {

    // MARK: - State

    private let recorder = RPScreenRecorder.shared()
    private let sender = UDPSender()
    private var isCapturing = false

    // JPEG compression quality (0.0 – 1.0). Lower = smaller packets, higher latency tolerance.
    private let jpegQuality: CGFloat = 0.5

    // MARK: - Public API

    var onError: ((String) -> Void)?
    var onStatusChange: ((Bool) -> Void)?

    func startCapture(host: String, port: UInt16) {
        guard !isCapturing else { return }
        guard recorder.isAvailable else {
            onError?("Screen recording is not available on this device.")
            return
        }

        sender.connect(host: host, port: port)

        recorder.startCapture(handler: { [weak self] sampleBuffer, bufferType, error in
            guard let self else { return }

            if let error {
                self.onError?(error.localizedDescription)
                return
            }

            // Only process video frames
            guard bufferType == .video else { return }

            self.processSampleBuffer(sampleBuffer)

        }, completionHandler: { [weak self] error in
            guard let self else { return }
            if let error {
                self.sender.disconnect()
                self.isCapturing = false
                self.onError?(error.localizedDescription)
                self.onStatusChange?(false)
            } else {
                self.isCapturing = true
                self.onStatusChange?(true)
            }
        })
    }

    func stopCapture() {
        guard isCapturing else { return }

        recorder.stopCapture { [weak self] error in
            guard let self else { return }
            self.sender.disconnect()
            self.isCapturing = false
            if let error {
                self.onError?(error.localizedDescription)
            }
            self.onStatusChange?(false)
        }
    }

    // MARK: - Private

    private func processSampleBuffer(_ sampleBuffer: CMSampleBuffer) {
        guard let imageBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }

        let ciImage = CIImage(cvPixelBuffer: imageBuffer)
        let context = CIContext()
        guard let cgImage = context.createCGImage(ciImage, from: ciImage.extent) else { return }

        let uiImage = UIImage(cgImage: cgImage)
        guard let jpegData = uiImage.jpegData(compressionQuality: jpegQuality) else { return }

        sender.send(frameData: jpegData)
    }
}
