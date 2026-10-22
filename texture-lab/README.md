# STT 00.22 — GPU texture comparison

Small local terrain crop and assembled hunter with original-size decoded base textures and UVs. Reuses original STT gait and SBC contact controller. GXM performs projection, near/far clipping, perspective texture sampling and depth testing. No runtime shader compiler or plugin installation is required: the build links libvita2d and its precompiled shader objects.

The VPK contains only executable and metadata; private texture-zone.bin and existing map-zone.bin stay outside GitHub. The texture stream has bounded counts, dimensions, byte budget, finite-coordinate/index checks and exact EOF. The loader keeps a previous scene unchanged on failed replacement. Sources assume little-endian IEEE float32 as Vita/CI targets.

Controls: sticks move/orbit; R switches linear/point sampling on the same scene; Circle switches 30/45 cap; Triangle resets; Select starts/stops the existing three-minute metric sender; Start exits. Movement stays within a 10 m test radius; terrain triangles are cropped at 14 m. This is a renderer trial, not the complete map or combat lab.

Limitations: no native foot IK; STT gait is not a recovered MH4U animation; base-color shader is opaque and does not reproduce original materials, foliage cutouts, lighting or effects. No mip chain in this trial. Original texture resolution is preserved, without AI enlargement. GPU submission stage times are CPU timings; present_us includes synchronous completion and display queue work, not a GPU utilization percentage. Compare fixed camera/action captures; the cropped GPU scene is not geometry-equivalent to the full 00.21 scene. No physical FPS or visual result is asserted by CI.

Implementation references (API/shader behavior, not game assets):
- https://github.com/xerpi/libvita2d/blob/master/libvita2d/shader/texture_v.cg
- https://github.com/xerpi/libvita2d/blob/master/libvita2d/shader/clear_v.cg
- https://github.com/vitasdk/vita-headers/blob/master/include/psp2/gxm.h

Automated checks: original checkerboard fixture, truncated/trailing/oversized/nonfinite/index cases, near/far and hunter transform checks under ASan/UBSan; pinned VitaSDK build; VPK identity/content inspection; Windows portable stream reviewer. Physical validation remains separate.
