SOURCEFILES = yun_pubnub/include/jsonParse.c c-core/core/pubnub_coreapi.c c-core/core/pubnub_ccore.c c-core/core/pubnub_netcore.c  c-core/lib/sockets/pbpal_sockets.c c-core/lib/sockets/pbpal_resolv_and_connect_sockets.c c-core/core/pubnub_alloc_std.c c-core/core/pubnub_assert_std.c c-core/core/pubnub_generate_uuid.c c-core/core/pubnub_blocking_io.c c-core/core/pubnub_json_parse.c c-core/core/pubnub_helper.c  c-core/posix/pubnub_version_posix.c  c-core/posix/pubnub_generate_uuid_posix.c c-core/posix/pbpal_posix_blocking_io.c c-core/core/pubnub_timers.c
CC = gcc
OS := $(shell uname)
ifeq ($(OS),Darwin)
SOURCEFILES += c-core/posix/monotonic_clock_get_time_darwin.c
else
SOURCEFILES += c-core/posix/monotonic_clock_get_time_posix.c
endif

CFLAGS =-g -I ./c-core/core  -I./c-core/posix -Wall -I yun_pubnub/include
# -g enables debugging, remove to get a smaller executable

LDFLAGS = -lpthread -lrt -ldl

all: solarMeter 

solarMeter: yun_pubnub/main.c $(SOURCEFILES) c-core/core/pubnub_ntf_sync.c
	$(CC) -o $@ $(CFLAGS) -D VERBOSE_DEBUG yun_pubnub/main.c c-core/core/pubnub_ntf_sync.c $(SOURCEFILES) $(LDFLAGS) 

clean:
	rm solarMeter
