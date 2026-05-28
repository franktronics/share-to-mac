import Foundation
import Network

/// Sends raw byte frames over UDP to a remote host.
/// Frames larger than `maxPayloadSize` are split into chunks with a simple header
/// so the receiver can reassemble them.
///
/// Header format per chunk (12 bytes):
///   [frameId: UInt32][chunkIndex: UInt16][totalChunks: UInt16][chunkSize: UInt32]
class UDPSender {

    // MARK: - Constants

    /// Max UDP payload size (safe value below typical MTU of 1500 bytes minus headers)
    private static let maxPayloadSize = 1400
    private static let headerSize = 12

    // MARK: - State

    private var connection: NWConnection?
    private let queue = DispatchQueue(label: "udp.sender.queue")
    private var frameId: UInt32 = 0

    // MARK: - Public API

    func connect(host: String, port: UInt16) {
        let endpoint = NWEndpoint.hostPort(
            host: NWEndpoint.Host(host),
            port: NWEndpoint.Port(rawValue: port)!
        )
        connection = NWConnection(to: endpoint, using: .udp)
        connection?.start(queue: queue)
    }

    func disconnect() {
        connection?.cancel()
        connection = nil
    }

    /// Encodes `data` into chunks and sends them as UDP datagrams.
    func send(frameData: Data) {
        guard let connection else { return }

        let payload = Array(frameData)
        let chunkSize = UDPSender.maxPayloadSize - UDPSender.headerSize
        let totalChunks = UInt16((payload.count + chunkSize - 1) / chunkSize)
        let currentFrameId = frameId
        frameId &+= 1

        for chunkIndex in 0..<totalChunks {
            let start = Int(chunkIndex) * chunkSize
            let end = min(start + chunkSize, payload.count)
            let chunk = Array(payload[start..<end])

            var packet = Data(capacity: UDPSender.headerSize + chunk.count)
            packet.append(contentsOf: withUnsafeBytes(of: currentFrameId.bigEndian) { Array($0) })
            packet.append(contentsOf: withUnsafeBytes(of: chunkIndex.bigEndian) { Array($0) })
            packet.append(contentsOf: withUnsafeBytes(of: totalChunks.bigEndian) { Array($0) })
            packet.append(contentsOf: withUnsafeBytes(of: UInt32(chunk.count).bigEndian) { Array($0) })
            packet.append(contentsOf: chunk)

            connection.send(content: packet, completion: .idempotent)
        }
    }
}
