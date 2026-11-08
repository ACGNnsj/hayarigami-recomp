// Display-resolution change events (nn::oe). The host window has one fixed size for the session, so the game is told
// nothing changes: the event it is handed is a real kernel event that is never signalled.
#include "host.h"
#include "kernel.h"

static void ov_resolution_change_event(Cpu *c) {
    kern_bind_system_event(c, arg_x(c, 0), 1);
    ret_x(c, 0);
}

// Result GetDefaultDisplayResolution(int *width, int *height): 1920x1080, the window's default size
static void ov_default_resolution(Cpu *c) {
    int *w = arg_p(c, 0), *h = arg_p(c, 1);
    if (w) *w = 1920;
    if (h) *h = 1080;
    ret_x(c, 0);
}

HOST_OVERRIDE("_ZN2nn2oe38GetDefaultDisplayResolutionChangeEventEPNS_2os11SystemEventE", ov_resolution_change_event);
HOST_OVERRIDE("_ZN2nn2oe27GetDefaultDisplayResolutionEPiS1_", ov_default_resolution);
