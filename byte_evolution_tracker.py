import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

def draw_dot():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluLookAt(10, 10, 20,  10, 10, 0,  0, 1, 0)

    glPushMatrix()
    glColor3f(1.0, 0.0, 0.0)  # Red dot
    glTranslatef(10, 10, 0)
    quad = gluNewQuadric()
    gluSphere(quad, 0.5, 16, 16)
    gluDeleteQuadric(quad)
    glPopMatrix()

    pygame.display.flip()

def main():
    pygame.init()
    pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    glClearColor(0, 0, 0, 1)
    glEnable(GL_DEPTH_TEST)
    gluPerspective(45, (800/600), 0.1, 100.0)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False

        draw_dot()
        pygame.time.wait(16)

    pygame.quit()

if __name__ == "__main__":
    main()
