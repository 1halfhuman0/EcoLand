import pygame
import sys
import random

# Pygame 초기화
pygame.init()

# 화면 크기 설정
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# 화면 제목 설정
pygame.display.set_caption("EcoWorld")

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CREATURE_COLOR = (0, 0, 255)

# FPS 설정
clock = pygame.time.Clock()
fps = 60

# Creature 클래스 정의
class Creature:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 20
        self.speed = 5

    def move(self):
        self.x += random.choice([-1, 0, 1]) * self.speed
        self.y += random.choice([-1, 0, 1]) * self.speed

        # 화면 경계 조건 설정
        if self.x < 0:
            self.x = 0
        elif self.x > screen_width - self.size:
            self.x = screen_width - self.size

        if self.y < 0:
            self.y = 0
        elif self.y > screen_height - self.size:
            self.y = screen_height - self.size

    def draw(self, screen):
        pygame.draw.rect(screen, CREATURE_COLOR, (self.x, self.y, self.size, self.size))

# 여러 Creature 인스턴스 생성
creatures = [Creature(random.randint(0, screen_width-20), random.randint(0, screen_height-20)) for _ in range(10)]

# 게임 루프
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 화면 흰색으로 채우기
    screen.fill(WHITE)

    # Creature 이동 및 그리기
    for creature in creatures:
        creature.move()
        creature.draw(screen)

    # 화면 업데이트
    pygame.display.flip()

    # FPS 맞추기
    clock.tick(fps)

# Pygame 종료
pygame.quit()
sys.exit()