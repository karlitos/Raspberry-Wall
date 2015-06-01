from recycleview import RecycleView
import post_generator
from kivy.properties import ListProperty, BooleanProperty, ObjectProperty
from kivy.properties import StringProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window
from kivy.app import App
from kivy.clock import Clock
from kivy.animation import Animation
import random
import time


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
    posts = ListProperty()
    movement_flag = BooleanProperty()
    selected_post_index = ObjectProperty()

    def __init__(self, **kwargs):
        super(PostWall, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        if not self._keyboard:
            return
        self._keyboard.bind(on_key_down=self.on_keyboard_down)

        self.data = post_generator.generate_new_data()
        self.movement_flag = False

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self.on_keyboard_down)
        self._keyboard = None

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        def animation_complete(animation, widget):
            self.movement_flag = False

        key = keycode[1]
        #print 'keyboard', key, text

        if (key == 'up' or key == 'down') and not self.movement_flag:
            computed_positions = self.current_layout_manager.computed_positions
            if (key == 'down' and self.selected_post_index >= len(computed_positions) - 1) or\
                    (key == 'up' and self.selected_post_index <= 0):
                return False
            # the layout height ist the last "position"
            computed_positions = computed_positions + [self.ids.layout.height]
            scrollview = self.ids.sv

            next_index = self.selected_post_index + 1 if key == 'down' else self.selected_post_index - 1
            scroll_dist = self.compute_vertical_scroll_distance(scrollview, computed_positions, next_index)

            # do the animation
            self.movement_flag = True

            animation = Animation(scroll_y=scroll_dist,  duration=.15)
            animation.bind(on_complete=animation_complete)
            animation.start(scrollview)
            #scrollview._update_effect_y_bounds()
            previous_selected_widget = self.current_adapter.views[self.selected_post_index]
            animation = Animation(background_color=previous_selected_widget.default_background_color,  duration=.2)
            animation.start(previous_selected_widget)
            next_selected_widget = self.current_adapter.views[next_index]
            animation = Animation(background_color=[0, 0, .5, .7],  duration=.2)
            animation.start(next_selected_widget)
            self.selected_post_index = next_index

        elif key == 'q':
            App.get_running_app().stop()
            return True

    def compute_vertical_scroll_distance(self, scrollview, computed_positions, post_index):
        # compute the relative distance
        scroll_dist = (scrollview.height - computed_positions[post_index] - computed_positions[post_index + 1])/2
        return 1 + scrollview.convert_distance_to_scroll(0, scroll_dist)[1]

    def center_first_post(self, *args):
        scrollview = self.ids.sv
        # we scroll to the first post and place it in the middle of the screen
        self.selected_post_index = 0
        computed_positions = self.current_layout_manager.computed_positions
        # compute the relative vertical scrolling distance
        scroll_dist = self.compute_vertical_scroll_distance(scrollview, computed_positions, self.selected_post_index)
        scrollview.scroll_y = scroll_dist
        #scrollview._scroll_y_mouse = scroll_dist
        #scrollview._update_effect_y_bounds()
        # now highlight the selected (current) widget
        selected_widget = self.current_adapter.views[self.selected_post_index]
        #anim = Animation(background_color=[0, 0, .5, .7])
        #anim.start(selected_widget)
        selected_widget.background_color = [0, 0, .5, .7]


class WallApp(App):
    def build(self):
        wall = PostWall()
        Clock.schedule_once(wall.center_first_post, 0)
        return wall

WallApp().run()
