# Simple Cinema Booking System

ROWS = 26
COLUMNS = 50
MOVIES = {
}
BOOKINGS = {}
NEXT_BOOKING_ID = 1


def create_seats(rows, cols):
    return [["." for _ in range(cols)] for _ in range(rows)]

def display_seats(seats):
    rows = len(seats)
    cols = len(seats[0])

    seat_display_width = 4 * cols + 4  # each seat takes up ~3 characters ("  1", " 25") + padding
    screen_label = "SCREEN"
    padding = max(0, (seat_display_width - len(screen_label)) // 2)

    print("Selected seats:")
    print("\n" + " " * padding + screen_label)
    print("-" * seat_display_width)
    
   

    for i in range(rows):
        row_label = chr(ord('A') + (rows - 1 - i))  # A at bottom, Z at top
        print(f"{row_label}  " + "  ".join(seats[i]))
    print("  " + " ".join(f"{i+1:>2}" for i in range(cols)))



def search_movie(movies):
    title = input("🔍 Enter movie title to search: ").strip().lower()
    if title in movies:
        print(f"\n🎬 Movie found: {movies[title]['title']}")
        display_seats(movies[title]['seats'])
    else:
        print("❌ Movie not found.")

def register_booking(movie_title, row_index, col_start, num_seats):
    global NEXT_BOOKING_ID
    booking_number = f"GIC{NEXT_BOOKING_ID:04d}" # keep to
    NEXT_BOOKING_ID += 1

    row_letter = chr(ord('A') + (len(MOVIES[movie_title]["seats"]) - 1 - row_index))
    seat_numbers = [col_start + i + 1 for i in range(num_seats)]
    BOOKINGS[booking_number] = {
        "movie": movie_title,
        "row": row_letter,
        "seats": seat_numbers
    }

    return booking_number


def find_best_seat_block(seats, num_seats):
    rows = len(seats)
    cols = len(seats[0])
    best_block = None
    best_distance = float("inf")

    for row_index in range(rows - 1, -1, -1):  # Start from back row
        for col_start in range(cols - num_seats + 1):
            if all(seats[row_index][col_start + i] == "." for i in range(num_seats)):
                block_center = col_start + (num_seats - 1) / 2
                row_center = (cols - 1) / 2
                distance = abs(block_center - row_center)

                if distance < best_distance:
                    best_distance = distance
                    best_block = (row_index, col_start)

    return best_block

def reserve_seats(seats, row_index, col_start, num_seats, symbol="o"):
    for i in range(num_seats):
        seats[row_index][col_start + i] = symbol


def book_seat(seats, num_seats, title):
    best_block = find_best_seat_block(seats, num_seats)
    if best_block:
        row_index, col_start = best_block
        reserve_seats(seats, row_index, col_start, num_seats)
        booking_number = register_booking(title, row_index, col_start, num_seats)
        print("✅ Seats booked successfully!")
        row_letter = chr(ord('A') + (len(seats) - 1 - row_index))
        for i in range(num_seats):
            print(f"  - Row {row_letter}, Seat {col_start + i + 1}")
        print(f"🎟️  Your booking number is: {booking_number}")
        return True
    return False

def display_booking_map(movie_title, booking_id):
    if booking_id not in BOOKINGS:
        print("❌ Booking ID not found.")
        return

    booking = BOOKINGS[booking_id]
    if booking["movie"] != movie_title:
        print("❌ Booking ID does not match the selected movie.")
        return

    seats = MOVIES[movie_title]["seats"]
    # Create a deep copy for display
    temp_seats = [row.copy() for row in seats]

    # Highlight the booking's seats with 'o'
    row_letter = booking["row"]
    row_index = len(temp_seats) - 1 - (ord(row_letter) - ord('A'))

    for seat in booking["seats"]:
        temp_seats[row_index][seat - 1] = "o"

    print(f"\nBooking {booking_id}:")
    display_seats(temp_seats)

def find_distributed_seats(seats, num_seats):
    allocated = []
    rows = len(seats)
    cols = len(seats[0])
    center = (cols - 1) / 2

    for row_index in range(rows - 1, -1, -1):  # Start from back row
        # Sort seat indices in the row by distance to center
        seat_order = sorted(range(cols), key=lambda c: abs(c - center))
        for col_index in seat_order:
            if seats[row_index][col_index] == ".":
                allocated.append((row_index, col_index))
                if len(allocated) == num_seats:
                    return allocated
    return None  # Not enough seats



def main():
    movie_input = input("Please define movie title and seating map in [Title] [Row] [SeatsPerRow] format (e.g. Inception 8 10): ")

    try:
        parts = movie_input.strip().split()
        title = " ".join(parts[:-2])
        rows = int(parts[-2])
        seats_per_row = int(parts[-1])
        if title not in MOVIES:
            MOVIES[title] = {"title": title, "seats": create_seats(rows, seats_per_row), "number_of_seats": rows * seats_per_row}
        seats = MOVIES[title]["seats"]

    except (ValueError, IndexError):
        print("❌ Invalid input format. Please enter: [title] [rows] [seats per row]")
        return

    while True:
        print(f"\nWelcome to GIC Cinemas")
        print(f"[1] Book tickets for {title} ({MOVIES[title]['number_of_seats']} seats available)")
        print("[2] Check bookings")
        print("[3] Exit")
        choice = input("Please enter your selection: ")

        if choice == "1":
            while True:
                num = input("Enter number of tickets to book, or enter blank to go back to main menu: ").strip()
                if num == "":
                    break  # Go back to main menu if the user enters blank
                try:
                    num = int(num)
                    if num <= 0:
                        print("❌ Invalid number of tickets. Please enter a positive number.")
                        continue
                    if num > MOVIES[title]["number_of_seats"]:
                        print(f"\nSorry, there are only {MOVIES[title]['number_of_seats']} seats available.")
                        continue  # Re-prompt the user if the number exceeds available seats

                    best_block = find_best_seat_block(seats, num)
                    if best_block:
                        row_index, col_start = best_block

                        # Create a deep copy of the seat map
                        temp_seats = [row.copy() for row in seats]
                        reserve_seats(temp_seats, row_index, col_start, num)

                        print(f"\nSuccessfully reserved seats for {num} {title} tickets.")

                        # Generate and display the booking number first
                        booking_number = f"GIC{NEXT_BOOKING_ID:04d}"
                        print(f"Booking id: {booking_number}")

                        display_seats(temp_seats)

                        confirm = input("Enter blank to accept seat selection, or enter a new seating position (e.g. C10): ").strip().upper()
                        if confirm == "":
                            reserve_seats(seats, row_index, col_start, num, symbol="#") # actual reservation
                            register_booking(title, row_index, col_start, num)
                            MOVIES[title]["number_of_seats"] -= num
                            print(f"Booking id: {booking_number} confirmed.")
                        else:
                            try:
                                # Parse new seat input (e.g., C10)
                                row_letter = confirm[0]
                                col_number = int(confirm[1:])

                                row_index_new = len(seats) - 1 - (ord(row_letter) - ord('A'))
                                col_start_new = col_number - 1

                                # Check if the new seat block is valid
                                if row_index_new < 0 or row_index_new >= len(seats):
                                    raise ValueError
                                if col_start_new < 0 or col_start_new + num > len(seats[0]):
                                    raise ValueError
                                if not all(seats[row_index_new][col_start_new + i] == "." for i in range(num)):
                                    print("❌ The selected block is not available.")
                                else:
                                    # Temporarily reserve the new block
                                    temp_seats = [row.copy() for row in seats]
                                    reserve_seats(temp_seats, row_index_new, col_start_new, num, symbol="o")
                                    print(f"\nNew seat selection preview:")
                                    display_seats(temp_seats)

                                    final_confirm = input("Enter blank to accept seat selection, or enter a new seating position (e.g. C10): ").strip()
                                    if final_confirm == "":
                                        reserve_seats(seats, row_index, col_start, num, symbol="#") # actual reservation
                                        register_booking(title, row_index_new, col_start_new, num)
                                        MOVIES[title]["number_of_seats"] -= num
                                        print(f"Booking id: {booking_number} confirmed.")
                                    else:
                                        print("❌ Booking cancelled.")
                            except Exception:
                                print("❌ Invalid seat input format or unavailable seats.")
                    else:
                        distributed = find_distributed_seats(seats, num)
                        if distributed:
                            # Preview map
                            temp_seats = [row.copy() for row in seats]
                            for r, c in distributed:
                                temp_seats[r][c] = "o"
                            display_seats(temp_seats)

                            confirm = input("Enter blank to accept distributed seating, or any key to cancel: ").strip()
                            if confirm == "":
                                for r, c in distributed:
                                    reserve_seats(seats, r, c, 1, symbol="#")
                                row_indices = [r for r, _ in distributed]
                                col_indices = [c for _, c in distributed]
                                # Register booking with first seat's position
                                booking_number = register_booking(title, row_indices[0], col_indices[0], num)
                                MOVIES[title]["number_of_seats"] -= num
                                print(f"Booking id: {booking_number} confirmed.")
                            else:
                                print("❌ Booking cancelled.")
                        else:
                            print("❌ Not enough seats available.")

                except ValueError:
                    print("❌ Invalid input. Please enter a number.")

        elif choice == "2":
            booking_id = input("Enter booking ID (e.g. GIC0001) or enter blank to go back to main menu ").strip().upper()
            if booking_id == '':
                continue
            display_booking_map(title, booking_id)

        elif choice == "3":
            print("Thank you for using GIC Cinemas system. Bye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
