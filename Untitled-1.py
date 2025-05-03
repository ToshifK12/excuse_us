import turtle

# Setup
screen = turtle.Screen()
screen.bgcolor("white")
pen = turtle.Turtle()
pen.hideturtle()
pen.speed(0)

def draw_circle(x, y, radius, color):
    pen.penup()
    pen.goto(x, y - radius)
    pen.pendown()
    pen.fillcolor(color)
    pen.begin_fill()
    pen.circle(radius)
    pen.end_fill()

def draw_heart(x, y, size, color):
    pen.penup()
    pen.goto(x, y)
    pen.pendown()
    pen.fillcolor(color)
    pen.begin_fill()
    pen.setheading(135)
    pen.forward(size)
    pen.circle(size * 0.5, 180)
    pen.setheading(-135)
    pen.circle(size * 0.5, 180)
    pen.forward(size)
    pen.end_fill()

def draw_eyes():
    draw_circle(-40, 80, 10, "black")
    draw_circle(-37, 85, 3, "white")  # sparkle
    draw_circle(40, 80, 10, "black")
    draw_circle(43, 85, 3, "white")   # sparkle

def draw_smile():
    pen.penup()
    pen.goto(-40, 40)
    pen.setheading(-60)
    pen.pendown()
    pen.pensize(5)
    pen.circle(50, 120)
    pen.pensize(1)

# Draw emoji face
draw_circle(0, 0, 100, "gold")
draw_eyes()
draw_smile()

# Draw heart
draw_heart(70, -70, 30, "red")

# Write message
pen.penup()
pen.goto(0, -160)
pen.color("darkblue")
pen.write("I saw you, and you seemed a little upset...", align="center", font=("Arial", 12, "normal"))
pen.goto(0, -180)
pen.write("so I just wanted to tell you:", align="center", font=("Arial", 12, "normal"))
pen.goto(0, -200)
pen.write("U tvom osmehu je svetlost koja leči. 💛", align="center", font=("Arial", 14, "bold"))

# Keep the window open
turtle.done()
