// NVIDIA DLSS Super Resolution through Streamline 2.x (manual Vulkan hooking, no proxy), in place of
// FSR's step-3 dispatch (vk_fsr3.c record_upscale): same inputs (the tone-mapped colour, the prepared depth and motion
// at the render size, the jitter in pixels), same output image, same blit to the stretch target. Steps 1-2 (the
// resolve/stretch detection, depth/motion prep, image management) stay FSR3's; this file only talks to SL.
//
// XC2_UPSCALER=dlss selects it, XC2_DLSS_MODE the DLSS mode (off|dlaa|quality|balanced|performance|ultraperformance).
// Without sl.interposer.dll next to the executable (staged by tools/build_game.py copy_dlss) or on a non-NVIDIA GPU
// vk_dlss_available stays 0 and the FSR path runs. Phase 2 (frame generation) and Phase 3 (neural rendering) build on
// this file's loader and init.
#pragma once

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// Before vkCreateInstance (vk_device.c create_instance): loads sl.interposer.dll and runs slInit, so the feature
// requirements below are known. A no-op unless XC2_UPSCALER=dlss.
void vk_dlss_early(void);
// Append the instance / device extension names SL requires to out (room for cap); returns how many were written.
// Valid from vk_dlss_early until vk_dlss_release.
int vk_dlss_instance_ext(const char **out, int cap);
int vk_dlss_device_ext(const char **out, int cap);
// After vkCreateDevice (vk_device.c create_device): hands SL the device and checks DLSS support on phys. Returns 1
// when a dispatch may run. gfx/comp families and the first queue index of each (0 here: no extra queues requested).
int vk_dlss_bind(void *device, void *instance, void *phys, unsigned gfx_family, unsigned comp_family);
// 1 when a dispatch may run: the library loaded, the device bound, the adapter supports DLSS, and the mode is not off.
int vk_dlss_available(void);
int vk_dlss_dlaa(void); // available and XC2_DLSS_MODE=dlaa: run at native resolution
// One upscale on cmd (the replay thread, like FSR's dispatch): colour/depth/motion in SHADER_READ_ONLY, out in
// GENERAL, all single-layer 2D. mvscale maps the motion values to [-1,1]; near/far/fov describe the game's camera.
// reset clears DLSS history (a camera cut, or the first frame). Returns 1 on success.
int vk_dlss_dispatch(void *cmd, void *color, void *color_view, uint32_t color_format, void *depth, void *depth_view,
                     uint32_t depth_format, void *mvec, void *mvec_view, uint32_t mvec_format, uint32_t rw, uint32_t rh,
                     uint32_t ow, uint32_t oh, const float jitter[2], const float mvscale[2], float near_z, float far_z,
                     float fov, int reset, void *out, void *out_view, uint32_t out_format);
// Before vkDestroyDevice.
void vk_dlss_release(void);

#ifdef __cplusplus
}
#endif
