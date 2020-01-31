# TRÅDFRI control application

App emulate Tradfri round control behaivour.
Work with standard home assistants lights and required switch to be registered as HASS switch.

# Installation

You can use [HACS](https://hacs.xyz/) or do it manually.


Download the `tradfri_control` directory from inside the apps directory to your local app's directory, then add the configuration to enable the `tradfri_control` module.

# Configuration

```yaml
name_your_app:
  module: tradfri_control
  class: TradfriControl
  
  remote: sensor.tradfri_control_action
  lights: light.my_light

  defaults:
    brightness: 255
    color_temp: 290

  brightness:
    attribute: brightness
    step: 15
    min: 1
    max: 255
    transition: 1 

  arrows: 
    attribute: color_temp
    step: 15
    min: 150
    max: 450
    transition: 1
```

key | optional | type | default | description
-- | -- | -- | -- | --
`module` | False | string | | The module name of the app.
`class` | False | string | | The name of the Class.
`remote` | False | string | | Tradfri switch action name
`lights` | False | string | | Light to controll, can be a single ligth or a group
`defaults` | True | dict | {brightness: 255, color_temp: 290} | Defaults that will be set on main button long press 
`brightness` | True | dict | | Dimmer settings that will be applied on brightness up/down buttons
`brightness.attribute` | False | string | | Attribute to change
`brightness.step` | True | int | 15 | Step value
`brightness.min` | True | int | 0 | Min value for this attribute
`brightness.max` | True | int | 255 | Max value for this attribute
`brightness.transition` | True | int | 1 | Transition time for dimmer single click 
`arrows` | True | dict | | Dimmer settings that will be applied on arrows left/right buttons
`arrows.attribute` | False | string | | Attribute to change
`arrows.step` | True | int | 15 | Step value
`arrows.min` | True | int | 0 | Min value for this attribute
`arrows.max` | True | int | 255 | Max value for this attribute
`arrows.transition` | True | int | 1 | Transition time for dimmer single click 
```
