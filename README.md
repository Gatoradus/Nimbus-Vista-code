# The Helmet Thing
## we need a better name...

This is basically where I plan to document the project, its overall design, code, and future directions. There may be other documents for each part as we develop it but this is it for now.

## Design Overview and Progress Report

This document is meant to build on the spreadsheets and Word files already written. They are in this repository under 'doc'.

### Technical Directions

#### Project Language (Python3):

for a variety of reasons this will be Python3 at least for the first prototype. The project can be recoded in a faster compiled language later after the basic concept is proven. The Raspberry Pi, which is the hardware platform for the project at this stage also already comes with a special version of Python3 that supports the unique features of the RPi hardware such as GPIO and SPI. Additionally, it seems that the Pi project leaders have mainly focused on developing in Python3 rather than Python2. [This link](http://stackoverflow.com/questions/1713554/threads-processes-vs-multithreading-multi-core-multiprocessor-how-they-are "This link") goes into some more technical discussion of these issues.

#### Configuration File Format (JSON & SVG):

This can be kept fairly simple. Most of the data objects in this project are simply representations of players. These are fairly simple for the purposes we intend, maily consisting of the players' locations, velocities, weights, heights, and whatever else might be relevant about them. I do not anticipate any need for complex, multilayered, or intertwined structures. JSON is very well supported in Python3 and we should be able to use it to read and write all relevant player and game data. The exception to JSON might be the use of SVG files to describe player and bot trajectories. This makes it easy to use existing drawing tools like Inkscape to create test data and display results. Fortunately, there are several good SVG parsers available for Python.


