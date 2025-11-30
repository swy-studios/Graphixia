import turtle
import math
import json

# TURN ON FULLSCREEN

version = "1.0.3"


currentPID = 1

turtle.tracer(False)
turtle.speed(0)
turtle.penup()
turtle.hideturtle()

screen = turtle.Screen()
screen.title("Graphixia v" + version)
sw = screen.window_width()
sh = screen.window_height()

# --- Camera ---
camx, camy, camz = 0, 0, 1
camRotationX, camRotationY, camRotationZ = 0, 0, 0


# ----------- MATRIX ROTATIONS -----------
def rotateX(x, y, z, angle):
    a = math.radians(angle)
    cosA = math.cos(a)
    sinA = math.sin(a)
    ny = y * cosA - z * sinA
    nz = y * sinA + z * cosA
    return x, ny, nz

def rotateY(x, y, z, angle):
    a = math.radians(angle)
    cosA = math.cos(a)
    sinA = math.sin(a)
    nx = x * cosA + z * sinA
    nz = -x * sinA + z * cosA
    return nx, y, nz

def rotateZ(x, y, z, angle):
    a = math.radians(angle)
    cosA = math.cos(a)
    sinA = math.sin(a)
    nx = x * cosA - y * sinA
    ny = x * sinA + y * cosA
    return nx, ny, z

# ----------- 2D Transform from 3D -----------
def transformPoint(x, y):
    z = 0
    x -= camx
    y -= camy

    x, y, z = rotateX(x, y, z, camRotationX)
    x, y, z = rotateY(x, y, z, camRotationY)
    x, y, z = rotateZ(x, y, z, camRotationZ)

    perspective = 1 / (1 + z * 0.005) if z != 0 else 1
    x *= camz * perspective
    y *= camz * perspective
    return x, y

def setposTransform(x, y):
    sx, sy = transformPoint(x, y)
    turtle.goto(sx, sy)

# ----------- Basic Drawing -----------
def drawpolygon(x1, y1, x2, y2, x3, y3):
    turtle.penup()
    setposTransform(x1, y1)
    turtle.pendown()
    turtle.begin_fill()
    setposTransform(x2, y2)
    setposTransform(x3, y3)
    setposTransform(x1, y1)
    turtle.end_fill()
    turtle.penup()

def drawplane(x1, y1, x2, y2, x3, y3, x4, y4):
    turtle.penup()
    setposTransform(x1, y1)
    turtle.pendown()
    turtle.begin_fill()
    setposTransform(x2, y2)
    setposTransform(x3, y3)
    setposTransform(x4, y4)
    setposTransform(x1, y1)
    turtle.end_fill()
    turtle.penup()

def drawsquare2D(x1,y1,x2,y2,x3,y3,x4,y4):
    turtle.penup()
    turtle.goto(x1,y1)
    turtle.pendown()
    turtle.begin_fill()
    turtle.goto(x2,y2)
    turtle.goto(x3,y3)
    turtle.goto(x4,y4)
    turtle.goto(x1,y1)
    turtle.end_fill()
    turtle.penup()

# ----------- Camera Movement -----------
def right(): global camx; camx += 2; update_screen()
def left(): global camx; camx -= 2; update_screen()
def up(): global camy; camy += 2; update_screen()
def down(): global camy; camy -= 2; update_screen()
def zoom_in(): global camz; camz *= 1.1; update_screen()
def zoom_out(): global camz; camz /= 1.1; update_screen()

# ----------- Camera Rotation -----------
def rot_x_positive(): global camRotationX; camRotationX += 1.25; update_screen()
def rot_x_negative(): global camRotationX; camRotationX -= 1.25; update_screen()
def rot_y_positive(): global camRotationY; camRotationY += 1.25; update_screen()
def rot_y_negative(): global camRotationY; camRotationY -= 1.25; update_screen()
def rot_z_positive(): global camRotationZ; camRotationZ += 1.25; update_screen()
def rot_z_negative(): global camRotationZ; camRotationZ -= 1.25; update_screen()

# ----------- 3D Projection & Solid Cube -----------
def project3D(x, y, z, dist=600.0):
    x -= camx
    y -= camy
    xr, yr, zr = rotateX(x, y, z, camRotationX)
    xr, yr, zr = rotateY(xr, yr, zr, camRotationY)
    xr, yr, zr = rotateZ(xr, yr, zr, camRotationZ)
    zr = -zr
    denom = zr + dist
    if denom == 0: denom = 0.0001
    factor = dist / denom
    sx = xr * factor * camz
    sy = -yr * factor * camz
    return sx, sy, zr

def drawFilledFace3D(pts3d, color):
    projected = [project3D(x, y, z) for (x, y, z) in pts3d]
    turtle.fillcolor(color)
    turtle.penup()
    turtle.goto(projected[0][0], projected[0][1])
    turtle.pendown()
    turtle.begin_fill()
    for sx, sy, _ in projected[1:]:
        turtle.goto(sx, sy)
    turtle.goto(projected[0][0], projected[0][1])
    turtle.end_fill()
    turtle.penup()

def average_z_of_face(pts3d):
    zs = []
    for x, y, z in pts3d:
        xr, yr, zr = rotateX(x - camx, y - camy, z, camRotationX)
        xr, yr, zr = rotateY(xr, yr, zr, camRotationY)
        xr, yr, zr = rotateZ(xr, yr, zr, camRotationZ)
        zs.append(zr)
    return sum(zs) / len(zs)

def drawSolidCube(center_x, center_y, center_z, size):
    global verticecount, facecount
    s = size / 2
    V = [
        (center_x - s, center_y - s, center_z - s),
        (center_x + s, center_y - s, center_z - s),
        (center_x + s, center_y + s, center_z - s),
        (center_x - s, center_y + s, center_z - s),
        (center_x - s, center_y - s, center_z + s),
        (center_x + s, center_y - s, center_z + s),
        (center_x + s, center_y + s, center_z + s),
        (center_x - s, center_y + s, center_z + s),
    ]
    faces = [
        (0,1,2,3, "#d95f5f"),
        (4,5,6,7, "#5fbe7a"),
        (0,1,5,4, "#5f8fbf"),
        (3,2,6,7, "#e6c64d"),
        (1,2,6,5, "#5fd0d9"),
        (0,3,7,4, "#c97ec6"),
    ]

    face_infos = []
    for a,b,c,d,color in faces:
        pts = [V[a], V[b], V[c], V[d]]
        avgz = average_z_of_face(pts)
        face_infos.append((avgz, pts, color))
    face_infos.sort(key=lambda x: x[0])
    for avgz, pts, color in face_infos:
        drawFilledFace3D(pts, color)

# ----------- REDRAW -----------
def PID1():
    setposTransform(-300, 0)
    turtle.write("cube (#0001) by swy_studios", False, "center", ("Arial", 10, "bold"))
    turtle.goto(0,-screen.window_height() / 4)
    turtle.write("cam position :" + str(camx) + ", " + str(camy) + ", " + str(camz), False, "center", ("Arial", 10, "bold"))
    turtle.goto(0,(-screen.window_height() / 4) - 15)
    turtle.write("cam rotation :" + str(camRotationX) + ", " + str(camRotationY) + ", " + str(camRotationZ), False, "center", ("Arial", 10, "bold"))
    drawSolidCube(0, 0, 0, 100)

def PID2():
    setposTransform(-300, 0)
    turtle.write("playground (#0002) by swy_studios", False, "center", ("Arial", 10, "bold"))
    turtle.goto(0,-screen.window_height() / 4)
    turtle.write("cam position :" + str(camx) + ", " + str(camy) + ", " + str(camz), False, "center", ("Arial", 10, "bold"))
    turtle.goto(0,(-screen.window_height() / 4) - 15)
    turtle.write("cam rotation :" + str(camRotationX) + ", " + str(camRotationY) + ", " + str(camRotationZ), False, "center", ("Arial", 10, "bold"))
    drawSolidCube(0, 0, 0, 200)
    drawSolidCube(300, 0, 0, 50)

def update_screen():
    turtle.clear()
    if currentPID == 1:
        PID1()
    elif currentPID == 2:
        PID2()
    turtle.update()
    turtle.penup()

# ----------- OTHER FUNCTIONS -----------

def save_data(key, value):
    data = {}

    # Load existing JSON
    try:
        with open("feedback.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        # create structure if missing
        data = { key: [] }

    # Ensure the PID key exists
    if key not in data:
        data[key] = []

    # Append the feedback
    data[key].append(value)

    # Save updated JSON
    with open("feedback.json", "w") as f:
        json.dump(data, f, indent=4)


def feedback():
    input1 = turtle.textinput("feedback", "give us feedback:")
    turtle.listen()
    if input1 is not None:
        save_data("PID1", input1)
        print("Feedback saved.")
 
def gotoproject():
    input1 = turtle.numinput("projects","go to project:", 1)
    turtle.listen()
    global currentPID
    currentPID = input1

# ----------- KEYBINDS -----------
screen.onkeypress(right, "d")
screen.onkeypress(left, "a")
screen.onkeypress(up, "q")
screen.onkeypress(down, "e")
screen.onkeypress(zoom_in, "w")
screen.onkeypress(zoom_out, "s")
screen.onkeypress(rot_x_positive, "i")
screen.onkeypress(rot_x_negative, "k")
screen.onkeypress(rot_y_positive, "o")
screen.onkeypress(rot_y_negative, "u")
screen.onkeypress(rot_z_positive, "l")
screen.onkeypress(rot_z_negative, "j")

screen.onkeypress(feedback, "f")
screen.onkeypress(gotoproject, "z")

screen.listen()


turtle.mainloop()
