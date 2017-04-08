# PerpendicularPaths
A puzzle game where you need to find the shortest path while only moving perpendicular off obstacles. You have 4 movable, color coded pieces. A goal is displayed that is colored the same as one of your peices. Your objective is to move the piece that matches the goal's color to that space. Movement is made in linear directions, but pieces will continue to move until they are obstructed by a wall or another piece. There are multiple solutions to each puzzle, but moves are recorded and the least amount of moves is optimal.<br>
<img src="https://github.com/betterin30days/PerpendicularPaths/blob/master/perppath.gif"/><br>

# How to run tests
`python -m unittest discover -v`

# Displays
This project was written in Python 3 and can use two seperate display interfaces that are both supported by Windows and Mac. There is a terminal view to allow a text-based command prompt/line display. Pygame is used to create a interactive, click-drag display with graphical effects. These interfaces are switched by editing line 2 of config.ini in the model/config directory. Use "native" for the pygame view and "terminal" for the terminal view.<br>
[pygame](http://www.pygame.org/)<br>

# Features
Multiple animations are displayed such as movement, a direction indicator, highlighted possible moves, and an impact  when a piece encounters a wall. A complete move history is displayed, and undo is supported. There is a solver that will calculate the solution with the least possible moves at any given time.<br>

# Screenshots
<img src="http://betterin30days.github.io/perpendicularpaths/screenshots/newgame.png"/><br>
<img src="http://betterin30days.github.io/perpendicularpaths/screenshots/moves.png"/><br>
<img src="http://betterin30days.github.io/perpendicularpaths/screenshots/solve.png"/><br>

[![Build Status](https://travis-ci.org/Jagermeister/PerpendicularPaths.svg?branch=master)](https://travis-ci.org/Jagermeister/PerpendicularPaths)
