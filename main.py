from recycleview import RecycleView
import post_generator
from kivy.properties import ListProperty, BooleanProperty, ObjectProperty, StringProperty, NumericProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import Image, CoreImage, AsyncImage
from kivy.uix.label import Label
from kivy.loader import Loader
from kivy.core.window import Window
from kivy.uix.carousel import Carousel
from kivy.uix.screenmanager import ScreenManager, Screen, RiseInTransition
from kivy.app import App
from kivy.clock import Clock
from kivy.animation import Animation

Loader.loading_image = 'loading_animation.gif'


class ImagePost(RelativeLayout):
    image_path = StringProperty('')
    timestamp = StringProperty('')
    from_person = StringProperty('')
    default_background_color = [.15, .15, .15, .7]
    background_color = ListProperty(default_background_color)


class TextPost(RelativeLayout):
    label_text = StringProperty('')
    timestamp = StringProperty('')
    from_person = StringProperty('')
    default_background_color = [.2, .2, .2, .7]
    background_color = ListProperty(default_background_color)


class PostWall(RecycleView):
    screen_manager = ObjectProperty()
    anim_move_duration = NumericProperty()

    def __init__(self, **kwargs):
        super(PostWall, self).__init__(**kwargs)
        # the screen manager reference
        self.screen_manager = None
        anim_move_duration = NumericProperty(0.2)

    def scroll_wall(self, next_index):
        def animation_complete(animation, widget):
            self.screen_manager.set_moving_flag(False)

        computed_positions = self.current_layout_manager.computed_positions
        # the layout height ist the last "position"
        computed_positions = computed_positions + [self.ids.layout.height]
        scrollview = self.ids.sv

        scroll_dist = self.compute_vertical_scroll_distance(scrollview, computed_positions, next_index)

        # do the animation
        self.screen_manager.set_moving_flag(True)

        animation = Animation(scroll_y=scroll_dist,  duration=.15)
        animation.bind(on_complete=animation_complete)
        animation.start(scrollview)
        #scrollview._update_effect_y_bounds()
        previous_selected_widget = self.current_adapter.views[self.screen_manager.current_active_post_index]
        animation = Animation(background_color=previous_selected_widget.default_background_color,  duration=.5)
        animation.start(previous_selected_widget)
        next_selected_widget = self.current_adapter.views[next_index]
        animation = Animation(background_color=[0, 0, .5, .7],  duration=self.anim_move_duration)
        animation.start(next_selected_widget)
        self.screen_manager.current_active_post_index = next_index

    def move_wall_to_index(self, post_index):
        scrollview = self.ids.sv
        computed_positions = self.current_layout_manager.computed_positions
        # the layout height ist the last "position"
        computed_positions = computed_positions + [self.ids.layout.height]
        scroll_dist = self.compute_vertical_scroll_distance(scrollview, computed_positions, post_index)
        scrollview.scroll_y = scroll_dist


    def compute_vertical_scroll_distance(self, scrollview, computed_positions, post_index):
        # compute the relative distance
        print 'Scrollview height', scrollview.height
        scroll_dist = (scrollview.height - computed_positions[post_index] - computed_positions[post_index + 1])/2
        return 1 + scrollview.convert_distance_to_scroll(0, scroll_dist)[1]

    def center_first_post(self, *args):
        scrollview = self.ids.sv
        # we scroll to the first post and place it in the middle of the screen
        self.screen_manager.current_active_post_index = 0
        computed_positions = self.current_layout_manager.computed_positions
        print 'Computed positions', computed_positions
        # compute the relative vertical scrolling distance
        scroll_dist = self.compute_vertical_scroll_distance(scrollview, computed_positions,
                                                            self.screen_manager.current_active_post_index)
        print 'Scroll distance', scroll_dist
        scrollview.scroll_y = scroll_dist
        #scrollview._scroll_y_mouse = scroll_dist
        #scrollview._update_effect_y_bounds()
        # now highlight the selected (current) widget
        selected_widget = self.current_adapter.views[self.screen_manager.current_active_post_index]
        #anim = Animation(background_color=[0, 0, .5, .7])
        #anim.start(selected_widget)
        selected_widget.background_color = [0, 0, .5, .7]


class PostCarousel(Carousel):
    screen_manager = ObjectProperty()

    def __init__(self, **kwargs):
        super(PostCarousel, self).__init__(**kwargs)
        self.loop = False
        self.anim_move_duration = 0.3
        self.direction = 'bottom'

        self.screen_manager = None

    def _start_animation(self, *args, **kwargs):
    #    super(PostCarousel, self)._start_animation.#(self, *args, **kwargs)
        # compute target offset for ease back, next or prev
        new_offset = 0
        direction = kwargs.get('direction', self.direction)
        is_horizontal = direction[0] in ['r', 'l']
        extent = self.width if is_horizontal else self.height
        min_move = kwargs.get('min_move', self.min_move)
        _offset = kwargs.get('offset', self._offset)

        if _offset < min_move * -extent:
            new_offset = -extent
        elif _offset > min_move * extent:
            new_offset = extent

        # if new_offset is 0, it wasnt enough to go next/prev
        dur = self.anim_move_duration
        if new_offset == 0:
            dur = self.anim_cancel_duration

        # detect edge cases if not looping
        len_slides = len(self.slides)
        index = self.index
        if not self.loop or len_slides == 1:
            is_first = (index == 0)
            is_last = (index == len_slides - 1)
            if direction[0] in ['r', 't']:
                towards_prev = (new_offset > 0)
                towards_next = (new_offset < 0)
            else:
                towards_prev = (new_offset < 0)
                towards_next = (new_offset > 0)
            if (is_first and towards_prev) or (is_last and towards_next):
                new_offset = 0

        self.screen_manager.set_moving_flag(True)
        anim = Animation(_offset=new_offset, d=dur, t=self.anim_type)
        anim.cancel_all(self)

        def _cmp(*l):
            """
            Only this part of the original _start_animation method will be overridden.
            """
            if self._skip_slide is not None:
                self.index = self._skip_slide
                self._skip_slide = None
            self.screen_manager.set_moving_flag(False)

        anim.bind(on_complete=_cmp)
        anim.start(self)


class PostScreenManager(ScreenManager):
    current_active_post_index = NumericProperty()
    number_of_posts = NumericProperty()
    movement_flag = BooleanProperty()

    def __init__(self, **kwargs):
        super(PostScreenManager, self).__init__(**kwargs)
        self.transition = RiseInTransition()

        # get the post wall and post carousel references
        wall = self.ids['pw']
        carousel = self.ids['pc']

        # pass the refernece to the screen manager
        wall.screen_manager = self
        carousel.screen_manager = self
        # generate new data
        data = post_generator.generate_new_data()
        self.number_of_posts = len(data)
        # pass the data tot he post wall
        wall.data = data
        # feed the carousel with the data
        for item in data:
            if 'ImagePost' in item['viewclass']:
                carousel.add_widget(Image(source=item['image_path']))
            elif 'TextPost' in item['viewclass']:
                carousel.add_widget(Label(text=item['label_text']))

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        if not self._keyboard:
            return
        self._keyboard.bind(on_key_down=self.on_keyboard_down)

        self.movement_flag = False
        #self.current_active_post_index = None
        Clock.schedule_once(wall.center_first_post, 1)

    def set_moving_flag(self, value):
        if not isinstance(value, bool):
            raise TypeError('The movement_flag can be set only to boolean values')
        self.movement_flag = value

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self.on_keyboard_down)
        self._keyboard = None

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):

        key = keycode[1]
        print 'keyboard screen manager', key, text
        # general key bindings
        if key == 'q':
            App.get_running_app().stop()
            return True
        # key binding for the wall
        elif self.current == 'Wall screen':
            if ((key == 'up' and self.current_active_post_index > 0) or
                    (key == 'down' and self.current_active_post_index < self.number_of_posts - 1))\
                    and not self.movement_flag:
                next_index = self.current_active_post_index + 1 if key == 'down' else self.current_active_post_index - 1
                self.ids['pw'].scroll_wall(next_index)
                return True
            elif key == 'enter':
                self.ids['pc'].index = self.current_active_post_index
                self.current = 'Carousel screen'
                return True
        # key bindings for the carousel
        elif self.current == 'Carousel screen':
            if key == 'up' and self.current_active_post_index > 0 and not self.movement_flag:
                self.ids['pc'].load_previous()
                self.current_active_post_index -= 1
            elif key == 'down' and self.current_active_post_index < self.number_of_posts - 1 and not self.movement_flag:
                self.ids['pc'].load_next()
                self.current_active_post_index += 1
            elif key == 'backspace':
                self.ids['pw'].move_wall_to_index(self.current_active_post_index)
                self.current = 'Wall screen'
                return True


class WallApp(App):

    def build(self):
        return PostScreenManager()

WallApp().run()
