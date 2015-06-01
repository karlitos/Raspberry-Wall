# Raspberry-Wall
Raspberry Wall is a implementation of a message-board/post-wall allowing to display short messages, images and videos on a screen, scroll through them, display the images and play the videos in full-screen. It queries an specified mailbox for particular messages, extract the text and display valid attachments. It works as an digital picture/video frame after some idle timeout.

## Installation
Raspberry Wall uses the [Kivy Cross-platform Python Framework](http://kivy.org/) and is based on the [incredible work](https://github.com/kivy-garden/garden.recycleview) of [Mathieu Virbel](https://github.com/tito). In order to run the Raspberry Wall you have to install recent Version of Kivy on your platform and also install the RecycleView Kivy widget. Follow the instructions in the _recycleview_ folder.

## Features
* run (also) on Raspberry-Pi directly in the framebuffer with minimal overhead
* generate random posts with images and text
* scroll through the posts with up/down arrow-keys

## ToDo
* display the selected post in full-screen
* go through the posts in full-screen mode
* query mailbox for new messages and save them locally
* notification (play sound) when new messages were received
* allow posts with video
* allow full-screen video playback
