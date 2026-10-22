# STT following camera — original design contract

## Provenance and dependencies

Reference: local STT camera_follow.py supplied in stt-camera-follow-20261022, SHA256 d268f0b43247c2982ca92d9870cd68fcec452fd1258cf7fed2dec1b62ffdd029. Its source/README identify it as original STT work, not recovered MH4U code. No separate third-party license was supplied; no external licensing status is inferred. This adaptation uses that same project's authorized original design and contains no game code, models, textures or clips. New C implementation remains in the prototype source tree.

The Python reference used cross(forward, Y) for screen-right, opposite to the existing +Z-forward renderer. The C adapter explicitly preserves +X screen-right. It also retains the original relative camera floor and avoids a recenter shortcut through the hunter when no world backend is supplied. This is not a byte-for-byte or behavioral-equivalence port.

PR dependency: this change targets the GPU texture PR33 branch. Its inherited chain contains PR32/31/30/29 and PR21 (original bounded pose integration). It does not replace or merge PR21, change Pose/1, edit PR3/PR7 or change monitor network contracts. No resource-bank import.

## Coordinates, time and ownership

- World is right-handed input space with Y up; distances metres, angles radians. At yaw zero, the camera looks toward +Z, screen-right +X; eye starts on -Z side of target.
- Existing SttCamera owns yaw/pitch and stick deadzone. Existing stt_camera_step runs at fixed 60 Hz (yaw 2.1 rad/s; pitch 1.5 rad/s). The new follower owns only eye/focus tracking state and updates once per rendered frame, dt in seconds clamped to (0, 0.1]. It never feeds smoothed positions back into movement/collision state.
- Focus anchor is hunter XYZ plus configurable 1.1 m. Defaults: boom 6 m, exponential focus rate 10/s, recovery 4/s, sweep sphere radius 0.2 m, skin 0.03 m, relative minimum eye height 0.35 m. These are original design parameters, not confirmed MH4U values.
- Lens remains the existing GPU projection (about 57.1 degrees vertical, near 0.15 m/far 80 m). The reference's 55 degrees is intentionally not introduced as another renderer setting.
- L recenters existing yaw behind hunter heading. Triangle/reset and resume reset follower state; teleport/zone callers must request snap/reset. Existing fallback camera remains available when the follower rejects an update.

## Obstacles and failure

Sweep callback(start,end,radius) returns unobstructed distance in metres [0, segment length], with initial-overlap support. The core validates its return, constrains target-to-focus, focus-to-eye and previous-eye-to-new-eye, contracts immediately for a newly invalid view and recovers exponentially. Failed input/backend leaves state unchanged. Output exposes eye/focus, orthonormal view basis, boom distance, dt used, collision/backend-present/framing-compromised flags.

Synthetic plane tests cover a new wall, ceiling, recovery and an invalid backend. The radius is applied by that plane backend. This does not validate arbitrary triangle edge/vertex sweeps or SBC semantics.

Native integration deliberately passes NULL for world sweep: no SBC collision backend is implemented. Relative floor and default horizontal gap provide the previous design safeguard, but are not terrain/ceiling collision guarantees. A world obstruction may force the camera inside the normal framing distance; that is flagged. Body/equipment exclusion under simultaneous world constraints remains pending. No claim that the full hunter always stays visible.

## Validation and delivery

ASan/UBSan tests: XYZ anchors, orthonormal basis and lateral sign, focus convergence at 30/60/120 Hz, vertical tracking, 180-degree recentre/body gap, teleport, dt cap, invalid input/config/backend atomicity, synthetic wall/ceiling and recovery. A 240-frame C trace with original synthetic geometry supports PC visual inspection. This does not prove full eye-path equivalence at different update rates.

Compile the native adaptation with pinned VitaSDK; package version 00.23 is distinct from physically tested 00.22. No FTP, installation, console execution or new telemetry capture is authorized by this camera task. Existing 00.22 45 FPS evidence must not be attributed to 00.23.
