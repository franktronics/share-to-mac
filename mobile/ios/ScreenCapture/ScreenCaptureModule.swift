import Foundation
import React

/// React Native bridge module exposing screen capture controls to JavaScript.
@objc(ScreenCaptureModule)
class ScreenCaptureModule: RCTEventEmitter {

    private let captureManager = ScreenCaptureManager()

    // MARK: - RCTEventEmitter

    override func supportedEvents() -> [String]! {
        return ["onCaptureStatusChange", "onCaptureError"]
    }

    override static func requiresMainQueueSetup() -> Bool {
        return false
    }

    // MARK: - Exposed Methods

    @objc(startCapture:port:resolver:rejecter:)
    func startCapture(
        host: String,
        port: NSNumber,
        resolve: @escaping RCTPromiseResolveBlock,
        reject: @escaping RCTPromiseRejectBlock
    ) {
        captureManager.onError = { [weak self] message in
            self?.sendEvent(withName: "onCaptureError", body: ["message": message])
        }

        captureManager.onStatusChange = { [weak self] isActive in
            self?.sendEvent(withName: "onCaptureStatusChange", body: ["isActive": isActive])
        }

        captureManager.startCapture(host: host, port: UInt16(truncating: port))
        resolve(nil)
    }

    @objc(stopCapture:rejecter:)
    func stopCapture(
        resolve: @escaping RCTPromiseResolveBlock,
        reject: @escaping RCTPromiseRejectBlock
    ) {
        captureManager.stopCapture()
        resolve(nil)
    }
}
