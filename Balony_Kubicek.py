import rhinoscriptsyntax as rs
import Rhino

# OFFSETING PARAMETERS:
DISTANCE = 21
# EXTENTION PARAMETERS
MY_EXTENSION_TYPE = 0  # 0 for line, 1 for arc

# select an object (a curve or a boudary intended)
def Select_Object(text):
    my_object = rs.GetObject("Select" + text + ": ", rs.filter.curve)
    return my_object

# offset curve upper
def Curve_Create_Offset_Left_Right(curve, boundary, distance):
    my_normal_to_curve = rs.CurveNormal(curve)
    Curve_Offset_Inner(curve, boundary, distance, my_normal_to_curve)
    Curve_Offset_Inner(curve, boundary, -distance, my_normal_to_curve)

# offset curve inner
def Curve_Offset_Inner(curve, boundary, distance, direction):
    my_new_curve = rs.OffsetCurve(curve, direction, distance)

    # 1) Extend the curve if it is inside the boudary
    start_end_points = [rs.CurveStartPoint(my_new_curve), rs.CurveEndPoint(my_new_curve)]
    for number, point in enumerate(start_end_points):
        if rs.PointInPlanarClosedCurve(point, boundary) == 1:
            my_new_curve = rs.ExtendCurve(my_new_curve, MY_EXTENSION_TYPE, number, [boundary])

    # 2) Shorten the curve if it stretches over the boudary
    intersections = rs.CurveCurveIntersection(my_new_curve, boundary)

    if not intersections:
        print("There are no intersections of {} and {}.".format(my_new_curve, boundary))
        return

    Split_Points = []
    for intersection in intersections:
        # on the 5 index is the intersection point
        Split_Points.append(intersection[5])
    Split_Curves = rs.SplitCurve(my_new_curve, Split_Points)

    if not Split_Curves:
        print('No split curves found.')
        return

    print('{} splited into {} new curves.'.format(my_new_curve, Split_Curves.Count))

    # 3) Delete the curves outside the boundary. Count deleted curves.
    deleted_curves = 0
    for splited_curve_segment in Split_Curves:
        curve_middle_point = rs.CurveMidPoint(splited_curve_segment)
        if rs.PointInPlanarClosedCurve(curve_middle_point, boundary) != 1:
            rs.DeleteObject(splited_curve_segment)
            deleted_curves += 1

    print('{} outside curves removed.'.format(deleted_curves))

# FINAL FUNCTION - DEFINE
def Duplicate_Curve_Extend_Shorten():
    Original_Curve = Select_Object("a curve to edit")
    Boundary = Select_Object("a boundary")
    Curve_Create_Offset_Left_Right(Original_Curve, Boundary, DISTANCE)
    print('Code finished as expected. No errors detected.')

# FINAL FUNCTION - CALL
Duplicate_Curve_Extend_Shorten()