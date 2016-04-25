# The Helmet Thing
## we need a better name...

This is basically where I plan to document the project, its overall design, code, and future directions. There may be other documents for each part as we develop it but this the main README. I'll link to other subdocuments as they are created. The spreadsheets and Word files already written are in this repository under 'doc'.

## Technical Directions

### Project Language (Python3):

For a variety of reasons this will be Python3 at least for the first prototype. The project can be recoded in a faster compiled language later after the basic concept is proven. There is also the [PyPy](http://pypy.org/ "PyPy") JIT compiler, which can often yield much better speed with Python than the standard CPython environment. I have yet to experiment with this option though. Additionally, the Raspberry Pi, which is the hardware platform for the project at this stage, already comes with a special version of Python3 that supports the unique features of the RPi hardware such as GPIO and SPI. It also seems that the Pi world in general focuses on developing in Python3 rather than Python2. [This link](http://stackoverflow.com/questions/24859323/which-python-version-should-i-use-with-raspberry-pi-running-web-applications "This link") goes into some more technical discussion of these issues.

### Configuration File Format (JSON & SVG):

This can be kept fairly simple. Most of the data objects in this project are simply representations of players. These are fairly simple for the purposes we intend, mainly consisting of the players' locations, velocities, weights, heights, and whatever else might be relevant about them. I do not anticipate any need for complex, multilayered, or intertwined structures. JSON is very well supported in Python3 and we should be able to use it to read and write all relevant player and game data. The exception to JSON might be the use of SVG files to describe player and bot trajectories. This makes it easy to use existing drawing tools like Inkscape to create test data and display results. Fortunately, there are several good SVG parsers available for Python.


