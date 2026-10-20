---
source: https://docs.kernel.org/driver-api/firmware/request_firmware.html
fetched: 2026-10-20
---

# request_firmware API[¶](#request-firmware-api "Permalink to this heading")

You would typically load firmware and then load it into your device somehow. The typical firmware work flow is reflected below:

if(request_firmware(&fw_entry, \$FIRMWARE, device) == 0)\
       copy_fw_to_device(fw_entry-\>data, fw_entry-\>size);\
release_firmware(fw_entry);\

## Synchronous firmware requests[¶](#synchronous-firmware-requests "Permalink to this heading")

Synchronous firmware requests will wait until the firmware is found or until an error is returned.

### request_firmware[¶](#request-firmware "Permalink to this heading")

int request_firmware(const struct firmware \*\*firmware_p, const char \*name, struct [device](#c.request_firmware "device") \*device)[¶](#c.request_firmware "Permalink to this definition")\  
send firmware request and wait for it

**Parameters**

`const`` ``struct`` ``firmware`` ``**firmware_p`  
pointer to firmware image

`const`` ``char`` ``*name`  
name of firmware file

`struct`` ``device`` ``*device`  
device for which firmware is being loaded

**Description**

> **firmware_p** will be used to return a firmware image by the name of **name** for device **device**.
>
> Should be called from user context where sleeping is allowed.
>
> **name** will be used as \$FIRMWARE in the uevent environment and should be distinctive enough not to be confused with any other firmware image for this or any other device. It must not contain any “..” path components - “foo/bar..bin” is allowed, but “foo/../bar.bin” is not.
>
> Caller must hold the reference count of **device**.
>
> The function can be called safely inside device’s suspend and resume callback.

### firmware_request_nowarn[¶](#firmware-request-nowarn "Permalink to this heading")

int firmware_request_nowarn(const struct [firmware](#c.firmware_request_nowarn "firmware") \*\*firmware, const char \*name, struct [device](#c.firmware_request_nowarn "device") \*device)[¶](#c.firmware_request_nowarn "Permalink to this definition")\  
request for an optional fw module

**Parameters**

`const`` ``struct`` ``firmware`` ``**firmware`  
pointer to firmware image

`const`` ``char`` ``*name`  
name of firmware file

`struct`` ``device`` ``*device`  
device for which firmware is being loaded

**Description**

This function is similar in behaviour to [`request_firmware()`](#c.request_firmware "request_firmware"), except it doesn’t produce warning messages when the file is not found. The sysfs fallback mechanism is enabled if direct filesystem lookup fails. However, failures to find the firmware file with it are still suppressed. It is therefore up to the driver to check for the return value of this call and to decide when to inform the users of errors.

### firmware_request_platform[¶](#firmware-request-platform "Permalink to this heading")

int firmware_request_platform(const struct [firmware](#c.firmware_request_platform "firmware") \*\*firmware, const char \*name, struct [device](#c.firmware_request_platform "device") \*device)[¶](#c.firmware_request_platform "Permalink to this definition")\  
request firmware with platform-fw fallback

**Parameters**

`const`` ``struct`` ``firmware`` ``**firmware`  
pointer to firmware image

`const`` ``char`` ``*name`  
name of firmware file

`struct`` ``device`` ``*device`  
device for which firmware is being loaded

**Description**

This function is similar in behaviour to request_firmware, except that if direct filesystem lookup fails, it will fallback to looking for a copy of the requested firmware embedded in the platform’s main (e.g. UEFI) firmware.

### request_firmware_direct[¶](#request-firmware-direct "Permalink to this heading")

int request_firmware_direct(const struct firmware \*\*firmware_p, const char \*name, struct [device](#c.request_firmware_direct "device") \*device)[¶](#c.request_firmware_direct "Permalink to this definition")\  
load firmware directly without usermode helper

**Parameters**

`const`` ``struct`` ``firmware`` ``**firmware_p`  
pointer to firmware image

`const`` ``char`` ``*name`  
name of firmware file

`struct`` ``device`` ``*device`  
device for which firmware is being loaded

**Description**

This function works pretty much like [`request_firmware()`](#c.request_firmware "request_firmware"), but this doesn’t fall back to usermode helper even if the firmware couldn’t be loaded directly from fs. Hence it’s useful for loading optional firmwares, which aren’t always present, without extra long timeouts of udev.

### request_firmware_into_buf[¶](#request-firmware-into-buf "Permalink to this heading")

int request_firmware_into_buf(const struct firmware \*\*firmware_p, const char \*name, struct [device](#c.request_firmware_into_buf "device") \*device, void \*buf, size_t size)[¶](#c.request_firmware_into_buf "Permalink to this definition")\  
load firmware into a previously allocated buffer

**Parameters**

`const`` ``struct`` ``firmware`` ``**firmware_p`  
pointer to firmware image

`const`` ``char`` ``*name`  
name of firmware file

`struct`` ``device`` ``*device`  
device for which firmware is being loaded and DMA region allocated

`void`` ``*buf`  
address of buffer to load firmware into

`size_t`` ``size`  
size of buffer

**Description**

This function works pretty much like [`request_firmware()`](#c.request_firmware "request_firmware"), but it doesn’t allocate a buffer to hold the firmware data. Instead, the firmware is loaded directly into the buffer pointed to by **buf** and the **firmware_p** data member is pointed at **buf**.

This function doesn’t cache firmware either.

## Asynchronous firmware requests[¶](#asynchronous-firmware-requests "Permalink to this heading")

Asynchronous firmware requests allow driver code to not have to wait until the firmware or an error is returned. Function callbacks are provided so that when the firmware or an error is found the driver is informed through the callback. [`request_firmware_nowait()`](#c.request_firmware_nowait "request_firmware_nowait") cannot be called in atomic contexts.

### request_firmware_nowait[¶](#request-firmware-nowait "Permalink to this heading")

int request_firmware_nowait(struct [module](#c.request_firmware_nowait "module") \*module, bool uevent, const char \*name, struct [device](#c.request_firmware_nowait "device") \*device, gfp_t gfp, void \*context, void (\*cont)(const struct firmware \*fw, void \*context))[¶](#c.request_firmware_nowait "Permalink to this definition")\  
asynchronous version of request_firmware

**Parameters**

`struct`` ``module`` ``*module`  
module requesting the firmware

`bool`` ``uevent`  
sends uevent to copy the firmware image if this flag is non-zero else the firmware copy must be done manually.

`const`` ``char`` ``*name`  
name of firmware file

`struct`` ``device`` ``*device`  
device for which firmware is being loaded

`gfp_t`` ``gfp`  
allocation flags

`void`` ``*context`  
will be passed over to **cont**, and **fw** may be `NULL` if firmware request fails.

`void`` ``(*cont)(const`` ``struct`` ``firmware`` ``*fw,`` ``void`` ``*context)`  
function will be called asynchronously when the firmware request is over.

**Description**

> Caller must hold the reference count of **device**.
>
> Asynchronous variant of request_firmware() for user contexts:  
> - sleep for as small periods as possible since it may increase kernel boot time of built-in device drivers requesting firmware in their -\>`probe()` methods, if **gfp** is GFP_KERNEL.
>
> - can’t sleep at all if **gfp** is GFP_ATOMIC.

## Special optimizations on reboot[¶](#special-optimizations-on-reboot "Permalink to this heading")

Some devices have an optimization in place to enable the firmware to be retained during system reboot. When such optimizations are used the driver author must ensure the firmware is still available on resume from suspend, this can be done with [`firmware_request_cache()`](#c.firmware_request_cache "firmware_request_cache") instead of requesting for the firmware to be loaded.

### firmware_request_cache()[¶](#firmware-request-cache "Permalink to this heading")

int firmware_request_cache(struct [device](#c.firmware_request_cache "device") \*device, const char \*name)[¶](#c.firmware_request_cache "Permalink to this definition")\  
cache firmware for suspend so resume can use it

**Parameters**

`struct`` ``device`` ``*device`  
device for which firmware should be cached for

`const`` ``char`` ``*name`  
name of firmware file

**Description**

There are some devices with an optimization that enables the device to not require loading firmware on system reboot. This optimization may still require the firmware present on resume from suspend. This routine can be used to ensure the firmware is present on resume from suspend in these situations. This helper is not compatible with drivers which use [`request_firmware_into_buf()`](#c.request_firmware_into_buf "request_firmware_into_buf") or [`request_firmware_nowait()`](#c.request_firmware_nowait "request_firmware_nowait") with no uevent set.

## request firmware API expected driver use[¶](#request-firmware-api-expected-driver-use "Permalink to this heading")

Once an API call returns you process the firmware and then release the firmware. For example if you used [`request_firmware()`](#c.request_firmware "request_firmware") and it returns, the driver has the firmware image accessible in fw_entry-\>{data,size}. If something went wrong [`request_firmware()`](#c.request_firmware "request_firmware") returns non-zero and fw_entry is set to NULL. Once your driver is done with processing the firmware it can call release_firmware(fw_entry) to release the firmware image and any related resource.
