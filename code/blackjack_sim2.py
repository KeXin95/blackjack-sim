import random
from collections import Counter
import json

# 1. Core Classes

class Card:
    SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    VALUES = {str(i): i for i in range(2, 11)}
    VALUES.update({'J': 10, 'Q': 10, 'K': 10, 'A': 11})

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.value = Card.VALUES[rank]

    def __str__(self):
        return f"{self.rank}"

    def __repr__(self):
        return str(self)

class Deck:
    def __init__(self, num_decks=6):
        self.num_decks = num_decks
        self.build()

    def build(self):
        self.cards = [Card(suit, rank)
                      for _ in range(self.num_decks)
                      for suit in Card.SUITS
                      for rank in Card.RANKS]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        if len(self.cards) == 0:
            self.build()
            self.shuffle()
        return self.cards.pop()

class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def get_value(self):
        value = sum(card.value for card in self.cards)
        num_aces = sum(1 for card in self.cards if card.rank == 'A')
        # Adjust for Aces
        while value > 21 and num_aces:
            value -= 10
            num_aces -= 1
        return value

    def __str__(self):
        return '-'.join(str(card) for card in self.cards)

    def is_blackjack(self):
        return len(self.cards) == 2 and self.get_value() == 21

    def is_soft(self):
        value = sum(card.value for card in self.cards)
        num_aces = sum(1 for card in self.cards if card.rank == 'A')
        return num_aces > 0 and value <= 21

# 2. Game Rules and Logic

def play_round(deck, strategy_func, betting_amount=10, betting_strategy=None, running_count=0, **strategy_args):
    # Deal initial hands
    player_hand = Hand()
    dealer_hand = Hand()
    player_hand.add_card(deck.deal())
    dealer_hand.add_card(deck.deal())
    player_hand.add_card(deck.deal())
    dealer_hand.add_card(deck.deal())

    cards_seen = player_hand.cards + dealer_hand.cards

    # Check for Blackjacks
    player_blackjack = player_hand.is_blackjack()
    dealer_blackjack = dealer_hand.is_blackjack()
    result = ''
    profit = 0

    def play_single_hand(hand, bet, allow_double=True, allow_split=True):
        nonlocal cards_seen
        # Handle splitting
        if allow_split and len(hand.cards) == 2 and hand.cards[0].rank == hand.cards[1].rank:
            action = strategy_func(hand, dealer_hand.cards[0], can_split=True, **strategy_args)
            if action == 'split':
                # Split into two hands
                hand1 = Hand()
                hand2 = Hand()
                hand1.add_card(hand.cards[0])
                hand2.add_card(hand.cards[1])
                hand1.add_card(deck.deal())
                hand2.add_card(deck.deal())
                cards_seen += [hand1.cards[1], hand2.cards[1]]
                # Play both hands recursively, but do not allow further splits for simplicity
                res1, prof1 = play_single_hand(hand1, bet, allow_double=True, allow_split=False)
                res2, prof2 = play_single_hand(hand2, bet, allow_double=True, allow_split=False)
                return (f"{str(hand1)}|{str(hand2)}", prof1 + prof2)
        # Handle doubling
        if allow_double and len(hand.cards) == 2:
            action = strategy_func(hand, dealer_hand.cards[0], can_double=True, **strategy_args)
            if action == 'double':
                card = deck.deal()
                hand.add_card(card)
                cards_seen.append(card)
                if hand.get_value() > 21:
                    return (str(hand), -2 * bet)
                # Dealer's turn
                dealer_final, dealer_val, dealer_cards = play_dealer()
                cards_seen += dealer_cards
                player_val = hand.get_value()
                if dealer_val > 21 or player_val > dealer_val:
                    return (str(hand), 2 * bet)
                elif player_val < dealer_val:
                    return (str(hand), -2 * bet)
                else:
                    return (str(hand), 0)
        # Normal play
        while True:
            action = strategy_func(hand, dealer_hand.cards[0], **strategy_args)
            if action == 'hit':
                card = deck.deal()
                hand.add_card(card)
                cards_seen.append(card)
                if hand.get_value() > 21:
                    return (str(hand), -bet)
            else:
                break
        # Dealer's turn
        dealer_final, dealer_val, dealer_cards = play_dealer()
        cards_seen += dealer_cards
        player_val = hand.get_value()
        if dealer_val > 21 or player_val > dealer_val:
            return (str(hand), bet)
        elif player_val < dealer_val:
            return (str(hand), -bet)
        else:
            return (str(hand), 0)

    def play_dealer():
        dealer = Hand()
        for c in dealer_hand.cards:
            dealer.add_card(c)
        dealer_cards = []
        while dealer.get_value() < 17 or (dealer.get_value() == 17 and dealer.is_soft()):
            card = deck.deal()
            dealer.add_card(card)
            dealer_cards.append(card)
        return (str(dealer), dealer.get_value(), dealer_cards)

    if player_blackjack and dealer_blackjack:
        result = 'push'
        profit = 0
    elif player_blackjack:
        result = 'win'
        profit = 1.5 * betting_amount
    elif dealer_blackjack:
        result = 'loss'
        profit = -betting_amount
    else:
        player_final, profit = play_single_hand(player_hand, betting_amount)
        result = 'win' if profit > 0 else ('loss' if profit < 0 else 'push')

    return {
        'player_hand': player_final if 'player_final' in locals() else str(player_hand),
        'player_final_value': player_hand.get_value(),
        'dealer_hand': str(dealer_hand),
        'dealer_final_value': dealer_hand.get_value(),
        'result': result,
        'profit': profit,
        'cards_seen': cards_seen,
    }

# 3. Player Playing Strategies

def strategy_mimic_dealer(player_hand, dealer_upcard, **kwargs):
    return 'hit' if player_hand.get_value() < 17 else 'stand'

def strategy_fixed_threshold(player_hand, dealer_upcard, threshold=15, **kwargs):
    return 'hit' if player_hand.get_value() < threshold else 'stand'

def strategy_dealer_weakness(player_hand, dealer_upcard, **kwargs):
    # Stand if dealer upcard is 2-6 and player has 12+, else hit
    if dealer_upcard.rank in ['2', '3', '4', '5', '6'] and player_hand.get_value() >= 12:
        return 'stand'
    return 'hit' if player_hand.get_value() < 17 else 'stand'

def strategy_basic(player_hand, dealer_upcard, can_double=False, can_split=False, **kwargs):
    # Full basic strategy for hard/soft hands and pairs, with double and split
    ranks = [card.rank for card in player_hand.cards]
    val = player_hand.get_value()
    up = dealer_upcard.rank
    # Splitting pairs
    if can_split and len(player_hand.cards) == 2 and ranks[0] == ranks[1]:
        pair = ranks[0]
        # Simplified pair splitting chart
        if pair in ['A', '8']:
            return 'split'
        if pair in ['2', '3', '7'] and up in ['2','3','4','5','6','7']:
            return 'split'
        if pair == '6' and up in ['2','3','4','5','6']:
            return 'split'
        if pair == '9' and up in ['2','3','4','5','6','8','9']:
            return 'split'
        if pair == '4' and up in ['5','6']:
            return 'split'
        if pair == '5' and up in ['2','3','4','5','6','7','8','9']:
            return 'double' if can_double else 'hit'
        if pair == '10':
            return 'stand'
    # Doubling down
    if can_double and len(player_hand.cards) == 2:
        # Soft hands (A + X)
        others = [r for r in ranks if r != 'A']
        other = others[0] if others else None
        if 'A' in ranks and other is not None:
            if other in ['2','3'] and up in ['5','6']:
                return 'double'
            if other in ['4','5'] and up in ['4','5','6']:
                return 'double'
            if other == '6' and up in ['3','4','5','6']:
                return 'double'
            if other == '7' and up in ['3','4','5','6']:
                return 'double'
        # Hard hands
        if val == 9 and up in ['3','4','5','6']:
            return 'double'
        if val == 10 and up in ['2','3','4','5','6','7','8','9']:
            return 'double'
        if val == 11 and up in ['2','3','4','5','6','7','8','9','10']:
            return 'double'
    # Standard basic strategy
    # Soft totals
    if 'A' in ranks and len(player_hand.cards) == 2:
        others = [r for r in ranks if r != 'A']
        other = others[0] if others else None
        if other is not None:
            if other in ['8','9','10']:
                return 'stand'
            if other == '7':
                if up in ['2','7','8']:
                    return 'stand'
                else:
                    return 'hit'
            if other == '6':
                if up in ['2','3','4','5','6']:
                    return 'stand'
                else:
                    return 'hit'
            if other in ['2','3','4','5']:
                if up in ['4','5','6']:
                    return 'stand'
                else:
                    return 'hit'
            if other in ['2','3'] and up in ['5','6']:
                return 'stand'
            return 'hit'
        else:
            # Both cards are Aces (after split): just hit (but play_single_hand will only allow one card)
            return 'hit'
    # Hard totals
    if val <= 11:
        return 'hit'
    elif val == 12:
        if up in ['4', '5', '6']:
            return 'stand'
        else:
            return 'hit'
    elif 13 <= val <= 16:
        if up in ['2', '3', '4', '5', '6']:
            return 'stand'
        else:
            return 'hit'
    else:
        return 'stand'

def strategy_card_counter(player_hand, dealer_upcard, running_count=0, **kwargs):
    # Use true count for deviations
    num_decks = kwargs.get('num_decks', 6)
    # Estimate decks remaining from hand size if available
    decks_remaining = max(kwargs.get('decks_remaining', 1), 1)
    true_count = running_count / decks_remaining
    val = player_hand.get_value()
    up = dealer_upcard.rank
    # Illustrious 18 deviations
    # Insurance: If true_count >= 3 and dealer upcard is Ace, take insurance
    if up == 'A' and true_count >= 3:
        return 'insurance'
    # 16 vs 10: stand if true_count >= 0
    if val == 16 and up == '10' and true_count >= 0:
        return 'stand'
    # 15 vs 10: stand if true_count >= 4
    if val == 15 and up == '10' and true_count >= 4:
        return 'stand'
    # 13 vs 2: hit if true_count <= -1
    if val == 13 and up == '2' and true_count <= -1:
        return 'hit'
    # 12 vs 3: hit if true_count <= 0
    if val == 12 and up == '3' and true_count <= 0:
        return 'hit'
    # 12 vs 2: stand if true_count >= 3
    if val == 12 and up == '2' and true_count >= 3:
        return 'stand'
    # Otherwise, follow basic strategy
    return strategy_basic(player_hand, dealer_upcard, **kwargs)

# 4. Betting Strategies

def betting_flat(base_bet, **kwargs):
    return base_bet

def betting_martingale(base_bet, last_result, current_bet, **kwargs):
    if last_result == 'loss':
        return current_bet * 2
    else:
        return base_bet

# 5. Card Counting Logic

def update_count(count, card):
    if card.rank in ['2', '3', '4', '5', '6']:
        return count + 1
    elif card.rank in ['10', 'J', 'Q', 'K', 'A']:
        return count - 1
    else:
        return count

# 6. Simulation Engine

def run_simulation(playing_strategy, num_games=100000, betting_strategy=betting_flat, base_bet=10, reshuffle_each_hand=True, **strategy_args):
    deck = Deck(num_decks=6)
    deck.shuffle()
    game_results = []
    running_count = 0
    last_result = None
    current_bet = base_bet
    cards_per_deck = 52
    total_cards = deck.num_decks * cards_per_deck
    for i in range(num_games):
        # Card Counter: only reshuffle when shoe is empty
        if playing_strategy == strategy_card_counter:
            if len(deck.cards) == 0:
                deck.build()
                deck.shuffle()
                running_count = 0
            # True count = running_count / decks_remaining
            decks_remaining = max(len(deck.cards) / 52, 1)
            true_count = running_count / decks_remaining
            # Improved bet spreading
            if true_count < 1:
                bet = 10
            elif true_count == 2:
                bet = 25
            elif true_count == 3:
                bet = 50
            elif true_count >= 4:
                bet = 100
            else:
                bet = 10
        else:
            if reshuffle_each_hand or len(deck.cards) < 52:
                deck.build()
                deck.shuffle()
                running_count = 0
            # Determine bet
            if betting_strategy == betting_martingale:
                bet = betting_strategy(base_bet, last_result, current_bet)
                current_bet = bet
            else:
                bet = betting_strategy(base_bet)
        # Play one round
        round_args = dict(strategy_args)
        round_args['running_count'] = running_count
        result = play_round(deck, playing_strategy, betting_amount=bet, betting_strategy=betting_strategy, **round_args)
        # Update running count
        for card in result['cards_seen']:
            running_count = update_count(running_count, card)
        # Store result
        result['bet'] = bet
        game_results.append(result)
        last_result = result['result']
    # Aggregate statistics
    total_profit = sum(r['profit'] for r in game_results)
    total_bet = sum(r['bet'] for r in game_results)
    num_wins = sum(1 for r in game_results if r['result'] == 'win')
    num_losses = sum(1 for r in game_results if r['result'] == 'loss')
    num_pushes = sum(1 for r in game_results if r['result'] == 'push')
    stats = {
        'num_games': num_games,
        'total_profit': total_profit,
        'total_bet': total_bet,
        'win_rate': num_wins / num_games,
        'loss_rate': num_losses / num_games,
        'push_rate': num_pushes / num_games,
        'avg_bet': sum(r['bet'] for r in game_results) / num_games,
        'max_bet': max(r['bet'] for r in game_results),
        'min_bet': min(r['bet'] for r in game_results),
    }
    return game_results, stats

# Helper to make game_results JSON serializable
def make_json_serializable(results):
    serializable = []
    for r in results:
        r_copy = dict(r)
        # Convert Card objects in cards_seen to strings
        r_copy['cards_seen'] = [str(card) for card in r_copy['cards_seen']]
        # player_hand and dealer_hand are already strings
        serializable.append(r_copy)
    return serializable


# 7. Main Execution Block
if __name__ == "__main__":
    strategies = [
        ("Mimic Dealer", strategy_mimic_dealer, {}),
        ("Dealer Weakness", strategy_dealer_weakness, {}),
        ("Basic", strategy_basic, {}),
        ("Card Counter", strategy_card_counter, {}),
    ]
    NUM_GAMES = 1_000_000
    STATS_DIR = "results"
    
    print("\n--- Blackjack Strategy Simulation Results ---\n")
    print(f"{'Strategy':<20} {'Games':>10} {'Profit':>12} {'Win%':>8} {'Loss%':>8} {'Push%':>8} {'AvgBet':>8} {'MaxBet':>8}")
    for name, strat, args in strategies:
        game_results, stats = run_simulation(strat, num_games=NUM_GAMES, base_bet=10, reshuffle_each_hand=True, **args)
        print(f"{name:<20} {stats['num_games']:>10,} ${stats['total_profit']:>12,.2f} {100*stats['win_rate']:>7.2f}% {100*stats['loss_rate']:>7.2f}% {100*stats['push_rate']:>7.2f}% {stats['avg_bet']:>8.2f} {stats['max_bet']:>8.2f}")
        # Save results to JSON
        filename = f"{STATS_DIR}/{name.replace(' ', '_').lower()}_results.json"
        with open(filename, 'w') as f:
            json.dump(make_json_serializable(game_results), f)
        print(f"Saved detailed results to {filename}")
        
    # Fixed Thresholds
    print("\nFixed Threshold Strategy (Threshold 12-20):")
    print(f"{'Threshold':<10} {'Profit':>12} {'Win%':>8} {'Loss%':>8} {'Push%':>8}")
    for threshold in range(12, 21):
        game_results, stats = run_simulation(strategy_fixed_threshold, num_games=NUM_GAMES, base_bet=10, reshuffle_each_hand=True, threshold=threshold)
        print(f"{threshold:<10,} ${stats['total_profit']:>12,.2f} {100*stats['win_rate']:>7.2f}% {100*stats['loss_rate']:>7.2f}% {100*stats['push_rate']:>7.2f}%")
        filename = f"{STATS_DIR}/fixed_threshold_{threshold}_results.json"
        with open(filename, 'w') as f:
            json.dump(make_json_serializable(game_results), f)
        print(f"Saved detailed results to {filename}")
        
    # Martingale system with Basic strategy
    print("\nMartingale Betting with Basic Strategy:")
    game_results, stats = run_simulation(strategy_basic, num_games=NUM_GAMES, base_bet=10, betting_strategy=betting_martingale, reshuffle_each_hand=True)
    print(f"{'Martingale':<10} ${stats['total_profit']:>12,.2f} {100*stats['win_rate']:>7.2f}% {100*stats['loss_rate']:>7.2f}% {100*stats['push_rate']:>7.2f}% {stats['avg_bet']:>8.2f} {stats['max_bet']:>8.2f}")
    filename = f"{STATS_DIR}/martingale_results.json"
    with open(filename, 'w') as f:
        json.dump(make_json_serializable(game_results), f)
    print(f"Saved detailed results to {filename}") 