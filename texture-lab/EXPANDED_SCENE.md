# Expanded private-scene support — 00.24

Removes the fixed 10 m origin crop. Movement is bounded by the supplied ground and wall stream. Starts at CAP30 without changing CPU/GPU clock settings. Left stick walks, right stick moves camera, hold R to run; Square changes texture filtering. L recenters, Triangle resets, Select enables existing metrics, Circle toggles CAP30/45, Start exits.

The bounded reader accepts legacy16 and optional33-pose hunter banks: idle0, walk1–16, run17–32. These are prototype transitions; original game timing is not claimed. Static groups use conservative clip-frustum rejection before allocating frame-pool buffers. Synthetic fixtures check the new bank and culling. No commercial assets, scene data, addresses or captures are included in this branch.

Build success does not establish FPS, memory stability, or visual correctness on physical PS Vita. Private scene conversion and transfer receipts are kept outside GitHub. Translucent ambient dust is omitted in the initial native scene because this renderer has no validated particle pass. Solid ship details and approximate baked material color remain.
