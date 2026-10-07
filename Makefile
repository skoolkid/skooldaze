SNAPSHOT = $(shell grep -Po 'SNAPSHOT=\$$SKOOLDAZE_HOME/\K.*' .ddiffsrc)
T2S = skool_daze.t2s

MK = $(SKOOLKIT_HOME)/tools/disassembly.mk
ifeq ($(wildcard $(MK)),)
    $(error $(MK): file not found)
endif
include $(MK)
