obj-m := pwm-soft.o
KVERSION := $(shell uname -r)

all:
	$(MAKE) -C /lib/modules/$(KVERSION)/build M=$(CURDIR) modules

clean:
	$(MAKE) -C /lib/modules/$(KVERSION)/build M=$(CURDIR) clean


