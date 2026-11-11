// NVIDIA DLSS Super Resolution through Streamline 2.x, manual Vulkan hooking (see vk_dlss.h).
//
// Without the SDK headers at build time every function below is a stub (vk_dlss_available stays 0); without
// sl.interposer.dll at run time vk_dlss_early leaves the bridge unloaded. Either way the game runs on FSR.
#include "vk_dlss.h"

#if !__has_include(<sl.h>)

void vk_dlss_early(void) {}
int vk_dlss_instance_ext(const char **out, int cap) {
    (void)out, (void)cap;
    return 0;
}
int vk_dlss_device_ext(const char **out, int cap) {
    (void)out, (void)cap;
    return 0;
}
int vk_dlss_bind(void *device, void *instance, void *phys, unsigned gfx_family, unsigned comp_family) {
    (void)device, (void)instance, (void)phys, (void)gfx_family, (void)comp_family;
    return 0;
}
int vk_dlss_available(void) { return 0; }
int vk_dlss_dlaa(void) { return 0; }
int vk_dlss_dispatch(void *cmd, void *color, void *color_view, uint32_t color_format, void *depth, void *depth_view,
                     uint32_t depth_format, void *mvec, void *mvec_view, uint32_t mvec_format, uint32_t rw, uint32_t rh,
                     uint32_t ow, uint32_t oh, const float jitter[2], const float mvscale[2], float near_z, float far_z,
                     float fov, int reset, void *out, void *out_view, uint32_t out_format) {
    (void)cmd, (void)color, (void)color_view, (void)color_format, (void)depth, (void)depth_view;
    (void)depth_format, (void)mvec, (void)mvec_view, (void)mvec_format, (void)rw, (void)rh, (void)ow, (void)oh;
    (void)jitter, (void)mvscale, (void)near_z, (void)far_z, (void)fov, (void)reset, (void)out, (void)out_view;
    (void)out_format;
    return 0;
}
void vk_dlss_release(void) {}

#else // the Streamline SDK is on the include path

#include <math.h>
#include <string.h>

#ifdef _WIN32
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#endif

#include <vulkan/vulkan.h>   // before the SL headers: sl_helpers_vk.h needs the Vk types

#include <sl.h>
#include <sl_consts.h>
#include <sl_dlss.h>
#include <sl_helpers_vk.h>

extern "C" {
#include "cfg.h"
#include "host.h"
#include "platform/platform.h"
}

static void *g_lib;
static PFun_slInit *f_init;
static PFun_slShutdown *f_shutdown;
static PFun_slIsFeatureSupported *f_supported;
static PFun_slGetFeatureRequirements *f_requirements;
static PFun_slGetNewFrameToken *f_token;
static PFun_slSetConstants *f_constants;
static PFun_slSetTagForFrame *f_tag;
static PFun_slDLSSSetOptions *f_options;
static PFun_slDLSSGetOptimalSettings *f_optimal;
static PFun_slEvaluateFeature *f_evaluate;
static PFun_slSetVulkanInfo *f_vulkan;
static PFun_slGetFeatureFunction *f_featurefn;
static void *g_feat; // sl.dlss.dll: DLSS-specific entry points

static int g_inited, g_usable;
static int g_warned; // bits of warn_once below
static const char *g_req_instance[8];
static const char *g_req_device[16];
static int g_n_instance, g_n_device;
static uint32_t g_frame;
static sl::ViewportHandle g_viewport{0};
static char g_opt_logged[32]; // "mode@WxH" already reported by slDLSSGetOptimalSettings

static void warn_once(int bit, const char *what) {
    if (g_warned & bit) return;
    g_warned |= bit;
    rt_log("vk: DLSS: %s", what);
}

static void log_cb(sl::LogType type, const char *msg) {
    (void)type;
    rt_log("vk: SL: %s", msg);
}

static void *sym(const char *name) {
    void *p = g_lib ? plat_lib_sym(g_lib, name) : NULL; // core API: sl.interposer.dll
    if (!p && g_feat) p = plat_lib_sym(g_feat, name);   // DLSS API: sl.dlss.dll
    return p;
}

void vk_dlss_early(void) {
    if (g_inited) return;
    g_inited = 1;
    if (strcmp(cfg_value("XC2_UPSCALER"), "dlss")) return; // FSR path: never touch Streamline
#ifdef _WIN32
    char exe[MAX_PATH], path[MAX_PATH];
    DWORD n = GetModuleFileNameA(NULL, exe, (DWORD)sizeof exe);
    if (n > 0 && n < sizeof exe) {
        char *s = strrchr(exe, '\\');
        if (s) {
            size_t dirlen = (size_t)(s - exe);
            if (dirlen + 20 < sizeof path) {
                memcpy(path, exe, dirlen);
                path[dirlen] = 0;
                strcat(path, "\\sl.interposer.dll");
                g_lib = plat_lib_open(path);
                strcpy(path + dirlen, "\\sl.dlss.dll");
                g_feat = plat_lib_open(path);
            }
        }
    }
    if (!g_lib) g_lib = plat_lib_open("sl.interposer.dll"); // last resort: default search
#else
    g_lib = plat_lib_open("sl.interposer.dll");
#endif
    if (!g_lib) {
        rt_log("vk: DLSS off: sl.interposer.dll not found next to the executable");
        return;
    }
    f_init = (PFun_slInit *)sym("slInit");
    f_shutdown = (PFun_slShutdown *)sym("slShutdown");
    f_supported = (PFun_slIsFeatureSupported *)sym("slIsFeatureSupported");
    f_requirements = (PFun_slGetFeatureRequirements *)sym("slGetFeatureRequirements");
    f_token = (PFun_slGetNewFrameToken *)sym("slGetNewFrameToken");
    f_constants = (PFun_slSetConstants *)sym("slSetConstants");
    f_tag = (PFun_slSetTagForFrame *)sym("slSetTagForFrame");
    // NOTE: DLSS entry points are NOT static DLL exports; the interposer resolves
    // them per-feature at runtime via slGetFeatureFunction (see sl.h inline wrappers).
    // Loaded lazily in vk_dlss_available() after slInit. Set NULL here.
    f_options = NULL;
    f_optimal = NULL;
    f_evaluate = (PFun_slEvaluateFeature *)sym("slEvaluateFeature");
    f_vulkan = (PFun_slSetVulkanInfo *)sym("slSetVulkanInfo");
    f_featurefn = (PFun_slGetFeatureFunction *)sym("slGetFeatureFunction");
    if (!f_init || !f_shutdown || !f_supported || !f_requirements || !f_token || !f_constants || !f_tag ||
        !f_evaluate || !f_vulkan || !f_featurefn) {
        rt_log("vk: DLSS off: sl.interposer.dll misses entry points");
        g_lib = NULL;
        return;
    }
    sl::Preferences pref{};
    sl::Feature dlss[] = {sl::kFeatureDLSS};
    pref.featuresToLoad = dlss;
    pref.numFeaturesToLoad = 1;
    pref.flags |= sl::PreferenceFlags::eUseFrameBasedResourceTagging; // slSetTagForFrame requires this
    pref.renderAPI = sl::RenderAPI::eVulkan;
    pref.engine = sl::EngineType::eCustom; // an engine id stands in for the NVIDIA application id
    pref.engineVersion = "hayarigami-recomp";
    // NGX project identity: Init_with_ProjectID needs no NVIDIA-issued numeric id,
    // just a stable GUID + engine name. Generated once for this project, do not change
    // (NGX OTA cache keys off it).
    pref.projectId = "3f6d1a2b-7c4e-4d8f-9a0b-5e6f1c2d3a4b";
    pref.logMessageCallback = log_cb;
    pref.logLevel = sl::LogLevel::eDefault; // present path validated 2026-11-11 (tags+evaluate clean, 0 fallback)
    sl::Result r = f_init(pref, sl::kSDKVersion);
    if (r != sl::Result::eOk) {
        rt_log("vk: DLSS off: slInit failed (%d)", (int)r);
        g_lib = NULL;
        return;
    }
    sl::FeatureRequirements req{};
    if (f_requirements(sl::kFeatureDLSS, req) == sl::Result::eOk) {
        g_n_instance = req.vkNumInstanceExtensions < 8 ? (int)req.vkNumInstanceExtensions : 8;
        g_n_device = req.vkNumDeviceExtensions < 16 ? (int)req.vkNumDeviceExtensions : 16;
        for (int i = 0; i < g_n_instance; i++) g_req_instance[i] = req.vkInstanceExtensions[i];
        for (int i = 0; i < g_n_device; i++) g_req_device[i] = req.vkDeviceExtensions[i];
        if (req.vkNumFeatures12 + req.vkNumFeatures13)
            rt_log("vk: DLSS wants extra device features (12:%u 13:%u), attempting anyway", req.vkNumFeatures12,
                   req.vkNumFeatures13);
    }
    rt_log("vk: DLSS: Streamline initialised (+%d instance, +%d device extensions)", g_n_instance, g_n_device);
}

int vk_dlss_instance_ext(const char **out, int cap) {
    int n = g_n_instance < cap ? g_n_instance : cap;
    for (int i = 0; i < n; i++) out[i] = g_req_instance[i];
    return n;
}

int vk_dlss_device_ext(const char **out, int cap) {
    int n = g_n_device < cap ? g_n_device : cap;
    for (int i = 0; i < n; i++) out[i] = g_req_device[i];
    return n;
}

int vk_dlss_bind(void *device, void *instance, void *phys, unsigned gfx_family, unsigned comp_family) {
    if (!g_lib) return 0;
    sl::VulkanInfo info{};
    info.device = (VkDevice)device;
    info.instance = (VkInstance)instance;
    info.physicalDevice = (VkPhysicalDevice)phys;
    info.graphicsQueueFamily = gfx_family;
    info.graphicsQueueIndex = 0;
    info.computeQueueFamily = comp_family;
    info.computeQueueIndex = 0;
    if (f_vulkan(info) != sl::Result::eOk) {
        rt_log("vk: DLSS off: slSetVulkanInfo failed");
        return 0;
    }
    sl::AdapterInfo adapter{};
    adapter.vkPhysicalDevice = phys;
    sl::Result r = f_supported(sl::kFeatureDLSS, adapter);
    if (r == sl::Result::eOk) {
        // DLSS entry points resolve per-feature at runtime, only valid after the device is set.
        void *p = NULL, *q = NULL;
        if (f_featurefn(sl::kFeatureDLSS, "slDLSSSetOptions", p) == sl::Result::eOk) f_options = (PFun_slDLSSSetOptions *)p;
        if (f_featurefn(sl::kFeatureDLSS, "slDLSSGetOptimalSettings", q) == sl::Result::eOk)
            f_optimal = (PFun_slDLSSGetOptimalSettings *)q;
        if (!f_options || !f_optimal) rt_log("vk: DLSS off: feature functions unresolved");
    }
    g_usable = r == sl::Result::eOk && f_options && f_optimal;
    rt_log("vk: DLSS %s (slIsFeatureSupported %d)", g_usable ? "ready" : "not supported on this adapter", (int)r);
    return g_usable;
}

int vk_dlss_available(void) {
    return g_usable && strcmp(cfg_value("XC2_DLSS_MODE"), "off") != 0 &&
           strcmp(cfg_value("XC2_UPSCALER"), "dlss") == 0;
}

int vk_dlss_dlaa(void) { return vk_dlss_available() && !strcmp(cfg_value("XC2_DLSS_MODE"), "dlaa"); }

static sl::DLSSMode dlss_mode(void) {
    const char *m = cfg_value("XC2_DLSS_MODE");
    if (!strcmp(m, "dlaa")) return sl::DLSSMode::eDLAA;
    if (!strcmp(m, "balanced")) return sl::DLSSMode::eBalanced;
    if (!strcmp(m, "performance")) return sl::DLSSMode::eMaxPerformance;
    if (!strcmp(m, "ultraperformance")) return sl::DLSSMode::eUltraPerformance;
    return sl::DLSSMode::eMaxQuality;
}

// A Vulkan perspective (camera looks down -Z, depth 0..1) from the game's fov/aspect/near/far, row-major, no jitter.
// The game never hands its matrices over (FSR reconstructs everything from jitter + depth + motion too), so this
// synthesis only orients DLSS; the motion vectors carry the real movement. Re-verify visually on each change.
static void camera_matrices(float fov, float aspect, float near_z, float far_z, sl::Constants &c) {
    float f = 1.0f / tanf(fov * 0.5f);
    float a = far_z / (far_z - near_z), b = -far_z * near_z / (far_z - near_z);
    c.cameraViewToClip.setRow(0, sl::float4(f / aspect, 0, 0, 0));
    c.cameraViewToClip.setRow(1, sl::float4(0, -f, 0, 0));
    c.cameraViewToClip.setRow(2, sl::float4(0, 0, a, 1));
    c.cameraViewToClip.setRow(3, sl::float4(0, 0, b, 0));
    // inverse of the above (affine in x/y, projective in z)
    c.clipToCameraView.setRow(0, sl::float4(aspect / f, 0, 0, 0));
    c.clipToCameraView.setRow(1, sl::float4(0, -1.0f / f, 0, 0));
    c.clipToCameraView.setRow(2, sl::float4(0, 0, 0, -1.0f / b));
    c.clipToCameraView.setRow(3, sl::float4(0, 0, 1.0f / b, a / b));
    c.clipToPrevClip.setRow(0, sl::float4(1, 0, 0, 0));
    c.clipToPrevClip.setRow(1, sl::float4(0, 1, 0, 0));
    c.clipToPrevClip.setRow(2, sl::float4(0, 0, 1, 0));
    c.clipToPrevClip.setRow(3, sl::float4(0, 0, 0, 1));
    c.prevClipToClip.setRow(0, sl::float4(1, 0, 0, 0));
    c.prevClipToClip.setRow(1, sl::float4(0, 1, 0, 0));
    c.prevClipToClip.setRow(2, sl::float4(0, 0, 1, 0));
    c.prevClipToClip.setRow(3, sl::float4(0, 0, 0, 1));
    c.clipToLensClip.setRow(0, sl::float4(1, 0, 0, 0));
    c.clipToLensClip.setRow(1, sl::float4(0, 1, 0, 0));
    c.clipToLensClip.setRow(2, sl::float4(0, 0, 1, 0));
    c.clipToLensClip.setRow(3, sl::float4(0, 0, 0, 1));
}

static void tag_resource(sl::Resource &r, sl::ResourceTag &t, void *img, void *view, uint32_t layout, uint32_t format,
                         uint32_t w, uint32_t h, sl::BufferType type, sl::ResourceLifecycle life, uint32_t usage) {
    r = sl::Resource(sl::ResourceType::eTex2d, img, NULL, view, layout);
    r.width = w;
    r.height = h;
    r.nativeFormat = format;
    r.mipLevels = 1;
    r.arrayLayers = 1;
    r.usage = usage;
    sl::Extent e{(uint32_t)0, (uint32_t)0, w, h};
    t = sl::ResourceTag(&r, type, life, &e);
}

int vk_dlss_dispatch(void *cmd, void *color, void *color_view, uint32_t color_format, void *depth, void *depth_view,
                     uint32_t depth_format, void *mvec, void *mvec_view, uint32_t mvec_format, uint32_t rw, uint32_t rh,
                     uint32_t ow, uint32_t oh, const float jitter[2], const float mvscale[2], float near_z, float far_z,
                     float fov, int reset, void *out, void *out_view, uint32_t out_format) {
    if (!vk_dlss_available() || !rw || !rh || !ow || !oh || far_z <= near_z) return 0;
    sl::ViewportHandle vp(0);
    g_viewport = vp;
    sl::FrameToken *tok = NULL;
    uint32_t frame = ++g_frame;
    if (f_token(tok, &frame) != sl::Result::eOk || !tok) return warn_once(1, "slGetNewFrameToken failed"), 0;

    sl::Constants c{};
    camera_matrices(fov, (float)rw / (float)rh, near_z, far_z, c);
    c.jitterOffset = sl::float2{jitter[0], jitter[1]};
    c.mvecScale = sl::float2{mvscale[0], mvscale[1]};
    c.cameraPos = sl::float3{0, 0, 0};
    c.cameraUp = sl::float3{0, 1, 0};
    c.cameraRight = sl::float3{1, 0, 0};
    c.cameraFwd = sl::float3{0, 0, -1};
    c.cameraNear = near_z;
    c.cameraFar = far_z;
    c.cameraFOV = fov;
    c.cameraAspectRatio = (float)rw / (float)rh;
    c.depthInverted = sl::Boolean::eFalse;
    c.cameraMotionIncluded = sl::Boolean::eTrue;
    c.motionVectorsJittered = sl::Boolean::eTrue;
    c.reset = reset ? sl::Boolean::eTrue : sl::Boolean::eFalse;
    c.orthographicProjection = sl::Boolean::eFalse;
    if (f_constants(c, *tok, vp) != sl::Result::eOk) return warn_once(2, "slSetConstants failed"), 0;

    sl::DLSSMode mode = dlss_mode();
    sl::DLSSOptions o{};
    o.mode = mode;
    o.outputWidth = ow;
    o.outputHeight = oh;
    o.colorBuffersHDR = sl::Boolean::eFalse; // the tone-mapped LDR picture, like FSR's input
    o.useAutoExposure = sl::Boolean::eFalse; // no exposure input in this pipeline; the picture is display-referred
    if (f_options(vp, o) != sl::Result::eOk) return warn_once(4, "slDLSSSetOptions failed"), 0;

    char key[32];
    snprintf(key, sizeof key, "%d@%ux%u", (int)mode, ow, oh);
    if (strcmp(key, g_opt_logged)) {
        snprintf(g_opt_logged, sizeof g_opt_logged, "%s", key);
        sl::DLSSOptimalSettings s{};
        if (f_optimal(o, s) == sl::Result::eOk)
            rt_log("vk: DLSS mode %d to %ux%u: optimal render %ux%u (game renders %ux%u)", (int)mode, ow, oh,
                   s.optimalRenderWidth, s.optimalRenderHeight, rw, rh);
    }

    const uint32_t RO = VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL, GEN = VK_IMAGE_LAYOUT_GENERAL;
    const uint32_t SAMPLED = VK_IMAGE_USAGE_SAMPLED_BIT, STORAGE = VK_IMAGE_USAGE_STORAGE_BIT;
    sl::Resource r_in, r_out, r_depth, r_mvec;
    sl::ResourceTag t_in, t_out, t_depth, t_mvec;
    tag_resource(r_in, t_in, color, color_view, RO, color_format, rw, rh, sl::kBufferTypeScalingInputColor,
                 sl::ResourceLifecycle::eOnlyValidNow, SAMPLED);
    tag_resource(r_out, t_out, out, out_view, GEN, out_format, ow, oh, sl::kBufferTypeScalingOutputColor,
                 sl::ResourceLifecycle::eOnlyValidNow, STORAGE);
    tag_resource(r_depth, t_depth, depth, depth_view, RO, depth_format, rw, rh, sl::kBufferTypeDepth,
                 sl::ResourceLifecycle::eValidUntilPresent, SAMPLED);
    tag_resource(r_mvec, t_mvec, mvec, mvec_view, RO, mvec_format, rw, rh, sl::kBufferTypeMotionVectors,
                 sl::ResourceLifecycle::eOnlyValidNow, SAMPLED);
    const sl::ResourceTag tags[] = {t_in, t_out, t_depth, t_mvec};
    sl::Result tr = f_tag(*tok, vp, tags, 4, (sl::CommandBuffer *)cmd);
    if (tr != sl::Result::eOk) {
        static int tag_logged;
        if (!tag_logged) {
            tag_logged = 1;
            rt_log("vk: DLSS: slSetTagForFrame failed (%d); color %ux%u fmt %u, depth fmt %u, mvec fmt %u, out %ux%u fmt %u",
                   (int)tr, rw, rh, color_format, depth_format, mvec_format, ow, oh, out_format);
        }
        return 0;
    }

    const sl::BaseStructure *inputs[] = {&vp};
    sl::Result r = f_evaluate(sl::kFeatureDLSS, *tok, inputs, 1, (sl::CommandBuffer *)cmd);
    if (r != sl::Result::eOk) {
        g_usable = 0; // fall back to the FSR path from the next frame; this frame blits stale output
        rt_log("vk: DLSS off: slEvaluateFeature failed (%d)", (int)r);
        return 0;
    }
    return 1;
}

void vk_dlss_release(void) {
    g_usable = 0;
    g_n_instance = g_n_device = 0;
    g_frame = 0;
    g_opt_logged[0] = 0;
    if (g_lib && f_shutdown) f_shutdown();
    g_lib = NULL;
    f_init = NULL;
}

#endif
