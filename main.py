from recycleview import RecycleView
import post_generator
from kivy.properties import ListProperty, BooleanProperty, ObjectProperty, StringProperty, NumericProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import Image, AsyncImage
from kivy.uix.label import Label
from kivy.loader import Loader
from kivy.core.window import Window
from kivy.uix.carousel import Carousel
from kivy.uix.screenmanager import ScreenManager, Screen, RiseInTransition, NoTransition
from kivy.app import App
from kivy.clock import Clock
from kivy.animation import Animation

Loader.loading_image = 'loading_animation.gif'


class ImageWallPost(RelativeLayout):
    image_path = StringProperty('')
    timestamp = StringProperty('')
    from_person = StringProperty('')
    default_background_color = [.15, .15, .15, .7]
    background_color = ListProperty(default_background_color)


class TextWallPost(RelativeLayout):
    label_text = StringProperty('')
    timestamp = StringProperty('')
    from_person = StringProperty('')
    default_background_color = [.2, .2, .2, .7]
    background_color = ListProperty(default_background_color)


class ImageFullPost(AsyncImage):
    image_path = StringProperty('')


class TextFullPost(Label):
    label_text = StringProperty('')


class PostView(RecycleView):
    screen_manager = ObjectProperty()
    anim_move_duration = NumericProperty()

    def __init__(self, **kwargs):
        super(PostView, self).__init__(**kwargs)
        # the screen manager reference
        self.screen_manager = None

    def scroll_wall(self, next_index):
        def animation_complete(animation, widget):
            self.screen_manager.set_moving_flag(False)

        computed_positions = self.current_layout_manager.computed_positions
        # the container height ist the last "position"
        computed_positions = computed_positions + [self.container.height]
        scrollview = self.ids.sv

        scroll_dist = self.compute_vertical_scroll_distance(scrollview, computed_positions, next_index)

        # do the animation
        self.screen_manager.set_moving_flag(True)

        animation = Animation(scroll_y=scroll_dist,  duration=self.anim_move_duration)
        animation.bind(on_complete=animation_complete)
        animation.start(scrollview)
        #scrollview._update_effect_y_bounds()
        self.screen_manager.current_active_post_index = next_index

    def move_wall_to_index(self, post_index):
        scrollview = self.ids.sv
        computed_positions = self.current_layout_manager.computed_positions
        # the layout height ist the last "position"
        computed_positions = computed_positions + [self.container.height]
        scroll_dist = self.compute_vertical_scroll_distance(scrollview, computed_positions, post_index)
        scrollview.scroll_y = scroll_dist

    def compute_vertical_scroll_distance(self, scrollview, computed_positions, post_index):
        # compute the relative distance
        print 'Scrollview height', scrollview.height
        scroll_dist = (scrollview.height - computed_positions[post_index] - computed_positions[post_index + 1])/2
        return 1 + scrollview.convert_distance_to_scroll(0, scroll_dist)[1]


class PostWall(PostView):

    def scroll_wall(self, next_index):
        previously_selected_widget = self.current_adapter.views[self.screen_manager.current_active_post_index]
        super(PostWall, self).scroll_wall(next_index)
        animation = Animation(background_color=previously_selected_widget.default_background_color,
                              duration=self.anim_move_duration)
        animation.start(previously_selected_widget)
        next_selected_widget = self.current_adapter.views[next_index]
        animation = Animation(background_color=[0, 0, .5, .7],  duration=self.anim_move_duration)
        animation.start(next_selected_widget)

    def mark_current_active_post(self, index=None):
        if not index:
            index = self.screen_manager.current_active_post_index
        selected_widget = self.current_adapter.views[index]
        print 'MARKING WIDGET', selected_widget
        selected_widget.background_color = [0, 0, .5, .7]

    def un_mark_post(self, index):
        marked_widget = self.current_adapter.views[index]
        marked_widget.background_color = marked_widget.default_background_color

    def center_first_post(self, *args):
        self.move_wall_to_index(0)
        self.screen_manager.current_active_post_index = 0
        self.mark_current_active_post()


class FullView(PostView):
    anim_move_duration = .35

    def center_first_post(self, *args):
        index = self.screen_manager.current_active_post_index = 0
        self.move_wall_to_index(index)


class PostScreenManager(ScreenManager):
    current_active_post_index = NumericProperty()
    number_of_posts = NumericProperty()
    movement_flag = BooleanProperty()

    def __init__(self, **kwargs):
        super(PostScreenManager, self).__init__(**kwargs)
        self.transition = NoTransition()#RiseInTransition()

        # get the post wall and the full posts references
        wall = self.ids['pw']
        posts = self.ids['fp']

        # pass the refernece to the screen manager
        wall.screen_manager = self
        posts.screen_manager = self
        # generate new data
        data = post_generator.generate_new_data()
        self.number_of_posts = len(data)
        # pass the data to the post wall
        wall.data = data
        newdata = []
        for item in data:
            if item['viewclass'] == 'ImageWallPost':
                newdata.append({
                    'viewclass': 'ImageFullPost',
                    'source': item['image_path']
                })
            elif item['viewclass'] == 'TextWallPost':
                newdata.append({
                    'viewclass': 'TextFullPost',
                    'text': item['label_text']
                })
        # pass the newdata to the posts wall
        posts.data = newdata
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        if not self._keyboard:
            return
        self._keyboard.bind(on_key_down=self.on_keyboard_down)

        self.movement_flag = False
        # Setting the 'posts' as the main screen, although is should be the 'wall', is the workaround for empty post RecycleView after the app was loaded
        self.current = 'Wall screen'
        #self.current = 'Post screen'
        Clock.schedule_once(wall.center_first_post, 1)
        #Clock.schedule_once(posts.center_first_post, 1)


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
        elif self.current == 'Wall screen':
            if ((key == 'up' and self.current_active_post_index > 0) or
                    (key == 'down' and self.current_active_post_index < self.number_of_posts - 1))\
                    and not self.movement_flag:
                next_index = self.current_active_post_index + 1 if key == 'down' else self.current_active_post_index - 1
                self.ids['pw'].scroll_wall(next_index)
                return True
            elif key == 'enter':
                self.ids['fp'].move_wall_to_index(self.current_active_post_index)
                self.current = 'Post screen'
                return True
        # key bindings for the posts
        elif self.current == 'Post screen':
            if ((key == 'up' and self.current_active_post_index > 0) or
                    (key == 'down' and self.current_active_post_index < self.number_of_posts - 1))\
                    and not self.movement_flag:
                next_index = self.current_active_post_index + 1 if key == 'down' else self.current_active_post_index - 1
                self.ids['fp'].scroll_wall(next_index)
                return True
            elif key == 'backspace':
                self.ids['pw'].move_wall_to_index(self.current_active_post_index)
                self.current = 'Wall screen'
                return True


class WallApp(App):

    def build(self):
        return PostScreenManager()

WallApp().run()
