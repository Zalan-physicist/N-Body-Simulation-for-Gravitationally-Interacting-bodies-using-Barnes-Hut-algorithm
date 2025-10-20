This code attempts to create a 2-D simulation of the implementation of the Barnes-Hut algorithm on a group of masses that interact via Newtonian Gravitation.
Since the analytical solutions of an n-body (n>2) problem are not possible, we use approximations to model the system.
Barnes-Hut algroithm is one approximation scheme for this purpose.
Masses are placed in "cells". To find the force on a particular mass (field point), we classify all other masses into two categories: masses that are "sufficiently" near the field point so that they can be individually considered, and masses that are sufficiently far away for us to treat them as a single object at their centre of mass.
To quantify the argument, we define a 'theta parameter' which is simply the width of the cell occupied by the field point divided by the actual distance of the other mass to the field point
In our case we keep the ratio at 0.5: theta less than 0.5 would indicate a 'sufficiently long'.
We then iterate for all our masses in this manner, and update their positions, velocities using the Euler-Cromer method to simplify the calculations.

Class Point is used to create the masses which have the attributes of mass, position, velocity and the net force being exerted on them.

Class Rectangle defines the 'cell' in which the masses are located. Each cell therefore has the relevant x,y coordinates of the left lower corner, the width and height. We also place attributes of the total number of object contained within, the total mass and the centre of mass position. There are methods to update the centre of mass, total mass, to verify whether a particular object exists in the cell, and to insert new objects. 

Class Quadtree creates the whole grid where the cells and objects shall be placed. There will be a capacity, beyond which if more masses are to be added, the grid would be divided into 4 cells (Rectangle class objects); northeast, northwest etc. Masses are inserted according to their positions and the particular cells they correspond to. Methods for calculating force are included.

Finally we run loops to iterate over each mass and find the net forces, then update the position and velocity through the Euler-Cromer method and simulate the evolution using Matplotlib.


