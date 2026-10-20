obj-m := leds-ktd202x.o
KVERSION := $(shell uname -r)

all:
	        $(MAKE) -C /lib/modules/$(KVERSION)/build M=$(CURDIR) modules

clean:
	        $(MAKE) -C /lib/modules/$(KVERSION)/build M=$(CURDIR) clean


