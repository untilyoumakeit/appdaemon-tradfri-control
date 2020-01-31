import appdaemon.plugins.hass.hassapi as hass
from typing import Callable


class Events:
  TOGGLE = "toggle"
  TOGGLE_HOLD = "toggle_hold"

  ARROW_RIGHT_CLICK = "arrow_right_click"
  ARROW_LEFT_CLICK = "arrow_left_click"
  ARROW_LEFT_HOLD = "arrow_left_hold"
  ARROW_RIGHT_HOLD = "arrow_right_hold"
  ARROW_LEFT_RELEASE = "arrow_left_release"
  ARROW_RIGHT_RELEASE = "arrow_right_release"  

  BRIGHTNESS_UP_CLICK = "brightness_up_click"
  BRIGHTNESS_DOWN_CLICK = "brightness_down_click"
  BRIGHTNESS_UP_HOLD = "brightness_up_hold"
  BRIGHTNESS_DOWN_HOLD = "brightness_down_hold"
  BRIGHTNESS_UP_RELEASE = "brightness_up_release"
  BRIGHTNESS_DOWN_RELEASE = "brightness_down_release"  


class Dimmer:
  """ Control one of the posible direction for dimmer """
  def __init__(self, get: Callable[[], int], set: Callable[[int, int], None], step: int, transition: int, min: int = 0, max: int = 255):
    self.__min = min
    self.__max = max
    self.__step = step
    self.__transition = transition
    self.__get = get
    self.__set = set
    self.__timer = None


  def up(self, hold = False):
    """ Increase value """
    self.__tick(lambda x: min(x + self.__step, self.__max), hold = hold)


  def down(self, hold = False):
    """ Decrease value """
    self.__tick(lambda x: max(x - self.__step, self.__min), hold = hold)


  def stop(self):
    """ Stop dimming progress if any """
    self.__in_progress = False


  def __tick(self, next_value: Callable[[int], int], hold: bool):
    current = self.__get()
    next = next_value(current)
    if next == current:
      self.stop()
    else:
      self.__set(next, self.__transition if hold is False else 0.2)
      if hold is True:
        def tick(app, **kwargs):
          if self.__in_progress is False:
            return
          self.__tick(next_value, hold = True)
        self.__in_progress = True
        self.run_in(tick, 1) # Do the next check in a second


class TradfriControl(hass.Hass):
  """
  IKEA Tradfri round control automation, as I use it
  """

  
  def __create_dimmer(self, config_key: str) -> Dimmer:
    if config_key in self.args:
      self.log(f"Create actions on {config_key} buttons")
      config = self.args[config_key]
      
      attribute = config.get("attribute")
      transition = config.get("transition", 1)
      step = config.get("step", 1)
      min = config.get("min", 1)
      max = config.get("max", 255)
    
      get = lambda: self.get_state(self.lights, attribute = attribute) or 0
      set = lambda b, t: self.turn_on(self.lights, transition = t, **{attribute: b})
      dimmer = Dimmer(get = get, set = set, step = step, transition = transition, min = min, max = max)
      dimmer.run_in = lambda f, t: self.run_in(f, t)
      return dimmer
    else:
      self.log(f"Didn't find {config_key} in attributes")
      return None


  def initialize(self):
    """ Initialisation """
    self.target = self.args["remote"]
    self.lights = self.args["lights"]

    self.brightness = self.__create_dimmer("brightness")
    self.arrows = self.__create_dimmer("arrows")

    # Subscribe to HASS events
    self.set_namespace("hass")
    self.listen_state(self.buttons_callback, self.target)


  def terminate(self):
    if self.brightness is not None:
      self.brightness.stop()
    if self.arrows is not None:
      self.arrows.stop()


  def buttons_callback(self, entity, attribute, old, new, kwargs):
    """ React on changes and dispatch to methods """
    if new == Events.TOGGLE:
      self.toggle()
    elif new == Events.TOGGLE_HOLD:
      self.reset()
    else:
      is_on = self.get_state(self.lights) == "on"
      # React on brightness

      if self.brightness is not None:
        if is_on and new == Events.BRIGHTNESS_UP_CLICK or new == Events.BRIGHTNESS_UP_HOLD:
          self.brightness.up(hold = new == Events.BRIGHTNESS_UP_HOLD)
        elif is_on and new == Events.BRIGHTNESS_DOWN_CLICK or new == Events.BRIGHTNESS_DOWN_HOLD:
          self.brightness.down(hold = new == Events.BRIGHTNESS_DOWN_HOLD)
        elif new == Events.BRIGHTNESS_UP_RELEASE or new == Events.BRIGHTNESS_DOWN_RELEASE:
          self.brightness.stop()
      # React on arrow buttons
      if self.arrows is not None:
        if is_on and (new == Events.ARROW_RIGHT_CLICK or new == Events.ARROW_RIGHT_HOLD):
          self.arrows.up(hold = new == Events.ARROW_RIGHT_HOLD)
        elif is_on and new == Events.ARROW_LEFT_CLICK or new == Events.ARROW_LEFT_HOLD:
          self.arrows.down(hold = new == Events.ARROW_LEFT_HOLD)
        elif new == Events.ARROW_RIGHT_RELEASE or new == Events.ARROW_LEFT_RELEASE:
          self.arrows.stop()


  def toggle(self):
    """ Toggle lights state """
    super().toggle(self.lights) 


  def reset(self):
    """ Reset lights to default values """
    defaults = self.args.get("defaults", {"brightness": 255, "rgb_color":  [255, 218, 109], "color_temp": 290})
    self.turn_on(self.lights, **defaults)

