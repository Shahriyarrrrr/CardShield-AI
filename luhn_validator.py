def luhn_check(card_number):
    
    # REMOVE SPACES
    card_number = card_number.replace(" ", "")

    # MUST BE ONLY DIGITS
    if not card_number.isdigit():
        return False

    total = 0
    reverse_digits = card_number[::-1]

    for index, digit in enumerate(reverse_digits):

        n = int(digit)

        # DOUBLE EVERY SECOND DIGIT
        if index % 2 == 1:
            n = n * 2

            # IF GREATER THAN 9
            if n > 9:
                n = n - 9

        total += n

    # VALID IF DIVISIBLE BY 10
    return total % 10 == 0


# TEST NUMBERS

test_cards = [
    "4532015112830366",   # VALID VISA
    "5555555555554444",   # VALID MASTERCARD
    "1234567890123456"    # FAKE CARD
]

print("\n===== LUHN VALIDATION RESULTS =====\n")

for card in test_cards:

    if luhn_check(card):
        print(f"{card} --> VALID CARD")
    else:
        print(f"{card} --> INVALID CARD")