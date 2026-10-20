---
source: https://aiyprojects.readthedocs.io/en/latest/aiy.vision.inference.html
fetched: 2026-10-20
---

# aiy.vision.inference[¶](#module-aiy.vision.inference "Permalink to this headline")

An inference engine that communicates with the Vision Bonnet from the Raspberry Pi side.

It can be used to load a model, analyze local image or image from camera shot. It automatically unload the model once the associated object is deleted. See image_classification.py and object_recognition.py as examples on how to use this API.

*class* `aiy.vision.inference.``CameraInference`(*descriptor*, *params=None*, *sparse_configs=None*)[¶](#aiy.vision.inference.CameraInference "Permalink to this definition")  
Bases: [`object`](https://docs.python.org/3/library/functions.html#object "(in Python v3.9)")

Helper class to run camera inference.

`close`()[¶](#aiy.vision.inference.CameraInference.close "Permalink to this definition")  

`count`[¶](#aiy.vision.inference.CameraInference.count "Permalink to this definition")  

`engine`[¶](#aiy.vision.inference.CameraInference.engine "Permalink to this definition")  

`rate`[¶](#aiy.vision.inference.CameraInference.rate "Permalink to this definition")  

`run`(*count=None*)[¶](#aiy.vision.inference.CameraInference.run "Permalink to this definition")  

&nbsp;

*class* `aiy.vision.inference.``FirmwareVersion`(*major*, *minor*)[¶](#aiy.vision.inference.FirmwareVersion "Permalink to this definition")  
Bases: [`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple "(in Python v3.9)")

`major`[¶](#aiy.vision.inference.FirmwareVersion.major "Permalink to this definition")  
Alias for field number 0

`minor`[¶](#aiy.vision.inference.FirmwareVersion.minor "Permalink to this definition")  
Alias for field number 1

&nbsp;

*exception* `aiy.vision.inference.``FirmwareVersionException`(*\*args*, *\*\*kwargs*)[¶](#aiy.vision.inference.FirmwareVersionException "Permalink to this definition")  
Bases: [`Exception`](https://docs.python.org/3/library/exceptions.html#Exception "(in Python v3.9)")

&nbsp;

*class* `aiy.vision.inference.``FromSparseTensorConfig`(*logical_shape*, *tensor_name*, *squeeze_dims*)[¶](#aiy.vision.inference.FromSparseTensorConfig "Permalink to this definition")  
Bases: [`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple "(in Python v3.9)")

`logical_shape`[¶](#aiy.vision.inference.FromSparseTensorConfig.logical_shape "Permalink to this definition")  
Alias for field number 0

`squeeze_dims`[¶](#aiy.vision.inference.FromSparseTensorConfig.squeeze_dims "Permalink to this definition")  
Alias for field number 2

`tensor_name`[¶](#aiy.vision.inference.FromSparseTensorConfig.tensor_name "Permalink to this definition")  
Alias for field number 1

&nbsp;

*class* `aiy.vision.inference.``ImageInference`(*descriptor*)[¶](#aiy.vision.inference.ImageInference "Permalink to this definition")  
Bases: [`object`](https://docs.python.org/3/library/functions.html#object "(in Python v3.9)")

Helper class to run image inference.

`close`()[¶](#aiy.vision.inference.ImageInference.close "Permalink to this definition")  

`engine`[¶](#aiy.vision.inference.ImageInference.engine "Permalink to this definition")  

`run`(*image*, *params=None*, *sparse_configs=None*)[¶](#aiy.vision.inference.ImageInference.run "Permalink to this definition")  

&nbsp;

*class* `aiy.vision.inference.``InferenceEngine`[¶](#aiy.vision.inference.InferenceEngine "Permalink to this definition")  
Bases: [`object`](https://docs.python.org/3/library/functions.html#object "(in Python v3.9)")

Class to access InferenceEngine on VisionBonnet board.

Inference result has the following format:

message InferenceResult {\
  string model_name;  // Name of the model to run inference on.\
  int32 width;        // Input image/frame width.\
  int32 height;       // Input image/frame height.\
  Rectangle window;   // Window inside width x height image/frame.\
  int32 duration_ms;  // Inference duration.\
  map\<string, FloatTensor\> tensors;  // Output tensors.\
\
  message Frame {\
    int32 index;        // Frame number.\
    int64 timestamp_us; // Frame timestamp.\
  }\
\
  Frame frame;          // Frame-specific inference data.\
}\

`camera_inference`()[¶](#aiy.vision.inference.InferenceEngine.camera_inference "Permalink to this definition")  
Returns the latest inference result from VisionBonnet.

`close`()[¶](#aiy.vision.inference.InferenceEngine.close "Permalink to this definition")  

`get_camera_state`()[¶](#aiy.vision.inference.InferenceEngine.get_camera_state "Permalink to this definition")  
Returns current camera state.

`get_firmware_info`()[¶](#aiy.vision.inference.InferenceEngine.get_firmware_info "Permalink to this definition")  
Returns firmware version as (major, minor) tuple.

`get_inference_state`()[¶](#aiy.vision.inference.InferenceEngine.get_inference_state "Permalink to this definition")  
Returns inference state.

`get_system_info`()[¶](#aiy.vision.inference.InferenceEngine.get_system_info "Permalink to this definition")  
Returns system information: uptime, memory usage, temperature.

`image_inference`(*model_name*, *image*, *params=None*, *sparse_configs=None*)[¶](#aiy.vision.inference.InferenceEngine.image_inference "Permalink to this definition")  
Runs inference on image using model identified by model_name.

[TABLE]

`load_model`(*descriptor*)[¶](#aiy.vision.inference.InferenceEngine.load_model "Permalink to this definition")  
Loads model on VisionBonnet.

|  |  |
|----|----|
| Parameters: | **descriptor** – ModelDescriptor, meta info that defines model name, where to get the model and etc. |
| Returns: | Model identifier. |

`reset`()[¶](#aiy.vision.inference.InferenceEngine.reset "Permalink to this definition")  

`start_camera_inference`(*model_name*, *params=None*, *sparse_configs=None*)[¶](#aiy.vision.inference.InferenceEngine.start_camera_inference "Permalink to this definition")  
Starts inference running on VisionBonnet.

`stop_camera_inference`()[¶](#aiy.vision.inference.InferenceEngine.stop_camera_inference "Permalink to this definition")  
Stops inference running on VisionBonnet.

`unload_model`(*model_name*)[¶](#aiy.vision.inference.InferenceEngine.unload_model "Permalink to this definition")  
Deletes model on VisionBonnet.

|  |  |
|----|----|
| Parameters: | **model_name** – string, unique identifier used to refer a model. |

&nbsp;

*exception* `aiy.vision.inference.``InferenceException`(*\*args*, *\*\*kwargs*)[¶](#aiy.vision.inference.InferenceException "Permalink to this definition")  
Bases: [`Exception`](https://docs.python.org/3/library/exceptions.html#Exception "(in Python v3.9)")

&nbsp;

*class* `aiy.vision.inference.``ModelDescriptor`(*name*, *input_shape*, *input_normalizer*, *compute_graph*)[¶](#aiy.vision.inference.ModelDescriptor "Permalink to this definition")  
Bases: [`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple "(in Python v3.9)")

`compute_graph`[¶](#aiy.vision.inference.ModelDescriptor.compute_graph "Permalink to this definition")  
Alias for field number 3

`input_normalizer`[¶](#aiy.vision.inference.ModelDescriptor.input_normalizer "Permalink to this definition")  
Alias for field number 2

`input_shape`[¶](#aiy.vision.inference.ModelDescriptor.input_shape "Permalink to this definition")  
Alias for field number 1

`name`[¶](#aiy.vision.inference.ModelDescriptor.name "Permalink to this definition")  
Alias for field number 0

&nbsp;

*class* `aiy.vision.inference.``ThresholdingConfig`(*logical_shape*, *threshold*, *top_k*, *to_ignore*)[¶](#aiy.vision.inference.ThresholdingConfig "Permalink to this definition")  
Bases: [`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple "(in Python v3.9)")

`logical_shape`[¶](#aiy.vision.inference.ThresholdingConfig.logical_shape "Permalink to this definition")  
Alias for field number 0

`threshold`[¶](#aiy.vision.inference.ThresholdingConfig.threshold "Permalink to this definition")  
Alias for field number 1

`to_ignore`[¶](#aiy.vision.inference.ThresholdingConfig.to_ignore "Permalink to this definition")  
Alias for field number 3

`top_k`[¶](#aiy.vision.inference.ThresholdingConfig.top_k "Permalink to this definition")  
Alias for field number 2
