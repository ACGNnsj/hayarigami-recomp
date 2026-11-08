// nn::ro overrides: the runtime module loader. A statically recompiled port links main, subsdk0 and sdk into the
// executable, so nothing is ever loaded through ro here: the initialisation entry points succeed and answer a neutral
// value, and an actual LoadModule call stops with a named fatal instead of walking the guest's module list.
#include "host.h"

static void ro_ok(Cpu *c) { ret_x(c, 0); }

static void ro_no_load(Cpu *c) {
    (void)c;
    rt_fatal("nn::ro::LoadModule: the game tried to load an NRO; this port links every module statically");
}

// void Initialize(), void InitializeWithPortName(const char *): no service to open
HOST_OVERRIDE("_ZN2nn2ro10InitializeEv", ro_ok);
HOST_OVERRIDE("_ZN2nn2ro22InitializeWithPortNameEPKc", ro_ok);
// Result GetBufferSize(size_t *out, const void *nro)
HOST_OVERRIDE("_ZN2nn2ro13GetBufferSizeEPmPKv", ro_ok);
// Result LookupSymbol(uintptr_t *out, const char *) / LookupModuleSymbol(uintptr_t *, const Module *, const char *)
HOST_OVERRIDE("_ZN2nn2ro12LookupSymbolEPmPKc", ro_ok);
HOST_OVERRIDE("_ZN2nn2ro18LookupModuleSymbolEPmPKNS0_6ModuleEPKc", ro_ok);
// Result RegisterModuleInfo(RegistrationInfo *, const void *) / UnregisterModuleInfo(RegistrationInfo *)
HOST_OVERRIDE("_ZN2nn2ro18RegisterModuleInfoEPNS0_16RegistrationInfoEPKv", ro_ok);
HOST_OVERRIDE("_ZN2nn2ro20UnregisterModuleInfoEPNS0_16RegistrationInfoE", ro_ok);
HOST_OVERRIDE("_ZN2nn2ro10LoadModuleEPNS0_6ModuleEPKvPvmi", ro_no_load);
HOST_OVERRIDE("_ZN2nn2ro10LoadModuleEPNS0_6ModuleEPKvPvmib", ro_no_load);
