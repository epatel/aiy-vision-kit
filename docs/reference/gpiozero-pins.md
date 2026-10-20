---
source: https://gpiozero.readthedocs.io/en/stable/api_pins.html
fetched: 2026-10-20
---

# 24. API - Pins[](#module-gpiozero.pins "Link to this heading")

As of release 1.1, the GPIO Zero library can be roughly divided into two things: pins and the devices that are connected to them. The majority of the documentation focuses on devices as pins are below the level that most users are concerned with. However, some users may wish to take advantage of the capabilities of alternative GPIO implementations or (in future) use GPIO extender chips. This is the purpose of the pins portion of the library.

When you construct a device, you pass in a pin specification. This is passed to a pin [`Factory`](#gpiozero.Factory "gpiozero.Factory") which turns it into a [`Pin`](#gpiozero.Pin "gpiozero.Pin") implementation. The default factory can be queried (and changed) with [`Device.pin_factory`](api_generic.html#gpiozero.Device.pin_factory "gpiozero.Device.pin_factory"). However, all classes (even internal devices) accept a *pin_factory* keyword argument to their constructors permitting the factory to be overridden on a per-device basis (the reason for allowing per-device factories is made apparent in the [Configuring Remote GPIO](remote_gpio.html) chapter).

This is illustrated in the following flow-chart:

![](_images/device_pin_flowchart.svg)

The default factory is constructed when the first device is initialised; if no default factory can be constructed (e.g. because no GPIO implementations are installed, or all of them fail to load for whatever reason), a [`BadPinFactory`](api_exc.html#gpiozero.BadPinFactory "gpiozero.BadPinFactory") exception will be raised at construction time.

After importing gpiozero, until constructing a gpiozero device, the pin factory is [`None`](https://docs.python.org/3.9/library/constants.html#None "(in Python v3.9)"), but at the point of first construction the default pin factory will come into effect:

pi@raspberrypi:~ \$ python3\
Python 3.7.3 (default, Apr  3 2019, 05:39:12)\
\[GCC 8.2.0\] on linux\
Type "help", "copyright", "credits" or "license" for more information.\
\>\>\> from gpiozero import Device, LED\
\>\>\> print(Device.pin_factory)\
None\
\>\>\> led = LED(2)\
\>\>\> Device.pin_factory\
\<gpiozero.pins.lgpio.LGPIOFactory object at 0xb667ae30\>\
\>\>\> led.pin_factory\
\<gpiozero.pins.lgpio.LGPIOFactory object at 0xb6323530\>\

As above, on a Raspberry Pi with the lgpio library installed, (assuming no environment variables are set), the default pin factory will be [`LGPIOFactory`](#gpiozero.pins.lgpio.LGPIOFactory "gpiozero.pins.lgpio.LGPIOFactory").

On a PC (with no pin libraries installed and no environment variables set), importing will work but attempting to create a device will raise [`BadPinFactory`](api_exc.html#gpiozero.BadPinFactory "gpiozero.BadPinFactory"):

ben@magicman:~ \$ python3\
Python 3.6.8 (default, Aug 20 2019, 17:12:48)\
\[GCC 8.3.0\] on linux\
Type "help", "copyright", "credits" or "license" for more information.\
\>\>\> from gpiozero import Device, LED\
\>\>\> print(Device.pin_factory)\
None\
\>\>\> led = LED(2)\
...\
BadPinFactory: Unable to load any default pin factory!\

## 24.1. Changing the pin factory[](#changing-the-pin-factory "Link to this heading")

Note

Check the pin factory support for your Pi model. Only lgpio works on the Pi 5.

The default pin factory can be replaced by specifying a value for the [`GPIOZERO_PIN_FACTORY`](cli_env.html#envvar-GPIOZERO_PIN_FACTORY) environment variable. For example:

pi@raspberrypi:~ \$ GPIOZERO_PIN_FACTORY=native python3\
Python 3.7.3 (default, Apr  3 2019, 05:39:12)\
\[GCC 8.2.0\] on linux\
Type "help", "copyright", "credits" or "license" for more information.\
\>\>\> from gpiozero import Device\
\>\>\> Device.\_default_pin_factory()\
\<gpiozero.pins.native.NativeFactory object at 0x762c26b0\>\

To set the [`GPIOZERO_PIN_FACTORY`](cli_env.html#envvar-GPIOZERO_PIN_FACTORY) for the rest of your session you can **export** this value:

pi@raspberrypi:~ \$ export GPIOZERO_PIN_FACTORY=native\
pi@raspberrypi:~ \$ python3\
Python 3.7.3 (default, Apr  3 2019, 05:39:12)\
\[GCC 8.2.0\] on linux\
Type "help", "copyright", "credits" or "license" for more information.\
\>\>\> import gpiozero\
\>\>\> Device.\_default_pin_factory()\
\<gpiozero.pins.native.NativeFactory object at 0x762c26b0\>\
\>\>\> quit()\
pi@raspberrypi:~ \$ python3\
Python 3.7.3 (default, Apr  3 2019, 05:39:12)\
\[GCC 8.2.0\] on linux\
Type "help", "copyright", "credits" or "license" for more information.\
\>\>\> import gpiozero\
\>\>\> Device.\_default_pin_factory()\
\<gpiozero.pins.native.NativeFactory object at 0x762c26b0\>\

If you add the **export** command to your `~/.bashrc` file, you’ll set the default pin factory for all future sessions too.

If the environment variable is set, the corresponding pin factory will be used, otherwise each of the four GPIO pin factories will be attempted to be used in turn.

The following values, and the corresponding [`Factory`](#gpiozero.Factory "gpiozero.Factory") and [`Pin`](#gpiozero.Pin "gpiozero.Pin") classes are listed in the table below. Factories are listed in the order that they are tried by default.

| Name | Factory class | Pin class | Pi support |
|----|----|----|----|
| lgpio | [`gpiozero.pins.lgpio.LGPIOFactory`](#gpiozero.pins.lgpio.LGPIOFactory "gpiozero.pins.lgpio.LGPIOFactory") | [`gpiozero.pins.lgpio.LGPIOPin`](#gpiozero.pins.lgpio.LGPIOPin "gpiozero.pins.lgpio.LGPIOPin") | All models |
| rpigpio | [`gpiozero.pins.rpigpio.RPiGPIOFactory`](#gpiozero.pins.rpigpio.RPiGPIOFactory "gpiozero.pins.rpigpio.RPiGPIOFactory") | [`gpiozero.pins.rpigpio.RPiGPIOPin`](#gpiozero.pins.rpigpio.RPiGPIOPin "gpiozero.pins.rpigpio.RPiGPIOPin") | (not Pi 5) |
| pigpio | [`gpiozero.pins.pigpio.PiGPIOFactory`](#gpiozero.pins.pigpio.PiGPIOFactory "gpiozero.pins.pigpio.PiGPIOFactory") | [`gpiozero.pins.pigpio.PiGPIOPin`](#gpiozero.pins.pigpio.PiGPIOPin "gpiozero.pins.pigpio.PiGPIOPin") | (not Pi 5) |
| native | [`gpiozero.pins.native.NativeFactory`](#gpiozero.pins.native.NativeFactory "gpiozero.pins.native.NativeFactory") | [`gpiozero.pins.native.NativePin`](#gpiozero.pins.native.NativePin "gpiozero.pins.native.NativePin") | (not Pi 5) |

If you need to change the default pin factory from within a script, either set [`Device.pin_factory`](api_generic.html#gpiozero.Device.pin_factory "gpiozero.Device.pin_factory") to the new factory instance to use:

from gpiozero.pins.native import NativeFactory\
from gpiozero import Device, LED\
\
Device.pin_factory = NativeFactory()\
\
\# These will now implicitly use NativePin instead of RPiGPIOPin\
led1 = LED(16)\
led2 = LED(17)\

Or use the *pin_factory* keyword parameter mentioned above:

from gpiozero.pins.native import NativeFactory\
from gpiozero import LED\
\
my_factory = NativeFactory()\
\
\# This will use NativePin instead of RPiGPIOPin for led1\
\# but led2 will continue to use RPiGPIOPin\
led1 = LED(16, pin_factory=my_factory)\
led2 = LED(17)\

Certain factories may take default information from additional sources. For example, to default to creating pins with [`gpiozero.pins.pigpio.PiGPIOPin`](#gpiozero.pins.pigpio.PiGPIOPin "gpiozero.pins.pigpio.PiGPIOPin") on a remote pi called “remote-pi” you can set the [`PIGPIO_ADDR`](cli_env.html#envvar-PIGPIO_ADDR) environment variable when running your script:

\$ GPIOZERO_PIN_FACTORY=pigpio PIGPIO_ADDR=remote-pi python3 my_script.py\

Like the [`GPIOZERO_PIN_FACTORY`](cli_env.html#envvar-GPIOZERO_PIN_FACTORY) value, these can be exported from your `~/.bashrc` script too.

Warning

The astute and mischievous reader may note that it is possible to mix factories, e.g. using [`RPiGPIOFactory`](#gpiozero.pins.rpigpio.RPiGPIOFactory "gpiozero.pins.rpigpio.RPiGPIOFactory") for one pin, and [`NativeFactory`](#gpiozero.pins.native.NativeFactory "gpiozero.pins.native.NativeFactory") for another. This is unsupported, and if it results in your script crashing, your components failing, or your Raspberry Pi turning into an actual raspberry pie, you have only yourself to blame.

Sensible uses of multiple pin factories are given in [Configuring Remote GPIO](remote_gpio.html).

## 24.2. Mock pins[](#mock-pins "Link to this heading")

There’s also a [`MockFactory`](#gpiozero.pins.mock.MockFactory "gpiozero.pins.mock.MockFactory") which generates entirely fake pins. This was originally intended for GPIO Zero developers who wish to write tests for devices without having to have the physical device wired in to their Pi. However, they have also proven useful in developing GPIO Zero scripts without having a Pi to hand. This pin factory will never be loaded by default; it must be explicitly specified, either by setting an environment variable or setting the pin factory within the script. For example:

pi@raspberrypi:~ \$ GPIOZERO_PIN_FACTORY=mock python3\

or:

from gpiozero import Device, LED\
from gpiozero.pins.mock import MockFactory\
\
Device.pin_factory = MockFactory()\
\
led = LED(2)\

You can create device objects and inspect their value changing as you’d expect:

pi@raspberrypi:~ \$ GPIOZERO_PIN_FACTORY=mock python3\
Python 3.7.3 (default, Apr  3 2019, 05:39:12)\
\[GCC 8.2.0\] on linux\
Type "help", "copyright", "credits" or "license" for more information.\
\>\>\> from gpiozero import LED\
\>\>\> led = LED(2)\
\>\>\> led.value\
0\
\>\>\> led.on()\
\>\>\> led.value\
1\

You can even control pin state changes to simulate device behaviour:

\>\>\> from gpiozero import LED, Button\
\
\# Construct a couple of devices attached to mock pins 16 and 17, and link the devices\
\>\>\> led = LED(17)\
\>\>\> btn = Button(16)\
\>\>\> led.source = btn\
\
\# Initially the button isn't "pressed" so the LED should be off\
\>\>\> led.value\
0\
\
\# Drive the pin low (this is what would happen electrically when the button is pressed)\
\>\>\> btn.pin.drive_low()\
\# The LED is now on\
\>\>\> led.value\
1\
\
\>\>\> btn.pin.drive_high()\
\# The button is now "released", so the LED should be off again\
\>\>\> led.value\
0\

Note

Setting [`source`](api_generic.html#gpiozero.SourceMixin.source "gpiozero.SourceMixin.source") starts a background thread which copies values from the source at regular intervals (every [`source_delay`](api_generic.html#gpiozero.SourceMixin.source_delay "gpiozero.SourceMixin.source_delay") seconds, 10ms by default). At the REPL, the delay between typing each line is normally enough for this to happen, but if you copy an example like the one above into a script and run it non-interactively, `led.value` may not have caught up with `btn`’s new state by the time it’s read. Add a short [`sleep()`](https://docs.python.org/3.9/library/time.html#time.sleep "(in Python v3.9)") (longer than [`source_delay`](api_generic.html#gpiozero.SourceMixin.source_delay "gpiozero.SourceMixin.source_delay")) after driving the pin if you need the change to be visible immediately.

Several sub-classes of mock pins exist for emulating various other things (pins that do/don’t support PWM, pins that are connected together, pins that drive high after a delay, etc), for example, you have to use [`MockPWMPin`](#gpiozero.pins.mock.MockPWMPin "gpiozero.pins.mock.MockPWMPin") to be able to use devices requiring PWM:

pi@raspberrypi:~ \$ GPIOZERO_PIN_FACTORY=mock GPIOZERO_MOCK_PIN_CLASS=mockpwmpin python3\

or:

from gpiozero import Device, LED\
from gpiozero.pins.mock import MockFactory, MockPWMPin\
\
Device.pin_factory = MockFactory(pin_class=MockPWMPin)\
\
led = LED(2)\

Interested users are invited to read the [GPIO Zero test suite](https://github.com/gpiozero/gpiozero/tree/master/tests) for further examples of usage.

## 24.3. Base classes[](#base-classes "Link to this heading")

class gpiozero.Factory[\[source\]](_modules/gpiozero/pins.html#Factory)[](#gpiozero.Factory "Link to this definition")  
Generates pins and SPI interfaces for devices. This is an abstract base class for pin factories. Descendents *must* override the following methods:

- [`ticks()`](#gpiozero.Factory.ticks "gpiozero.Factory.ticks")

- [`ticks_diff()`](#gpiozero.Factory.ticks_diff "gpiozero.Factory.ticks_diff")

- `_get_board_info()`

Descendents *may* override the following methods, if applicable:

- [`close()`](#gpiozero.Factory.close "gpiozero.Factory.close")

- [`reserve_pins()`](#gpiozero.Factory.reserve_pins "gpiozero.Factory.reserve_pins")

- [`release_pins()`](#gpiozero.Factory.release_pins "gpiozero.Factory.release_pins")

- [`release_all()`](#gpiozero.Factory.release_all "gpiozero.Factory.release_all")

- [`pin()`](#gpiozero.Factory.pin "gpiozero.Factory.pin")

- [`spi()`](#gpiozero.Factory.spi "gpiozero.Factory.spi")

close()[\[source\]](_modules/gpiozero/pins.html#Factory.close)[](#gpiozero.Factory.close "Link to this definition")  
Closes the pin factory. This is expected to clean up all resources manipulated by the factory. It it typically called at script termination.

pin(*name*)[\[source\]](_modules/gpiozero/pins.html#Factory.pin)[](#gpiozero.Factory.pin "Link to this definition")  
Creates an instance of a [`Pin`](#gpiozero.Pin "gpiozero.Pin") descendent representing the specified pin.

Warning

Descendents must ensure that pin instances representing the same hardware are identical; i.e. two separate invocations of [`pin()`](#gpiozero.Factory.pin "gpiozero.Factory.pin") for the same pin specification must return the same object.

release_all(*reserver*)[\[source\]](_modules/gpiozero/pins.html#Factory.release_all)[](#gpiozero.Factory.release_all "Link to this definition")  
Releases all pin reservations taken out by *reserver*. See [`release_pins()`](#gpiozero.Factory.release_pins "gpiozero.Factory.release_pins") for further information).

release_pins(*reserver*, *\*names*)[\[source\]](_modules/gpiozero/pins.html#Factory.release_pins)[](#gpiozero.Factory.release_pins "Link to this definition")  
Releases the reservation of *reserver* against pin *names*. This is typically called during [`close()`](api_generic.html#gpiozero.Device.close "gpiozero.Device.close") to clean up reservations taken during construction. Releasing a reservation that is not currently held will be silently ignored (to permit clean-up after failed / partial construction).

reserve_pins(*requester*, *\*names*)[\[source\]](_modules/gpiozero/pins.html#Factory.reserve_pins)[](#gpiozero.Factory.reserve_pins "Link to this definition")  
Called to indicate that the device reserves the right to use the specified pin *names*. This should be done during device construction. If pins are reserved, you must ensure that the reservation is released by eventually called [`release_pins()`](#gpiozero.Factory.release_pins "gpiozero.Factory.release_pins").

spi(*\*\*spi_args*)[\[source\]](_modules/gpiozero/pins.html#Factory.spi)[](#gpiozero.Factory.spi "Link to this definition")  
Returns an instance of an [`SPI`](#gpiozero.SPI "gpiozero.SPI") interface, for the specified SPI *port* and *device*, or for the specified pins (*clock_pin*, *mosi_pin*, *miso_pin*, and *select_pin*). Only one of the schemes can be used; attempting to mix *port* and *device* with pin numbers will raise [`SPIBadArgs`](api_exc.html#gpiozero.SPIBadArgs "gpiozero.SPIBadArgs").

ticks()[\[source\]](_modules/gpiozero/pins.html#Factory.ticks)[](#gpiozero.Factory.ticks "Link to this definition")  
Return the current ticks, according to the factory. The reference point is undefined and thus the result of this method is only meaningful when compared to another value returned by this method.

The format of the time is also arbitrary, as is whether the time wraps after a certain duration. Ticks should only be compared using the [`ticks_diff()`](#gpiozero.Factory.ticks_diff "gpiozero.Factory.ticks_diff") method.

ticks_diff(*later*, *earlier*)[\[source\]](_modules/gpiozero/pins.html#Factory.ticks_diff)[](#gpiozero.Factory.ticks_diff "Link to this definition")  
Return the time in seconds between two [`ticks()`](#gpiozero.Factory.ticks "gpiozero.Factory.ticks") results. The arguments are specified in the same order as they would be in the formula *later* - *earlier* but the result is guaranteed to be in seconds, and to be positive even if the ticks “wrapped” between calls to [`ticks()`](#gpiozero.Factory.ticks "gpiozero.Factory.ticks").

property board_info[](#gpiozero.Factory.board_info "Link to this definition")  
Returns a `BoardInfo` instance (or derivative) representing the board that instances generated by this factory will be attached to.

&nbsp;

class gpiozero.Pin[\[source\]](_modules/gpiozero/pins.html#Pin)[](#gpiozero.Pin "Link to this definition")  
Abstract base class representing a pin attached to some form of controller, be it GPIO, SPI, ADC, etc.

Descendents should override property getters and setters to accurately represent the capabilities of pins. Descendents *must* override the following methods:

- `_get_info()`

- `_get_function()`

- `_set_function()`

- `_get_state()`

Descendents *may* additionally override the following methods, if applicable:

- [`close()`](#gpiozero.Pin.close "gpiozero.Pin.close")

- [`output_with_state()`](#gpiozero.Pin.output_with_state "gpiozero.Pin.output_with_state")

- [`input_with_pull()`](#gpiozero.Pin.input_with_pull "gpiozero.Pin.input_with_pull")

- `_set_state()`

- `_get_frequency()`

- `_set_frequency()`

- `_get_pull()`

- `_set_pull()`

- `_get_bounce()`

- `_set_bounce()`

- `_get_edges()`

- `_set_edges()`

- `_get_when_changed()`

- `_set_when_changed()`

close()[\[source\]](_modules/gpiozero/pins.html#Pin.close)[](#gpiozero.Pin.close "Link to this definition")  
Cleans up the resources allocated to the pin. After this method is called, this [`Pin`](#gpiozero.Pin "gpiozero.Pin") instance may no longer be used to query or control the pin’s state.

input_with_pull(*pull*)[\[source\]](_modules/gpiozero/pins.html#Pin.input_with_pull)[](#gpiozero.Pin.input_with_pull "Link to this definition")  
Sets the pin’s function to “input” and specifies an initial pull-up for the pin. By default this is equivalent to performing:

pin.function = 'input'\
pin.pull = pull\

However, descendents may override this in order to provide the smallest possible delay between configuring the pin for input and pulling the pin up/down (which can be important for avoiding “blips” in some configurations).

output_with_state(*state*)[\[source\]](_modules/gpiozero/pins.html#Pin.output_with_state)[](#gpiozero.Pin.output_with_state "Link to this definition")  
Sets the pin’s function to “output” and specifies an initial state for the pin. By default this is equivalent to performing:

pin.function = 'output'\
pin.state = state\

However, descendents may override this in order to provide the smallest possible delay between configuring the pin for output and specifying an initial value (which can be important for avoiding “blips” in active-low configurations).

property bounce[](#gpiozero.Pin.bounce "Link to this definition")  
The amount of bounce detection (elimination) currently in use by edge detection, measured in seconds. If bounce detection is not currently in use, this is [`None`](https://docs.python.org/3.9/library/constants.html#None "(in Python v3.9)").

For example, if [`edges`](#gpiozero.Pin.edges "gpiozero.Pin.edges") is currently “rising”, [`bounce`](#gpiozero.Pin.bounce "gpiozero.Pin.bounce") is currently 5/1000 (5ms), then the waveform below will only fire [`when_changed`](#gpiozero.Pin.when_changed "gpiozero.Pin.when_changed") on two occasions despite there being three rising edges:

TIME 0...1...2...3...4...5...6...7...8...9...10..11..12 ms\
\
bounce elimination   \|===================\| \|==============\
\
HIGH - - - - \>       ,--. ,--------------. ,--.\
                     \|  \| \|              \| \|  \|\
                     \|  \| \|              \| \|  \|\
LOW  ----------------'  \`-'              \`-'  \`-----------\
                     :                     :\
                     :                     :\
               when_changed          when_changed\
                   fires                 fires\

If the pin does not support edge detection, attempts to set this property will raise [`PinEdgeDetectUnsupported`](api_exc.html#gpiozero.PinEdgeDetectUnsupported "gpiozero.PinEdgeDetectUnsupported"). If the pin supports edge detection, the class must implement bounce detection, even if only in software.

property edges[](#gpiozero.Pin.edges "Link to this definition")  
The edge that will trigger execution of the function or bound method assigned to [`when_changed`](#gpiozero.Pin.when_changed "gpiozero.Pin.when_changed"). This can be one of the strings “both” (the default), “rising”, “falling”, or “none”:

HIGH - - - - \>           ,--------------.\
                         \|              \|\
                         \|              \|\
LOW  --------------------'              \`--------------\
                         :              :\
                         :              :\
Fires when_changed     "both"         "both"\
when edges is ...     "rising"       "falling"\

If the pin does not support edge detection, attempts to set this property will raise [`PinEdgeDetectUnsupported`](api_exc.html#gpiozero.PinEdgeDetectUnsupported "gpiozero.PinEdgeDetectUnsupported").

property frequency[](#gpiozero.Pin.frequency "Link to this definition")  
The frequency (in Hz) for the pin’s PWM implementation, or [`None`](https://docs.python.org/3.9/library/constants.html#None "(in Python v3.9)") if PWM is not currently in use. This value always defaults to [`None`](https://docs.python.org/3.9/library/constants.html#None "(in Python v3.9)") and may be changed with certain pin types to activate or deactivate PWM.

If the pin does not support PWM, [`PinPWMUnsupported`](api_exc.html#gpiozero.PinPWMUnsupported "gpiozero.PinPWMUnsupported") will be raised when attempting to set this to a value other than [`None`](https://docs.python.org/3.9/library/constants.html#None "(in Python v3.9)").

property function[](#gpiozero.Pin.function "Link to this definition")  
The function of the pin. This property is a string indicating the current function or purpose of the pin. Typically this is the string “input” or “output”. However, in some circumstances it can be other strings indicating non-GPIO related functionality.

With certain pin types (e.g. GPIO pins), this attribute can be changed to configure the function of a pin. If an invalid function is specified, for this attribute, [`PinInvalidFunction`](api_exc.html#gpiozero.PinInvalidFunction "gpiozero.PinInvalidFunction") will be raised.

property info[](#gpiozero.Pin.info "Link to this definition")  
Returns the [`PinInfo`](api_info.html#gpiozero.PinInfo "gpiozero.PinInfo") associated with the pin. This can be used to determine physical properties of the pin, including its location on the header, fixed pulls, and the various specs that can be used to identify it.

property pull[](#gpiozero.Pin.pull "Link to this definition")  
The pull-up state of the pin represented as a string. This is typically one of the strings “up”, “down”, or “floating” but additional values may be supported by the underlying hardware.

If the pin does not support changing pull-up state (for example because of a fixed pull-up resistor), attempts to set this property will raise [`PinFixedPull`](api_exc.html#gpiozero.PinFixedPull "gpiozero.PinFixedPull"). If the specified value is not supported by the underlying hardware, [`PinInvalidPull`](api_exc.html#gpiozero.PinInvalidPull "gpiozero.PinInvalidPull") is raised.

property state[](#gpiozero.Pin.state "Link to this definition")  
The state of the pin. This is 0 for low, and 1 for high. As a low level view of the pin, no swapping is performed in the case of pull ups (see [`pull`](#gpiozero.Pin.pull "gpiozero.Pin.pull") for more information):

HIGH - - - - \>       ,----------------------\
                     \|\
                     \|\
LOW  ----------------'\

Descendents which implement analog, or analog-like capabilities can return values between 0 and 1. For example, pins implementing PWM (where [`frequency`](#gpiozero.Pin.frequency "gpiozero.Pin.frequency") is not [`None`](https://docs.python.org/3.9/library/constants.html#None "(in Python v3.9)")) return a value between 0.0 and 1.0 representing the current PWM duty cycle.

If a pin is currently configured for input, and an attempt is made to set this attribute, [`PinSetInput`](api_exc.html#gpiozero.PinSetInput "gpiozero.PinSetInput") will be raised. If an invalid value is specified for this attribute, [`PinInvalidState`](api_exc.html#gpiozero.PinInvalidState "gpiozero.PinInvalidState") will be raised.

property when_changed[](#gpiozero.Pin.when_changed "Link to this definition")  
A function or bound method to be called when the pin’s state changes (more specifically when the edge specified by [`edges`](#gpiozero.Pin.edges "gpiozero.Pin.edges") is detected on the pin). The function or bound method must accept two parameters: the first will report the ticks (from [`Factory.ticks()`](#gpiozero.Factory.ticks "gpiozero.Factory.ticks")) when the pin’s state changed, and the second will report the pin’s current state.

Warning

Depending on hardware support, the state is *not guaranteed to be accurate*. For instance, many GPIO implementations will provide an interrupt indicating when a pin’s state changed but not what it changed to. In this case the pin driver simply reads the pin’s current state to supply this parameter, but the pin’s state may have changed *since* the interrupt. Exercise appropriate caution when relying upon this parameter.

If the pin does not support edge detection, attempts to set this property will raise [`PinEdgeDetectUnsupported`](api_exc.html#gpiozero.PinEdgeDetectUnsupported "gpiozero.PinEdgeDetectUnsupported").

&nbsp;

class gpiozero.SPI(*\*args*, *\*\*kwargs*)[\[source\]](_modules/gpiozero/pins.html#SPI)[](#gpiozero.SPI "Link to this definition")  
Abstract interface for [Serial Peripheral Interface](https://en.wikipedia.org/wiki/Serial_Peripheral_Interface_Bus) (SPI) implementations. Descendents *must* override the following methods:

- [`transfer()`](#gpiozero.SPI.transfer "gpiozero.SPI.transfer")

- `_get_clock_mode()`

Descendents *may* override the following methods, if applicable:

- [`read()`](#gpiozero.SPI.read "gpiozero.SPI.read")

- [`write()`](#gpiozero.SPI.write "gpiozero.SPI.write")

- `_set_clock_mode()`

- `_get_lsb_first()`

- `_set_lsb_first()`

- `_get_select_high()`

- `_set_select_high()`

- `_get_bits_per_word()`

- `_set_bits_per_word()`

read(*n*)[\[source\]](_modules/gpiozero/pins.html#SPI.read)[](#gpiozero.SPI.read "Link to this definition")  
Read *n* words of data from the SPI interface, returning them as a sequence of unsigned ints, each no larger than the configured [`bits_per_word`](#gpiozero.SPI.bits_per_word "gpiozero.SPI.bits_per_word") of the interface.

This method is typically used with read-only devices that feature half-duplex communication. See [`transfer()`](#gpiozero.SPI.transfer "gpiozero.SPI.transfer") for full duplex communication.

transfer(*data*)[\[source\]](_modules/gpiozero/pins.html#SPI.transfer)[](#gpiozero.SPI.transfer "Link to this definition")  
Write *data* to the SPI interface. *data* must be a sequence of unsigned integer words each of which will fit within the configured [`bits_per_word`](#gpiozero.SPI.bits_per_word "gpiozero.SPI.bits_per_word") of the interface. The method returns the sequence of words read from the interface while writing occurred (full duplex communication).

The length of the sequence returned dictates the number of words of *data* written to the interface. Each word in the returned sequence will be an unsigned integer no larger than the configured [`bits_per_word`](#gpiozero.SPI.bits_per_word "gpiozero.SPI.bits_per_word") of the interface.

write(*data*)[\[source\]](_modules/gpiozero/pins.html#SPI.write)[](#gpiozero.SPI.write "Link to this definition")  
Write *data* to the SPI interface. *data* must be a sequence of unsigned integer words each of which will fit within the configured [`bits_per_word`](#gpiozero.SPI.bits_per_word "gpiozero.SPI.bits_per_word") of the interface. The method returns the number of words written to the interface (which may be less than or equal to the length of *data*).

This method is typically used with write-only devices that feature half-duplex communication. See [`transfer()`](#gpiozero.SPI.transfer "gpiozero.SPI.transfer") for full duplex communication.

property bits_per_word[](#gpiozero.SPI.bits_per_word "Link to this definition")  
Controls the number of bits that make up a word, and thus where the word boundaries appear in the data stream, and the maximum value of a word. Defaults to 8 meaning that words are effectively bytes.

Several implementations do not support non-byte-sized words.

property clock_mode[](#gpiozero.SPI.clock_mode "Link to this definition")  
Presents a value representing the [`clock_polarity`](#gpiozero.SPI.clock_polarity "gpiozero.SPI.clock_polarity") and [`clock_phase`](#gpiozero.SPI.clock_phase "gpiozero.SPI.clock_phase") attributes combined according to the following table:

| mode | polarity (CPOL) | phase (CPHA) |
|------|-----------------|--------------|
| 0    | False           | False        |
| 1    | False           | True         |
| 2    | True            | False        |
| 3    | True            | True         |

Adjusting this value adjusts both the [`clock_polarity`](#gpiozero.SPI.clock_polarity "gpiozero.SPI.clock_polarity") and [`clock_phase`](#gpiozero.SPI.clock_phase "gpiozero.SPI.clock_phase") attributes simultaneously.

property clock_phase[](#gpiozero.SPI.clock_phase "Link to this definition")  
The phase of the SPI clock pin. If this is [`False`](https://docs.python.org/3.9/library/constants.html#False "(in Python v3.9)") (the default), data will be read from the MISO pin when the clock pin activates. Setting this to [`True`](https://docs.python.org/3.9/library/constants.html#True "(in Python v3.9)") will cause data to be read from the MISO pin when the clock pin deactivates. On many data sheets this is documented as the CPHA value. Whether the clock edge is rising or falling when the clock is considered activated is controlled by the [`clock_polarity`](#gpiozero.SPI.clock_polarity "gpiozero.SPI.clock_polarity") attribute (corresponding to CPOL).

The following diagram indicates when data is read when [`clock_polarity`](#gpiozero.SPI.clock_polarity "gpiozero.SPI.clock_polarity") is [`False`](https://docs.python.org/3.9/library/constants.html#False "(in Python v3.9)"), and [`clock_phase`](#gpiozero.SPI.clock_phase "gpiozero.SPI.clock_phase") is [`False`](https://docs.python.org/3.9/library/constants.html#False "(in Python v3.9)") (the default), equivalent to CPHA 0:

    ,---.   ,---.   ,---.   ,---.   ,---.   ,---.   ,---.\
CLK \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|\
    \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|\
----'   \`---'   \`---'   \`---'   \`---'   \`---'   \`---'   \`-------\
    :       :       :       :       :       :       :\
MISO---.   ,---.   ,---.   ,---.   ,---.   ,---.   ,---.\
  /     \\/     \\/     \\/     \\/     \\/     \\/     \\\
-{  Bit  X  Bit  X  Bit  X  Bit  X  Bit  X  Bit  X  Bit  }------\
  \\    / \\    / \\    / \\    / \\    / \\    / \\    /\
   \`---'   \`---'   \`---'   \`---'   \`---'   \`---'   \`---'\

The following diagram indicates when data is read when [`clock_polarity`](#gpiozero.SPI.clock_polarity "gpiozero.SPI.clock_polarity") is [`False`](https://docs.python.org/3.9/library/constants.html#False "(in Python v3.9)"), but [`clock_phase`](#gpiozero.SPI.clock_phase "gpiozero.SPI.clock_phase") is [`True`](https://docs.python.org/3.9/library/constants.html#True "(in Python v3.9)"), equivalent to CPHA 1:

    ,---.   ,---.   ,---.   ,---.   ,---.   ,---.   ,---.\
CLK \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|\
    \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|\
----'   \`---'   \`---'   \`---'   \`---'   \`---'   \`---'   \`-------\
        :       :       :       :       :       :       :\
MISO   ,---.   ,---.   ,---.   ,---.   ,---.   ,---.   ,---.\
      /     \\/     \\/     \\/     \\/     \\/     \\/     \\\
-----{  Bit  X  Bit  X  Bit  X  Bit  X  Bit  X  Bit  X  Bit  }--\
      \\    / \\    / \\    / \\    / \\    / \\    / \\    /\
       \`---'   \`---'   \`---'   \`---'   \`---'   \`---'   \`---'\

property clock_polarity[](#gpiozero.SPI.clock_polarity "Link to this definition")  
The polarity of the SPI clock pin. If this is [`False`](https://docs.python.org/3.9/library/constants.html#False "(in Python v3.9)") (the default), the clock pin will idle low, and pulse high. Setting this to [`True`](https://docs.python.org/3.9/library/constants.html#True "(in Python v3.9)") will cause the clock pin to idle high, and pulse low. On many data sheets this is documented as the CPOL value.

The following diagram illustrates the waveform when [`clock_polarity`](#gpiozero.SPI.clock_polarity "gpiozero.SPI.clock_polarity") is [`False`](https://docs.python.org/3.9/library/constants.html#False "(in Python v3.9)") (the default), equivalent to CPOL 0:

       on      on      on      on      on      on      on\
      ,---.   ,---.   ,---.   ,---.   ,---.   ,---.   ,---.\
CLK   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|\
      \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|\
------'   \`---'   \`---'   \`---'   \`---'   \`---'   \`---'   \`------\
idle       off     off     off     off     off     off       idle\

The following diagram illustrates the waveform when [`clock_polarity`](#gpiozero.SPI.clock_polarity "gpiozero.SPI.clock_polarity") is [`True`](https://docs.python.org/3.9/library/constants.html#True "(in Python v3.9)"), equivalent to CPOL 1:

idle       off     off     off     off     off     off       idle\
------.   ,---.   ,---.   ,---.   ,---.   ,---.   ,---.   ,------\
      \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|\
CLK   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|\
      \`---'   \`---'   \`---'   \`---'   \`---'   \`---'   \`---'\
       on      on      on      on      on      on      on\

property lsb_first[](#gpiozero.SPI.lsb_first "Link to this definition")  
Controls whether words are read and written LSB in (Least Significant Bit first) order. The default is [`False`](https://docs.python.org/3.9/library/constants.html#False "(in Python v3.9)") indicating that words are read and written in MSB (Most Significant Bit first) order. Effectively, this controls the [Bit endianness](https://en.wikipedia.org/wiki/Endianness#Bit_endianness) of the connection.

The following diagram shows the a word containing the number 5 (binary 0101) transmitted on MISO with [`bits_per_word`](#gpiozero.SPI.bits_per_word "gpiozero.SPI.bits_per_word") set to 4, and [`clock_mode`](#gpiozero.SPI.clock_mode "gpiozero.SPI.clock_mode") set to 0, when [`lsb_first`](#gpiozero.SPI.lsb_first "gpiozero.SPI.lsb_first") is [`False`](https://docs.python.org/3.9/library/constants.html#False "(in Python v3.9)") (the default):

    ,---.   ,---.   ,---.   ,---.\
CLK \|   \|   \|   \|   \|   \|   \|   \|\
    \|   \|   \|   \|   \|   \|   \|   \|\
----'   \`---'   \`---'   \`---'   \`-----\
    :     ,-------. :     ,-------.\
MISO:     \| :     \| :     \| :     \|\
    :     \| :     \| :     \| :     \|\
----------' :     \`-------' :     \`----\
    :       :       :       :\
   MSB                     LSB\

And now with [`lsb_first`](#gpiozero.SPI.lsb_first "gpiozero.SPI.lsb_first") set to [`True`](https://docs.python.org/3.9/library/constants.html#True "(in Python v3.9)") (and all other parameters the same):

    ,---.   ,---.   ,---.   ,---.\
CLK \|   \|   \|   \|   \|   \|   \|   \|\
    \|   \|   \|   \|   \|   \|   \|   \|\
----'   \`---'   \`---'   \`---'   \`-----\
  ,-------. :     ,-------. :\
MISO:     \| :     \| :     \| :\
  \| :     \| :     \| :     \| :\
--' :     \`-------' :     \`-----------\
    :       :       :       :\
   LSB                     MSB\

property rate[](#gpiozero.SPI.rate "Link to this definition")  
Controls the speed of the SPI interface in Hz (or baud).

Note that most software SPI implementations ignore this property, and will raise `SPIFixedRate` if an attempt is made to set it, as they have no rate control (they simply bit-bang as fast as possible because typically this isn’t very fast anyway, and introducing measures to limit the rate would simply slow them down to the point of being useless).

property select_high[](#gpiozero.SPI.select_high "Link to this definition")  
If [`False`](https://docs.python.org/3.9/library/constants.html#False "(in Python v3.9)") (the default), the chip select line is considered active when it is pulled low. When set to [`True`](https://docs.python.org/3.9/library/constants.html#True "(in Python v3.9)"), the chip select line is considered active when it is driven high.

The following diagram shows the waveform of the chip select line, and the clock when [`clock_polarity`](#gpiozero.SPI.clock_polarity "gpiozero.SPI.clock_polarity") is [`False`](https://docs.python.org/3.9/library/constants.html#False "(in Python v3.9)"), and [`select_high`](#gpiozero.SPI.select_high "gpiozero.SPI.select_high") is [`False`](https://docs.python.org/3.9/library/constants.html#False "(in Python v3.9)") (the default):

---.                                                     ,------\
\_\_ \|                                                     \|\
CS \|      chip is selected, and will react to clock      \|  idle\
   \`-----------------------------------------------------'\
\
    ,---.   ,---.   ,---.   ,---.   ,---.   ,---.   ,---.\
CLK \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|\
    \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|\
----'   \`---'   \`---'   \`---'   \`---'   \`---'   \`---'   \`-------\

And when [`select_high`](#gpiozero.SPI.select_high "gpiozero.SPI.select_high") is [`True`](https://docs.python.org/3.9/library/constants.html#True "(in Python v3.9)"):

   ,-----------------------------------------------------.\
CS \|      chip is selected, and will react to clock      \|  idle\
   \|                                                     \|\
---'                                                     \`------\
\
    ,---.   ,---.   ,---.   ,---.   ,---.   ,---.   ,---.\
CLK \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|\
    \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|   \|\
----'   \`---'   \`---'   \`---'   \`---'   \`---'   \`---'   \`-------\

&nbsp;

class gpiozero.pins.pi.PiFactory[\[source\]](_modules/gpiozero/pins/pi.html#PiFactory)[](#gpiozero.pins.pi.PiFactory "Link to this definition")  
Extends [`Factory`](#gpiozero.Factory "gpiozero.Factory"). Abstract base class representing hardware attached to a Raspberry Pi. This forms the base of [`LocalPiFactory`](#gpiozero.pins.local.LocalPiFactory "gpiozero.pins.local.LocalPiFactory").

close()[\[source\]](_modules/gpiozero/pins/pi.html#PiFactory.close)[](#gpiozero.pins.pi.PiFactory.close "Link to this definition")  
Closes the pin factory. This is expected to clean up all resources manipulated by the factory. It it typically called at script termination.

pin(*name*)[\[source\]](_modules/gpiozero/pins/pi.html#PiFactory.pin)[](#gpiozero.pins.pi.PiFactory.pin "Link to this definition")  
Creates an instance of a `Pin` descendent representing the specified pin.

Warning

Descendents must ensure that pin instances representing the same hardware are identical; i.e. two separate invocations of [`pin()`](#gpiozero.pins.pi.PiFactory.pin "gpiozero.pins.pi.PiFactory.pin") for the same pin specification must return the same object.

spi(*\*\*spi_args*)[\[source\]](_modules/gpiozero/pins/pi.html#PiFactory.spi)[](#gpiozero.pins.pi.PiFactory.spi "Link to this definition")  
Returns an SPI interface, for the specified SPI *port* and *device*, or for the specified pins (*clock_pin*, *mosi_pin*, *miso_pin*, and *select_pin*). Only one of the schemes can be used; attempting to mix *port* and *device* with pin numbers will raise [`SPIBadArgs`](api_exc.html#gpiozero.SPIBadArgs "gpiozero.SPIBadArgs").

If the pins specified match the hardware SPI pins (clock on GPIO11, MOSI on GPIO10, MISO on GPIO9, and chip select on GPIO8 or GPIO7), and the spidev module can be imported, a hardware based interface (using spidev) will be returned. Otherwise, a software based interface will be returned which will use simple bit-banging to communicate.

Both interfaces have the same API, support clock polarity and phase attributes, and can handle half and full duplex communications, but the hardware interface is significantly faster (though for many simpler devices this doesn’t matter).

&nbsp;

class gpiozero.pins.pi.PiPin(*factory*, *info*)[\[source\]](_modules/gpiozero/pins/pi.html#PiPin)[](#gpiozero.pins.pi.PiPin "Link to this definition")  
Extends [`Pin`](#gpiozero.Pin "gpiozero.Pin"). Abstract base class representing a multi-function GPIO pin attached to a Raspberry Pi. Descendents *must* override the following methods:

- `_get_function()`

- `_set_function()`

- `_get_state()`

- `_call_when_changed()`

- `_enable_event_detect()`

- `_disable_event_detect()`

Descendents *may* additionally override the following methods, if applicable:

- `close()`

- `output_with_state()`

- `input_with_pull()`

- `_set_state()`

- `_get_frequency()`

- `_set_frequency()`

- `_get_pull()`

- `_set_pull()`

- `_get_bounce()`

- `_set_bounce()`

- `_get_edges()`

- `_set_edges()`

property info[](#gpiozero.pins.pi.PiPin.info "Link to this definition")  
Returns the `PinInfo` associated with the pin. This can be used to determine physical properties of the pin, including its location on the header, fixed pulls, and the various specs that can be used to identify it.

&nbsp;

class gpiozero.pins.local.LocalPiFactory[\[source\]](_modules/gpiozero/pins/local.html#LocalPiFactory)[](#gpiozero.pins.local.LocalPiFactory "Link to this definition")  
Extends [`PiFactory`](#gpiozero.pins.pi.PiFactory "gpiozero.pins.pi.PiFactory"). Abstract base class representing pins attached locally to a Pi. This forms the base class for local-only pin interfaces ([`RPiGPIOPin`](#gpiozero.pins.rpigpio.RPiGPIOPin "gpiozero.pins.rpigpio.RPiGPIOPin"), [`LGPIOPin`](#gpiozero.pins.lgpio.LGPIOPin "gpiozero.pins.lgpio.LGPIOPin"), and [`NativePin`](#gpiozero.pins.native.NativePin "gpiozero.pins.native.NativePin")).

static ticks()[\[source\]](_modules/gpiozero/pins/local.html#LocalPiFactory.ticks)[](#gpiozero.pins.local.LocalPiFactory.ticks "Link to this definition")  
Return the current ticks, according to the factory. The reference point is undefined and thus the result of this method is only meaningful when compared to another value returned by this method.

The format of the time is also arbitrary, as is whether the time wraps after a certain duration. Ticks should only be compared using the [`ticks_diff()`](#gpiozero.pins.local.LocalPiFactory.ticks_diff "gpiozero.pins.local.LocalPiFactory.ticks_diff") method.

static ticks_diff(*later*, *earlier*)[\[source\]](_modules/gpiozero/pins/local.html#LocalPiFactory.ticks_diff)[](#gpiozero.pins.local.LocalPiFactory.ticks_diff "Link to this definition")  
Return the time in seconds between two [`ticks()`](#gpiozero.pins.local.LocalPiFactory.ticks "gpiozero.pins.local.LocalPiFactory.ticks") results. The arguments are specified in the same order as they would be in the formula *later* - *earlier* but the result is guaranteed to be in seconds, and to be positive even if the ticks “wrapped” between calls to [`ticks()`](#gpiozero.pins.local.LocalPiFactory.ticks "gpiozero.pins.local.LocalPiFactory.ticks").

&nbsp;

class gpiozero.pins.local.LocalPiPin(*factory*, *info*)[\[source\]](_modules/gpiozero/pins/local.html#LocalPiPin)[](#gpiozero.pins.local.LocalPiPin "Link to this definition")  
Extends [`PiPin`](#gpiozero.pins.pi.PiPin "gpiozero.pins.pi.PiPin"). Abstract base class representing a multi-function GPIO pin attached to the local Raspberry Pi.

## 24.4. RPi.GPIO[](#module-gpiozero.pins.rpigpio "Link to this heading")

class gpiozero.pins.rpigpio.RPiGPIOFactory[\[source\]](_modules/gpiozero/pins/rpigpio.html#RPiGPIOFactory)[](#gpiozero.pins.rpigpio.RPiGPIOFactory "Link to this definition")  
Extends [`LocalPiFactory`](#gpiozero.pins.local.LocalPiFactory "gpiozero.pins.local.LocalPiFactory"). Uses the [RPi.GPIO](https://pypi.org/project/RPi.GPIO) library to interface to the Pi’s GPIO pins. This is the default pin implementation if the RPi.GPIO library is installed. Supports all features including PWM (via software).

Because this is the default pin implementation you can use it simply by specifying an integer number for the pin in most operations, e.g.:

from gpiozero import LED\
\
led = LED(12)\

However, you can also construct RPi.GPIO pins manually if you wish:

from gpiozero.pins.rpigpio import RPiGPIOFactory\
from gpiozero import LED\
\
factory = RPiGPIOFactory()\
led = LED(12, pin_factory=factory)\

&nbsp;

class gpiozero.pins.rpigpio.RPiGPIOPin(*factory*, *info*)[\[source\]](_modules/gpiozero/pins/rpigpio.html#RPiGPIOPin)[](#gpiozero.pins.rpigpio.RPiGPIOPin "Link to this definition")  
Extends [`LocalPiPin`](#gpiozero.pins.local.LocalPiPin "gpiozero.pins.local.LocalPiPin"). Pin implementation for the [RPi.GPIO](https://pypi.org/project/RPi.GPIO) library. See [`RPiGPIOFactory`](#gpiozero.pins.rpigpio.RPiGPIOFactory "gpiozero.pins.rpigpio.RPiGPIOFactory") for more information.

## 24.5. lgpio[](#module-gpiozero.pins.lgpio "Link to this heading")

class gpiozero.pins.lgpio.LGPIOFactory(*chip=None*)[\[source\]](_modules/gpiozero/pins/lgpio.html#LGPIOFactory)[](#gpiozero.pins.lgpio.LGPIOFactory "Link to this definition")  
Extends [`LocalPiFactory`](#gpiozero.pins.local.LocalPiFactory "gpiozero.pins.local.LocalPiFactory"). Uses the [lgpio](http://abyz.me.uk/lg/py_lgpio.html) library to interface to the local computer’s GPIO pins. The lgpio library simply talks to Linux gpiochip devices; it is not specific to the Raspberry Pi although this class is currently constructed under the assumption that it is running on a Raspberry Pi.

You can construct lgpio pins manually like so:

from gpiozero.pins.lgpio import LGPIOFactory\
from gpiozero import LED\
\
factory = LGPIOFactory(chip=0)\
led = LED(12, pin_factory=factory)\

The *chip* parameter to the factory constructor specifies which gpiochip device to attempt to open. It defaults to 0 and thus doesn’t normally need to be specified (the example above only includes it for completeness).

The lgpio library relies on access to the `/dev/gpiochip*` devices. If you run into issues, please check that your user has read/write access to the specific gpiochip device you are attempting to open (0 by default).

&nbsp;

class gpiozero.pins.lgpio.LGPIOPin(*factory*, *info*)[\[source\]](_modules/gpiozero/pins/lgpio.html#LGPIOPin)[](#gpiozero.pins.lgpio.LGPIOPin "Link to this definition")  
Extends [`LocalPiPin`](#gpiozero.pins.local.LocalPiPin "gpiozero.pins.local.LocalPiPin"). Pin implementation for the [lgpio](http://abyz.me.uk/lg/py_lgpio.html) library. See [`LGPIOFactory`](#gpiozero.pins.lgpio.LGPIOFactory "gpiozero.pins.lgpio.LGPIOFactory") for more information.

## 24.6. PiGPIO[](#module-gpiozero.pins.pigpio "Link to this heading")

class gpiozero.pins.pigpio.PiGPIOFactory(*host=None*, *port=None*)[\[source\]](_modules/gpiozero/pins/pigpio.html#PiGPIOFactory)[](#gpiozero.pins.pigpio.PiGPIOFactory "Link to this definition")  
Extends [`PiFactory`](#gpiozero.pins.pi.PiFactory "gpiozero.pins.pi.PiFactory"). Uses the [pigpio](http://abyz.me.uk/rpi/pigpio/) library to interface to the Pi’s GPIO pins. The pigpio library relies on a daemon (**pigpiod**) to be running as root to provide access to the GPIO pins, and communicates with this daemon over a network socket.

While this does mean only the daemon itself should control the pins, the architecture does have several advantages:

- Pins can be remote controlled from another machine (the other machine doesn’t even have to be a Raspberry Pi; it simply needs the [pigpio](http://abyz.me.uk/rpi/pigpio/) client library installed on it)

- The daemon supports hardware PWM via the DMA controller

- Your script itself doesn’t require root privileges; it just needs to be able to communicate with the daemon

You can construct pigpio pins manually like so:

from gpiozero.pins.pigpio import PiGPIOFactory\
from gpiozero import LED\
\
factory = PiGPIOFactory()\
led = LED(12, pin_factory=factory)\

This is particularly useful for controlling pins on a remote machine. To accomplish this simply specify the host (and optionally port) when constructing the pin:

from gpiozero.pins.pigpio import PiGPIOFactory\
from gpiozero import LED\
\
factory = PiGPIOFactory(host='192.168.0.2')\
led = LED(12, pin_factory=factory)\

Note

In some circumstances, especially when playing with PWM, it does appear to be possible to get the daemon into “unusual” states. We would be most interested to hear any bug reports relating to this (it may be a bug in our pin implementation). A workaround for now is simply to restart the **pigpiod** daemon.

&nbsp;

class gpiozero.pins.pigpio.PiGPIOPin(*factory*, *info*)[\[source\]](_modules/gpiozero/pins/pigpio.html#PiGPIOPin)[](#gpiozero.pins.pigpio.PiGPIOPin "Link to this definition")  
Extends [`PiPin`](#gpiozero.pins.pi.PiPin "gpiozero.pins.pi.PiPin"). Pin implementation for the [pigpio](http://abyz.me.uk/rpi/pigpio/) library. See [`PiGPIOFactory`](#gpiozero.pins.pigpio.PiGPIOFactory "gpiozero.pins.pigpio.PiGPIOFactory") for more information.

## 24.7. Native[](#module-gpiozero.pins.native "Link to this heading")

class gpiozero.pins.native.NativeFactory[\[source\]](_modules/gpiozero/pins/native.html#NativeFactory)[](#gpiozero.pins.native.NativeFactory "Link to this definition")  
Extends [`LocalPiFactory`](#gpiozero.pins.local.LocalPiFactory "gpiozero.pins.local.LocalPiFactory"). Uses a built-in pure Python implementation to interface to the Pi’s GPIO pins. This is the default pin implementation if no third-party libraries are discovered.

Warning

This implementation does *not* currently support PWM. Attempting to use any class which requests PWM will raise an exception.

You can construct native pin instances manually like so:

from gpiozero.pins.native import NativeFactory\
from gpiozero import LED\
\
factory = NativeFactory()\
led = LED(12, pin_factory=factory)\

&nbsp;

class gpiozero.pins.native.NativePin(*factory*, *info*)[\[source\]](_modules/gpiozero/pins/native.html#NativePin)[](#gpiozero.pins.native.NativePin "Link to this definition")  
Extends [`LocalPiPin`](#gpiozero.pins.local.LocalPiPin "gpiozero.pins.local.LocalPiPin"). Native pin implementation. See [`NativeFactory`](#gpiozero.pins.native.NativeFactory "gpiozero.pins.native.NativeFactory") for more information.

&nbsp;

class gpiozero.pins.native.Native2835Pin(*factory*, *info*)[\[source\]](_modules/gpiozero/pins/native.html#Native2835Pin)[](#gpiozero.pins.native.Native2835Pin "Link to this definition")  
Extends [`NativePin`](#gpiozero.pins.native.NativePin "gpiozero.pins.native.NativePin") for Pi hardware prior to the Pi 4 (Pi 0, 1, 2, 3, and 3+).

&nbsp;

class gpiozero.pins.native.Native2711Pin(*factory*, *info*)[\[source\]](_modules/gpiozero/pins/native.html#Native2711Pin)[](#gpiozero.pins.native.Native2711Pin "Link to this definition")  
Extends [`NativePin`](#gpiozero.pins.native.NativePin "gpiozero.pins.native.NativePin") for Pi 4 hardware (Pi 4, CM4, Pi 400 at the time of writing).

## 24.8. Mock[](#module-gpiozero.pins.mock "Link to this heading")

class gpiozero.pins.mock.MockFactory(*revision=None*, *pin_class=None*)[\[source\]](_modules/gpiozero/pins/mock.html#MockFactory)[](#gpiozero.pins.mock.MockFactory "Link to this definition")  
Factory for generating mock pins.

The *revision* parameter specifies what revision of Pi the mock factory pretends to be (this affects the result of the `Factory.board_info` attribute as well as where pull-ups are assumed to be).

The *pin_class* attribute specifies which mock pin class will be generated by the [`pin()`](#gpiozero.pins.mock.MockFactory.pin "gpiozero.pins.mock.MockFactory.pin") method by default. This can be changed after construction by modifying the [`pin_class`](#gpiozero.pins.mock.MockFactory.pin_class "gpiozero.pins.mock.MockFactory.pin_class") attribute.

pin_class[](#gpiozero.pins.mock.MockFactory.pin_class "Link to this definition")  
This attribute stores the [`MockPin`](#gpiozero.pins.mock.MockPin "gpiozero.pins.mock.MockPin") class (or descendant) that will be used when constructing pins with the [`pin()`](#gpiozero.pins.mock.MockFactory.pin "gpiozero.pins.mock.MockFactory.pin") method (if no *pin_class* parameter is used to override it). It defaults on construction to the value of the *pin_class* parameter in the constructor, or [`MockPin`](#gpiozero.pins.mock.MockPin "gpiozero.pins.mock.MockPin") if that is unspecified.

static ticks()[\[source\]](_modules/gpiozero/pins/mock.html#MockFactory.ticks)[](#gpiozero.pins.mock.MockFactory.ticks "Link to this definition")  
Return the current ticks, according to the factory. The reference point is undefined and thus the result of this method is only meaningful when compared to another value returned by this method.

The format of the time is also arbitrary, as is whether the time wraps after a certain duration. Ticks should only be compared using the [`ticks_diff()`](#gpiozero.pins.mock.MockFactory.ticks_diff "gpiozero.pins.mock.MockFactory.ticks_diff") method.

static ticks_diff(*later*, *earlier*)[\[source\]](_modules/gpiozero/pins/mock.html#MockFactory.ticks_diff)[](#gpiozero.pins.mock.MockFactory.ticks_diff "Link to this definition")  
Return the time in seconds between two [`ticks()`](#gpiozero.pins.mock.MockFactory.ticks "gpiozero.pins.mock.MockFactory.ticks") results. The arguments are specified in the same order as they would be in the formula *later* - *earlier* but the result is guaranteed to be in seconds, and to be positive even if the ticks “wrapped” between calls to [`ticks()`](#gpiozero.pins.mock.MockFactory.ticks "gpiozero.pins.mock.MockFactory.ticks").

pin(*name*, *pin_class=None*, *\*\*kwargs*)[\[source\]](_modules/gpiozero/pins/mock.html#MockFactory.pin)[](#gpiozero.pins.mock.MockFactory.pin "Link to this definition")  
The pin method for [`MockFactory`](#gpiozero.pins.mock.MockFactory "gpiozero.pins.mock.MockFactory") additionally takes a *pin_class* attribute which can be used to override the class’ [`pin_class`](#gpiozero.pins.mock.MockFactory.pin_class "gpiozero.pins.mock.MockFactory.pin_class") attribute. Any additional keyword arguments will be passed along to the pin constructor (useful with things like [`MockConnectedPin`](#gpiozero.pins.mock.MockConnectedPin "gpiozero.pins.mock.MockConnectedPin") which expect to be constructed with another pin).

reset()[\[source\]](_modules/gpiozero/pins/mock.html#MockFactory.reset)[](#gpiozero.pins.mock.MockFactory.reset "Link to this definition")  
Clears the pins and reservations sets. This is primarily useful in test suites to ensure the pin factory is back in a “clean” state before the next set of tests are run.

&nbsp;

class gpiozero.pins.mock.MockPin(*factory*, *info*)[\[source\]](_modules/gpiozero/pins/mock.html#MockPin)[](#gpiozero.pins.mock.MockPin "Link to this definition")  
A mock pin used primarily for testing. This class does *not* support PWM.

&nbsp;

class gpiozero.pins.mock.MockPWMPin(*factory*, *info*)[\[source\]](_modules/gpiozero/pins/mock.html#MockPWMPin)[](#gpiozero.pins.mock.MockPWMPin "Link to this definition")  
This derivative of [`MockPin`](#gpiozero.pins.mock.MockPin "gpiozero.pins.mock.MockPin") adds PWM support.

&nbsp;

class gpiozero.pins.mock.MockConnectedPin(*factory*, *info*, *input_pin=None*)[\[source\]](_modules/gpiozero/pins/mock.html#MockConnectedPin)[](#gpiozero.pins.mock.MockConnectedPin "Link to this definition")  
This derivative of [`MockPin`](#gpiozero.pins.mock.MockPin "gpiozero.pins.mock.MockPin") emulates a pin connected to another mock pin. This is used in the “real pins” portion of the test suite to check that one pin can influence another.

&nbsp;

class gpiozero.pins.mock.MockChargingPin(*factory*, *info*, *charge_time=0.01*)[\[source\]](_modules/gpiozero/pins/mock.html#MockChargingPin)[](#gpiozero.pins.mock.MockChargingPin "Link to this definition")  
This derivative of [`MockPin`](#gpiozero.pins.mock.MockPin "gpiozero.pins.mock.MockPin") emulates a pin which, when set to input, waits a predetermined length of time and then drives itself high (as if attached to, e.g. a typical circuit using an LDR and a capacitor to time the charging rate).

&nbsp;

class gpiozero.pins.mock.MockTriggerPin(*factory*, *info*, *echo_pin=None*, *echo_time=0.04*)[\[source\]](_modules/gpiozero/pins/mock.html#MockTriggerPin)[](#gpiozero.pins.mock.MockTriggerPin "Link to this definition")  
This derivative of [`MockPin`](#gpiozero.pins.mock.MockPin "gpiozero.pins.mock.MockPin") is intended to be used with another [`MockPin`](#gpiozero.pins.mock.MockPin "gpiozero.pins.mock.MockPin") to emulate a distance sensor. Set *echo_pin* to the corresponding pin instance. When this pin is driven high it will trigger the echo pin to drive high for the echo time.

&nbsp;

class gpiozero.pins.mock.MockSPIDevice(*clock_pin*, *mosi_pin=None*, *miso_pin=None*, *select_pin=None*, *\**, *clock_polarity=False*, *clock_phase=False*, *lsb_first=False*, *bits_per_word=8*, *select_high=False*, *pin_factory=None*)[\[source\]](_modules/gpiozero/pins/mock.html#MockSPIDevice)[](#gpiozero.pins.mock.MockSPIDevice "Link to this definition")  
This class is used to test `SPIDevice` implementations. It can be used to mock up the slave side of simple SPI devices, e.g. the MCP3xxx series of ADCs.

Descendants should override the `on_start()` and/or `on_bit()` methods to respond to SPI interface events. The `rx_word()` and `tx_word()` methods can be used facilitate communications within these methods. Such descendents can then be passed as the *spi_class* parameter of the [`MockFactory`](#gpiozero.pins.mock.MockFactory "gpiozero.pins.mock.MockFactory") constructor to have instances attached to any SPI interface requested by an `SPIDevice`.
