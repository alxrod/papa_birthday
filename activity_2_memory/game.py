import pygame
import random
import string
import requests

BASE_URL = "http://192.168.1.105:8000"

def get_answers():
    try:
        response = requests.get(f"{BASE_URL}/answers")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching answers: {e}")
        return None

def set_answer(team_id, answer):
    try:
        response = requests.post(
            f"{BASE_URL}/answer/{team_id}",
            json={"answer": answer}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error setting answer: {e}")
        return None
    
def reset_answers(teams):
    for team in teams:
        try:
            response = requests.post(
                f"{BASE_URL}/answer/{team}",
                json={"answer": ""}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error setting answer: {e}")
            return None

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1400, 1000  # Increased window size
MEMORY_SIZE = 64
BLOCK_SIZE = 10
PADDING = 150
NUM_TEAMS = 1

MODE = 1

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Memory Allocation Game")

# Fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

class MemoryRow:
    def __init__(self, y_pos, team_name):
        self.memory = [(0, WHITE, '')] * MEMORY_SIZE  # (allocation_round, color, id)
        self.y_pos = y_pos
        self.is_out = False
        self.score = 0
        self.team_name = team_name

    def allocate(self, size, address, allocation_round, color, block_id):
        if self.is_out or address < 0 or address + size > MEMORY_SIZE:
            return False
        
        # Check if all blocks in the range are free
        for i in range(address, address + size):
            if self.memory[i][2] != '':  # If any block is not free
                return False
        
        # Allocate memory blocks
        for i in range(address, address + size):
            self.memory[i] = (allocation_round, color, block_id)
        
        return True

    def free(self, address, block_id):
        start_address = -1
        for i in range(MEMORY_SIZE):
            if self.memory[i][2] == block_id:
                start_address = i
                break
        
        print("TRIED TO FREE AT ", address, " but it's actually at ", start_address)
        if start_address != address:
            return False
        
        # Free the memory blocks
        for i in range(start_address, MEMORY_SIZE):
            if self.memory[i][2] == block_id:
                self.memory[i] = (0, WHITE, '')
            else:
                break
        
        return True

    def get_max_free_space(self):
        max_space = 0
        current_space = 0
        for block in self.memory:
            if block[2] == '':  # Free space
                current_space += 1
                max_space = max(max_space, current_space)
            else:
                current_space = 0
        return max_space

    def get_allocated_blocks(self):
        blocks = set()
        for _, _, block_id in self.memory:
            if block_id:
                blocks.add(block_id)
        return list(blocks)

    def draw(self, surface):
        # Draw memory blocks
        for i, (_, color, block_id) in enumerate(self.memory):
            pygame.draw.rect(surface, color, (PADDING + i * BLOCK_SIZE, self.y_pos, BLOCK_SIZE, BLOCK_SIZE))
        
        # Draw labels for allocated blocks
        current_id = None
        start_index = 0
        for i, (_, _, block_id) in enumerate(self.memory):
            if block_id != current_id:
                if current_id:
                    self.draw_label(surface, current_id, start_index, i - 1)
                current_id = block_id
                start_index = i
        if current_id:
            self.draw_label(surface, current_id, start_index, len(self.memory) - 1)

        # Draw position labels
        self.draw_position_labels(surface)

        # Draw OUT label if the team is out
        if self.is_out:
            out_text = font.render("OUT", True, RED)
            text_rect = out_text.get_rect(center=(PADDING + MEMORY_SIZE * BLOCK_SIZE / 2, self.y_pos + BLOCK_SIZE / 2))
            surface.blit(out_text, text_rect)

        # Draw score
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        surface.blit(score_text, (WIDTH - 150, self.y_pos + BLOCK_SIZE / 2))

        # Draw team name
        team_name_text = font.render(self.team_name, True, WHITE)
        surface.blit(team_name_text, (10, self.y_pos + BLOCK_SIZE / 2))

    def draw_label(self, surface, block_id, start, end):
        if not block_id:
            return
        mid_point = (start + end) / 2
        label_x = PADDING + mid_point * BLOCK_SIZE
        label_y = self.y_pos - 15  # Position label above the block
        id_surface = small_font.render(block_id, True, WHITE)
        label_rect = id_surface.get_rect(center=(label_x, label_y))
        surface.blit(id_surface, label_rect)

    def draw_position_labels(self, surface):
        for i in range(0, MEMORY_SIZE, 4):
            label_x = PADDING + i * BLOCK_SIZE
            label_y = self.y_pos + BLOCK_SIZE + 10  # Position label below the memory row
            label_surface = small_font.render(str(i), True, WHITE)
            label_rect = label_surface.get_rect(center=(label_x, label_y))
            surface.blit(label_surface, label_rect)

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = WHITE
        self.text = text
        self.txt_surface = font.render(text, True, WHITE)  # Change text color to WHITE
        self.active = False
        self.placeholder = "Enter here"
        self.invalid = False
        self.complete = False
        self.message = ""

    def draw(self, screen):
        if self.text:
            self.txt_surface = font.render(self.text, True, WHITE)  # Render text in WHITE
            screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        else:
            placeholder_surface = small_font.render(self.placeholder, True, GRAY)
            screen.blit(placeholder_surface, (self.rect.x+5, self.rect.y+10))
        pygame.draw.rect(screen, self.color, self.rect, 2)
        
        color = RED
        if not self.invalid:
            color = GREEN

        msg_surface = small_font.render(self.message, True, color)
        screen.blit(msg_surface, (self.rect.x, self.rect.y - 20))
    
    def update(self, newText):
        if MODE == 2:
            self.text = newText
            self.txt_surface = font.render(self.text, True, WHITE)  # Render text in WHITE

class Button:
    def __init__(self, x, y, w, h, text, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.text = text
        self.txt_surface = font.render(text, True, BLACK)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def draw_game(screen, teams, input_boxes, allocation_size, free_id, restart_button, start_button, toggle_button, all_teams_out, action, show_visualization):
    screen.fill(BLACK)
    
    if show_visualization:
        for team in teams:
            team.draw(screen)

    if MODE == 1 and not all_teams_out:
        start_button.draw(screen)
    elif MODE == 2:
        for i, (team, box) in enumerate(zip(teams, input_boxes)):
            if not team.is_out:
                box.draw(screen)
        action_text = font.render(f"{action}: {allocation_size} bytes" if action == "Allocate" else f"Free Block {free_id}", True, WHITE)
        text_rect = action_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(action_text, text_rect)

        if all_teams_out:
            game_over_text = font.render("All teams out! Game Over!", True, RED)
            text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(game_over_text, text_rect)

    restart_button.draw(screen)
    toggle_button.draw(screen)
    pygame.display.flip()

def get_random_color():
    return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

def main():
    global MODE  # Declare MODE as global inside the main function
    team_names = ["cardiff", "comet", "mutiny", "macmillan"]
    row_height = 150
    teams = [MemoryRow(100 + i * row_height, team_names[i]) for i in range(NUM_TEAMS)]
    input_boxes = [InputBox(WIDTH - 200, 70 + i * row_height, 140, 32) for i in range(NUM_TEAMS)]
    restart_button = Button(WIDTH - 120, 10, 100, 40, "Restart", RED)
    start_button = Button(WIDTH // 2 - 50, 10, 150, 40, "Start Round", GREEN)
    toggle_button = Button(WIDTH - 360, 10, 190, 40, "TOGGLE VIEW", GREEN)

    allocation_size = get_alloc_size()
    
    free_id = ""

    MODE = 1  # Initialize MODE here, already done globally
    allocation_round = 0
    current_color = get_random_color()
    current_id = generate_id()
    allocation_ids = []
    
    clock = pygame.time.Clock()
    running = True

    all_teams_out = False
    action = "Allocate"
    round_finished_order = []
    show_visualization = True  # Start with visualizations visible

    while running:
        answers = get_answers()
        if answers:
            for i, team in enumerate(team_names):
                if i >= NUM_TEAMS:
                    break
                input_boxes[i].update(answers.get(team, ""))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.is_clicked(event.pos):
                    # Reset the game
                    teams = [MemoryRow(100 + i * row_height, team_names[i]) for i in range(NUM_TEAMS)]
                    input_boxes = [InputBox(WIDTH - 200, 70 + i * row_height, 140, 32) for i in range(NUM_TEAMS)]
                    allocation_size = get_alloc_size()
                    free_id = ""
                    allocation_round = 0
                    allocation_ids = []
                    current_color = get_random_color()
                    current_id = generate_id()
                    MODE = 1
                    all_teams_out = False
                    action = "Allocate"
                    round_finished_order = []
                    show_visualization = True  # Ensure visualization is visible after reset
                elif toggle_button.is_clicked(event.pos):
                    show_visualization = not show_visualization
                elif MODE == 1 and start_button.is_clicked(event.pos) and not all_teams_out:
                    # Randomly decide between allocation and free actions

                    average_max_free = 0
                    max_space = 0
                    for i, team in enumerate(teams):
                        team_max = team.get_max_free_space()
                        average_max_free += team_max
                        if team_max > max_space:
                            max_space = team_max

                    average_max_free /= NUM_TEAMS
                    print("Current average allocation space remaining: ", average_max_free, max_space, allocation_size)

                    if average_max_free > (MEMORY_SIZE * 0.5):
                        print("Less than 50% full so allocating")
                        print("Adding option ", current_id)
                        allocation_ids.append(current_id)
                        action = "Allocate"
                        
                    elif max_space < allocation_size:
                        print("Best team can't allocate so freeing")
                        action = "Free"
                        print("Free id options:  ", allocation_ids)
                        free_id = random.choice(allocation_ids)
                        while free_id == allocation_ids[-1]:
                            free_id = random.choice(allocation_ids)
                        print("Removing option ", free_id)
                        allocation_ids.remove(free_id)

                    elif random.choice([True, False]) and len(allocation_ids) > 1:
                        print("Best team can't allocate so freeing")
                        action = "Free"
                        print("Free id options:  ", allocation_ids)
                        free_id = random.choice(allocation_ids)
                        while free_id == allocation_ids[-1]:
                            free_id = random.choice(allocation_ids)
                        print("Removing option ", free_id)
                        allocation_ids.remove(free_id)
                        
                    else:
                        print("50/50 and allocating")
                        print("Adding option ", current_id)
                        allocation_ids.append(current_id)
                        action = "Allocate"
                        
                    MODE = 2
                    show_visualization = False  # Hide visualization during mode 2
                    for i, team in enumerate(teams):
                        if team.get_max_free_space() < allocation_size and action == "Allocate":
                            team.is_out = True
                        else:
                            input_boxes[i].invalid = False

                    # Check if all teams are out
                    all_teams_out = all(team.is_out for team in teams)

        if MODE == 2 and not all_teams_out:
            for i, (team, box) in enumerate(zip(teams, input_boxes)):
                if not team.is_out:
                    input_text = box.text
                    if input_text and input_text != "" and not box.complete:
                        print(input_text, box.complete)
                        if not input_text.isdigit():
                            box.invalid = True
                            box.message = "Not Addr"
                        elif action == "Allocate":
                            try:
                                address = int(input_text)
                                if team.allocate(allocation_size, address, allocation_round, current_color, current_id):
                                    box.message = 'Done'
                                    box.invalid = False
                                    box.complete = True
                                    if team not in round_finished_order:
                                        round_finished_order.append(team)
                                else:
                                    print("failed allocation")
                                    box.invalid = True
                                    box.message = 'Invalid'
                            except ValueError:
                                box.invalid = True
                                box.message = 'Invalid'
                        elif action == "Free":
                            block_address = int(input_text)
                            if team.free(block_address, free_id):
                                box.message = 'Freed'
                                box.invalid = False
                                box.complete = True
                                if team not in round_finished_order:
                                    round_finished_order.append(team)
                            else:
                                box.invalid = True
                                box.message = 'Invalid'
            
        draw_game(screen, teams, input_boxes, allocation_size, free_id, restart_button, start_button, toggle_button, all_teams_out, action, show_visualization)

        if MODE == 2 and all(team.is_out or box.complete for team, box in zip(teams, input_boxes)):

            print("RESET CALED")
            for box in input_boxes:
                box.complete = False
                box.update("")
                box.message = ""
                print("Text is: ", box.text)
                box.invalid = False
            reset_answers([team_names[i] for i in range(NUM_TEAMS)])


            MODE = 1
            show_visualization = True  # Show visualization during mode 1
            allocation_size = get_alloc_size()
            allocation_round += 1
            current_color = get_random_color()
            current_id = generate_id()

            # Award points based on order
            for idx, team in enumerate(round_finished_order):
                team.score += NUM_TEAMS - idx
            round_finished_order = []

        clock.tick(60)

    pygame.quit()

def get_alloc_size():
    return random.randint(4, 32)

def generate_id():
    return ''.join(random.choices(string.ascii_uppercase, k=2))

if __name__ == "__main__":
    main()