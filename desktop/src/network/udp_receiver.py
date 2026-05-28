import socket
import struct
import threading
from collections import defaultdict
from typing import Callable, Optional

# Header layout: frameId(4) + chunkIndex(2) + totalChunks(2) + chunkSize(4) = 12 bytes
HEADER_FORMAT = ">IHHH"  # big-endian: uint32, uint16, uint16, uint16
HEADER_SIZE = struct.calcsize(HEADER_FORMAT) + 2  # +2 for the uint32 chunkSize padding

# Correct header: frameId(4) + chunkIndex(2) + totalChunks(2) + chunkSize(4)
HEADER_STRUCT = struct.Struct(">IHHI")
HEADER_BYTES = HEADER_STRUCT.size  # 12


class UDPReceiver:
    """
    Listens on a UDP port and reassembles chunked JPEG frames sent by the iOS app.

    Each datagram carries a 12-byte header followed by the chunk payload.
    Once all chunks for a frame are received, `on_frame` is called with the
    complete JPEG bytes.
    """

    def __init__(self, port: int, on_frame: Callable[[bytes], None]):
        self._port = port
        self._on_frame = on_frame
        self._socket: Optional[socket.socket] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False

        # Buffer: { frameId -> { chunkIndex -> bytes } }
        self._buffers: dict[int, dict[int, bytes]] = defaultdict(dict)
        # Track expected total chunks per frame
        self._totals: dict[int, int] = {}

    def start(self) -> None:
        self._running = True
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(("0.0.0.0", self._port))
        self._socket.settimeout(1.0)

        self._thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._socket:
            self._socket.close()
            self._socket = None

    # ------------------------------------------------------------------
    # Internal

    def _receive_loop(self) -> None:
        while self._running:
            try:
                data, _ = self._socket.recvfrom(65535)
            except socket.timeout:
                continue
            except OSError:
                break

            if len(data) < HEADER_BYTES:
                continue

            frame_id, chunk_index, total_chunks, chunk_size = HEADER_STRUCT.unpack_from(data, 0)
            payload = data[HEADER_BYTES: HEADER_BYTES + chunk_size]

            self._buffers[frame_id][chunk_index] = payload
            self._totals[frame_id] = total_chunks

            if len(self._buffers[frame_id]) == total_chunks:
                frame_data = self._reassemble(frame_id)
                self._on_frame(frame_data)
                del self._buffers[frame_id]
                del self._totals[frame_id]

            # Drop stale frames to avoid unbounded memory growth
            self._evict_stale_frames(frame_id)

    def _reassemble(self, frame_id: int) -> bytes:
        chunks = self._buffers[frame_id]
        return b"".join(chunks[i] for i in sorted(chunks))

    def _evict_stale_frames(self, current_frame_id: int, max_lag: int = 30) -> None:
        stale = [fid for fid in list(self._buffers) if current_frame_id - fid > max_lag]
        for fid in stale:
            del self._buffers[fid]
            self._totals.pop(fid, None)
