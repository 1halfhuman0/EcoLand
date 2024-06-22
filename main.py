import pygame
import sys
import random
import math

# Pygame 초기화
pygame.init()

# 화면 크기 설정 (전체 화면 모드)
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

# 맵 크기 설정 (화면보다 훨씬 크게 설정)
map_width = screen_width * 2
map_height = screen_height * 2

# 화면 제목 설정
pygame.display.set_caption("EcoWorld")

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CREATURE_COLOR = (0, 0, 255)
FOOD_COLOR = (0, 255, 0)
OUTSIDE_COLOR = (169, 169, 169)  # 회색 (맵 밖 영역)

# FPS 설정
clock = pygame.time.Clock()
fps = 60

# 카메라 초기 위치 및 확대/축소 설정
camera_x = 0
camera_y = 0
zoom = 1.0
min_zoom = 0.5
max_zoom = 2.0

# 드래그 상태 변수
dragging = False
drag_start_x = 0
drag_start_y = 0

# Creature 클래스 정의
class Creature:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 20
        self.speed = 2
        self.direction = random.randint(0, 359)  # 눈의 방향 (0도에서 359도 사이의 랜덤 각도)
        self.sight_radius = 100  # 시야 반경
        self.sight_angle = 120  # 시야 각도 (부채꼴의 각도)
        self.detect_range = self.sight_radius  # 먹이를 탐지할 수 있는 범위 (시야 반경과 동일하게 설정)
        self.change_direction_interval = 60  # 방향을 바꾸는 간격 (프레임 단위)
        self.change_direction_timer = self.change_direction_interval

    def move_towards(self, target_x, target_y):
        # 이동 방향을 먹이 방향으로 설정하는 함수
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        if distance != 0:
            self.direction = math.degrees(math.atan2(dy, dx))
        self.x += self.speed * math.cos(math.radians(self.direction))
        self.y += self.speed * math.sin(math.radians(self.direction))

    def random_move(self):
        self.change_direction_timer -= 1
        if self.change_direction_timer <= 0:
            # 왼쪽 혹은 오른쪽 방향으로 회전하도록 설정
            self.direction += random.choice([-45, 45])  # 45도씩 회전
            self.change_direction_timer = self.change_direction_interval  # 타이머 재설정

        radian_angle = math.radians(self.direction)
        self.x += math.cos(radian_angle) * self.speed
        self.y += math.sin(radian_angle) * self.speed

        # 맵 경계 조건 설정
        if self.x < 0:
            self.x = 0
            self.direction += 180  # 맵 경계에 닿으면 방향 전환
        elif self.x > map_width - self.size:
            self.x = map_width - self.size
            self.direction += 180  # 맵 경계에 닿으면 방향 전환

        if self.y < 0:
            self.y = 0
            self.direction += 180  # 맵 경계에 닿으면 방향 전환
        elif self.y > map_height - self.size:
            self.y = map_height - self.size
            self.direction += 180  # 맵 경계에 닿으면 방향 전환


    def move(self, foods):
        closest_food = None
        closest_distance = self.detect_range

        for food in foods:
            distance = ((self.x - food.x) ** 2 + (self.y - food.y) ** 2) ** 0.5
            if distance < closest_distance:
                closest_distance = distance
                closest_food = food

        if closest_food:
            self.move_towards(closest_food.x, closest_food.y)
            if abs(self.x - closest_food.x) < self.size and abs(self.y - closest_food.y) < self.size:
                foods.remove(closest_food)
                self.size += 5
        else:
            self.random_move()

    def draw(self, screen, camera_x, camera_y, zoom):
        pygame.draw.rect(screen, CREATURE_COLOR, 
                         ((self.x - camera_x) * zoom, 
                          (self.y - camera_y) * zoom, 
                          self.size * zoom, 
                          self.size * zoom))

    def draw_sight(self, screen, camera_x, camera_y, zoom):
        # 시야를 시각적으로 표현 (부채꼴)
        sight_color = (100, 100, 255, 100)  # 투명도가 있는 파란색
        start_angle = math.radians(-self.sight_angle / 2)
        end_angle = math.radians(self.sight_angle / 2)
        num_segments = int(self.sight_angle / 10)  # 부채꼴을 근사하기 위한 세그먼트 수

        vertices = []
        vertices.append((self.x * zoom - camera_x * zoom, self.y * zoom - camera_y * zoom))

        for i in range(num_segments + 1):
            angle = start_angle + (end_angle - start_angle) * (i / num_segments)
            dx = self.sight_radius * math.cos(angle)
            dy = self.sight_radius * math.sin(angle)
            rotated_dx = dx * math.cos(math.radians(self.direction)) - dy * math.sin(math.radians(self.direction))
            rotated_dy = dx * math.sin(math.radians(self.direction)) + dy * math.cos(math.radians(self.direction))
            target_x = (self.x + rotated_dx) * zoom - camera_x * zoom
            target_y = (self.y + rotated_dy) * zoom - camera_y * zoom
            vertices.append((target_x, target_y))

        pygame.draw.polygon(screen, sight_color, vertices)

# Food 클래스 정의
class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 10

    def draw(self, screen, camera_x, camera_y, zoom):
        pygame.draw.rect(screen, FOOD_COLOR, 
                         ((self.x - camera_x) * zoom, 
                          (self.y - camera_y) * zoom, 
                          self.size * zoom, 
                          self.size * zoom))

# 여러 Creature 인스턴스 생성
creatures = [Creature(random.randint(0, map_width-20), random.randint(0, map_height-20)) for _ in range(10)]

# 여러 Food 인스턴스 생성
foods = [Food(random.randint(0, map_width-10), random.randint(0, map_height-10)) for _ in range(100)]

# 게임 루프
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 좌클릭
                dragging = True
                drag_start_x, drag_start_y = event.pos
            elif event.button == 4:  # 마우스 휠 위
                zoom = min(max_zoom, zoom + 0.1)
            elif event.button == 5:  # 마우스 휠 아래
                zoom = max(min_zoom, zoom - 0.1)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # 좌클릭
                dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                dx, dy = event.rel
                camera_x -= dx / zoom
                camera_y -= dy / zoom

    # 화면 회색으로 채우기 (맵 밖 영역)
    screen.fill(OUTSIDE_COLOR)

    # 맵 영역만 흰색으로 채우기
    pygame.draw.rect(screen, WHITE, (max(0, -camera_x * zoom), max(0, -camera_y * zoom), min(screen_width, map_width * zoom - camera_x * zoom), min(screen_height, map_height * zoom - camera_y * zoom)))

    # Creature 이동 및 그리기
    for creature in creatures:
        creature.move(foods)
        creature.draw_sight(screen, camera_x, camera_y, zoom)
        creature.draw(screen, camera_x, camera_y, zoom)

    # Food 그리기
    for food in foods:
        food.draw(screen, camera_x, camera_y, zoom)

    # 화면 업데이트
    pygame.display.flip()

    # FPS 맞추기
    clock.tick(fps)

# Pygame 종료
pygame.quit()
sys.exit()
