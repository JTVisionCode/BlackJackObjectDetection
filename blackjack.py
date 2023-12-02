import tkinter as tk
from tkinter import PhotoImage, messagebox
from PIL import Image, ImageTk
import random
import os
import sys
import subprocess
import threading


class BlackjackGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack Game")

        # Set the window size
        # Adjust the width and height as needed
        self.root.geometry("530x820")

        # Set the background color to white
        self.root.configure(bg="white")

        # Initialize the deck
        self.deck = self.get_deck()

        # Initialize player and dealer hands
        self.player_hand = []
        self.dealer_hand = []

        # Create and pack the UI elements
        self.create_ui()

        # Start the game
        self.start_game()

    def run_stored_numbers_script_threaded(self):
        # Run the stored numbers script in a separate thread
        threading.Thread(target=self.run_stored_numbers_script).start()

    def restart_game(self):
        # Reset hands
        self.player_hand = []
        self.dealer_hand = []

        # Clear labels and images
        for label in self.player_frame.winfo_children():
            label.destroy()
        for label in self.dealer_frame.winfo_children():
            label.destroy()

        self.player_images = []
        self.dealer_images = []

        # Enable hit button
        self.hit_button["state"] = "normal"

        # Start a new game
        self.start_game()

    def get_deck(self):
        ranks = ['2', '3', '4', '5', '6', '7',
                 '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        deck = [{'rank': rank, 'suit': suit}
                for rank in ranks for suit in suits]
        random.shuffle(deck)
        return deck

    def create_ui(self):
        # Player frame
        self.player_frame = tk.Frame(self.root, bg="white")
        self.player_frame.grid(row=0, column=0, columnspan=5)

        self.player_label = tk.Label(
            self.player_frame, text="Player's Hand", bg="white")
        self.player_label.grid(row=0, column=0, columnspan=5)

        self.player_images = []

        # Dealer frame
        self.dealer_frame = tk.Frame(self.root, bg="white")
        self.dealer_frame.grid(row=1, column=0, columnspan=5)

        self.dealer_label = tk.Label(
            self.dealer_frame, text="Dealer's Hand", bg="white")
        self.dealer_label.grid(row=0, column=0, columnspan=5)

        self.dealer_images = []

        # Buttons (inside the player frame)
        self.hit_button = tk.Button(
            self.root, text="Hit", command=self.hit, bd=5, bg="grey", fg="white", width=5, height=1, relief=tk.RAISED)
        self.hit_button.grid(row=2, column=0, pady=20, columnspan=5)

        # self.stand_button = tk.Button(
        # self.player_frame, text="Stand", command=self.stand, bd=0, bg="grey")
        # self.stand_button.grid(row=2, column=2, padx=5, pady=5, columnspan=2)

    def start_game(self):
        # Create UI elements only if it's the beginning of the game
        if not self.player_hand and not self.dealer_hand:
            # Deal initial cards
            self.deal_card(self.player_hand, self.player_images,
                           self.player_frame)
            self.deal_card(self.dealer_hand, self.dealer_images,
                           self.dealer_frame)
            self.deal_card(self.player_hand, self.player_images,
                           self.player_frame)
            self.deal_card(self.dealer_hand, self.dealer_images,
                           self.dealer_frame, hidden=True)

            # Print hands after dealing
            print("Player's Hand:", self.player_hand)
            print("Dealer's Hand:", self.dealer_hand)

            # Run the stored numbers script
            self.run_stored_numbers_script_threaded()

    def deal_card(self, hand, image_list, frame, hidden=False):
        card = self.deck.pop()
        hand.append(card)

        folder_name = "cardimages"
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(
            current_dir, folder_name, f"{card['rank'].lower()}_{card['suit']}.png")

        try:
            image = Image.open(image_path)
        except FileNotFoundError:
            print("Error: File not found.")
            return

        new_size = (int(image.width * 0.5), int(image.height * 0.5))
        image = image.resize(new_size, Image.LANCZOS)
        photo_image = ImageTk.PhotoImage(image)

        image_list.append(photo_image)

        label = tk.Label(frame, image=photo_image)
        label.photo = photo_image

        # Determine the position based on the number of cards already in the hand
        position = len(hand)

        # Place the label in the grid
        label.grid(row=1, column=position, padx=5)

        # Update the GUI
        self.root.update_idletasks()
        self.root.geometry("")  # Force window resizing

        # Uncomment the line below if you want to center the window on the screen after resizing
        self.center_window()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def hit(self):
        self.deal_card(self.player_hand, self.player_images, self.player_frame)

        # Check for bust
        if self.calculate_hand_value(self.player_hand) > 21:
            messagebox.showinfo("Bust", "You busted! Dealer wins.")
            self.hit_button["state"] = "disabled"
            self.restart_game()

    def stand(self):
        # Reveal the dealer's hidden card
        self.dealer_images[0] = ImageTk.PhotoImage(
            Image.open(f"cardimages/{self.dealer_hand[0]['rank'].lower()}_{self.dealer_hand[0]['suit']}.png"))
        self.dealer_label.configure(text="Dealer's Hand")

        # Dealer hits until they have 17 or more points
        while self.calculate_hand_value(self.dealer_hand) < 17:
            self.deal_card(self.dealer_hand, self.dealer_images,
                           self.dealer_frame)

        # Determine the winner
        player_value = self.calculate_hand_value(self.player_hand)
        dealer_value = self.calculate_hand_value(self.dealer_hand)

        if player_value > 21 or (dealer_value <= 21 and dealer_value >= player_value):
            result = "Dealer wins!"
        else:
            result = "Player wins!"

        messagebox.showinfo("Game Over", result)

        # Disable buttons after the game is over
        self.hit_button["state"] = "disabled"
        # self.stand_button["state"] = "disabled"

    def calculate_hand_value(self, hand):
        value = 0
        num_aces = 0

        for card in hand:
            if card['rank'] == 'A':
                num_aces += 1
                value += 11
            elif card['rank'] in ['K', 'Q', 'J']:
                value += 10
            else:
                value += int(card['rank'])

        while value > 21 and num_aces:
            value -= 10
            num_aces -= 1

        return value

    def run_stored_numbers_script(self):
        script_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "storednumbers.py"
        )
        try:
            subprocess.run([sys.executable, script_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running {script_path}: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    game = BlackjackGame(root)
    root.mainloop()
