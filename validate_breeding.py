# validate_breeding.py

# Runs 1,000 fake breeding trials through DinoInterpreter's real breeding
# logic and checks the results are statistically correct. Does not touch

# Must be run from the repo root, since dino_interpreter.py loads
# dinolution.tx using a path relative to the current folder.

import contextlib
import io
import math
import random
from collections import Counter

from dino_interpreter import Dino, DinoInterpreter

# Color dominance order, same as in DinoInterpreter._express_trait
COLOR_DOMINANCE = ['Red', 'Green', 'Blue', 'Yellow', 'Orange', 'Purple']

NUM_TRIALS = 1000


class _MutationBlock:
    # Stand-in for a textx BreedBlock node: no mutations happening at breed time
    def __init__(self):
        self.mutations = []


class _BreedStmt:
    # Stand-in for a textx BreedStmt node, just the fields _handle_breed reads
    def __init__(self, parent1, parent2):
        self.parent1 = parent1
        self.parent2 = parent2
        self.breedBlock = _MutationBlock()


def random_color_alleles():
    # A random list of 2 or 3 different colors for one parent
    count = random.choice([2, 3])
    return random.sample(COLOR_DOMINANCE, count)


def random_strength_alleles():
    # Two different random strength numbers for one parent
    # (kept different so we can tell which one got picked, for check 3)
    return random.sample(range(1, 21), 2)


def expected_dominant_color(alleles):
    # Walk the dominance order and return the first color present
    for color in COLOR_DOMINANCE:
        if color in alleles:
            return color
    raise ValueError(f"No known color in alleles: {alleles}")


def run_trials(n=NUM_TRIALS):
    # How many trials matched what we expected
    color_matches = 0
    strength_matches = 0

    # How often allele index 0 vs index 1 got picked, for lists of exactly 2
    color_choice_counts = Counter()
    strength_choice_counts = Counter()

    interp = DinoInterpreter()

    for i in range(n):
        # Build two random parents with multi-allele traits
        p1_color = random_color_alleles()
        p2_color = random_color_alleles()
        p1_strength = random_strength_alleles()
        p2_strength = random_strength_alleles()

        parent1 = Dino(f"P1_{i}", {'color': p1_color, 'strength': p1_strength})
        parent2 = Dino(f"P2_{i}", {'color': p2_color, 'strength': p2_strength})

        # Register the parents and breed them using the real interpreter logic
        interp.dinos = {parent1.name: parent1, parent2.name: parent2}
        interp._handle_breed(_BreedStmt(parent1.name, parent2.name))

        child = interp.dinos[f"{parent1.name}_{parent2.name}_child"]
        a1_color, a2_color = child.genotype['color']
        a1_strength, a2_strength = child.genotype['strength']

        # Check 1: child color should be the dominant one of the two alleles
        expected_color = expected_dominant_color([a1_color, a2_color])
        if child.traits['color'] == expected_color:
            color_matches += 1

        # Check 2: child strength should be floor of the average of the two alleles
        expected_strength = math.floor((a1_strength + a2_strength) / 2)
        if child.traits['strength'] == expected_strength:
            strength_matches += 1

        # Check 3: for 2-allele lists, track which index got chosen each time
        if len(p1_color) == 2:
            color_choice_counts[p1_color.index(a1_color)] += 1
        if len(p2_color) == 2:
            color_choice_counts[p2_color.index(a2_color)] += 1
        # strength lists are always length 2 by construction
        strength_choice_counts[p1_strength.index(a1_strength)] += 1
        strength_choice_counts[p2_strength.index(a2_strength)] += 1

    return {
        'trials': n,
        'color_matches': color_matches,
        'strength_matches': strength_matches,
        'color_choice_counts': color_choice_counts,
        'strength_choice_counts': strength_choice_counts,
    }


def main():
    # Run all the trials with the interpreter's normal print() output
    # swallowed, so only our summary shows up
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        results = run_trials(NUM_TRIALS)

    n = results['trials']
    color_pct = 100 * results['color_matches'] / n
    strength_pct = 100 * results['strength_matches'] / n

    cc = results['color_choice_counts']
    sc = results['strength_choice_counts']
    color_total = cc[0] + cc[1]
    strength_total = sc[0] + sc[1]
    color_idx0_pct = 100 * cc[0] / color_total if color_total else float('nan')
    color_idx1_pct = 100 * cc[1] / color_total if color_total else float('nan')
    strength_idx0_pct = 100 * sc[0] / strength_total if strength_total else float('nan')
    strength_idx1_pct = 100 * sc[1] / strength_total if strength_total else float('nan')

    # Print the final summary
    print(f"=== Breeding Validation Summary ({n} trials) ===")
    print()
    print("1. Color dominance hierarchy (Red > Green > Blue > Yellow > Orange > Purple):")
    print(f"   {results['color_matches']}/{n} matched expected dominant color ({color_pct:.2f}%)")
    print()
    print("2. Strength = floor((allele1 + allele2) / 2):")
    print(f"   {results['strength_matches']}/{n} matched exactly ({strength_pct:.2f}%)")
    print()
    print("3. random.choice() 50/50 split for 2-allele traits:")
    print(f"   color:    allele[0] picked {color_idx0_pct:.2f}% of the time, "
          f"allele[1] picked {color_idx1_pct:.2f}% of the time (n={color_total} draws)")
    print(f"   strength: allele[0] picked {strength_idx0_pct:.2f}% of the time, "
          f"allele[1] picked {strength_idx1_pct:.2f}% of the time (n={strength_total} draws)")


if __name__ == '__main__':
    main()
