Point(1) = {-0.7, 0.6, 0, 1.0};
Point(2) = {-0.2, 0.9, 0, 1.0};
Point(3) = {0.3, 0.4, 0, 1.0};
Point(4) = {-0.2, -0.2, 0, 1.0};
Point(5) = {-0.6, 0.1, 0, 1.0};
Point(6) = {0.4, 0.9, 0, 1.0};
Point(7) = {0.5, -0.2, 0, 1.0};
Point(8) = {-0.9, -0.3, 0, 1.0};
Point(9) = {-0.9, 0.9, 0, 1.0};
Line(1) = {9, 2};
Line(2) = {2, 6};
Line(3) = {6, 7};
Line(4) = {7, 4};
Line(5) = {4, 8};
Line(6) = {8, 9};
Line(7) = {2, 5};
Line(8) = {1, 3};
Line Loop(9) = {6, 1, 2, 3, 4, 5};
Plane Surface(10) = {9};
Point{1, 3, 5, 2} In Surface{10};
Point{1, 5, 3} In Surface{10};
Point{1, 5, 3} In Surface{10};
