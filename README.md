# Dino-lution
Dino-lution is a domain-specific language for simulating and interacting with virtual dinosaurs. Programs start by declaring named dinos with traits like species, color, strength, and food. Time is indicated through a 'tick' statement that decrease each dino’s food. The 'feed' actions can restore this food and boost the strenght trait. You can mutate traits directly using mutate statement or breed pairs of dinos to inherit and combine parental alleles into a new child. 

In this repository is:
* dinolution.tx: The TextX grammar defining the language syntax.
* dinolution_interpreter.py: The python interpreter that parses and executes the .dino programs.
* Example ".dino" programs that show off features like loops, feeding, mutation, and breeding.

# Programs

* feed_example.dino:

A simple program that defines a single dino (Sunny) and feeds it twice. Shows how the feed statement increases both strength and food (capped by MAX_FOOD).

![Image](https://github.com/user-attachments/assets/92dacb6b-038f-45b8-92de-93c6bb66fe9b)

* feed_example output:

![Image](https://github.com/user-attachments/assets/28e91843-23b1-4eb3-b942-efc8c9135c4a)


* breed_example.dino:

A minimal breeding scenario with two parent dinos, demonstrating genotype inheritance and phenotype expression.

![Image](https://github.com/user-attachments/assets/0ec5a192-d6fa-46a6-bc0b-9737e23f1b46)

* breed_example output:

* Parents Creation:
  - A: strength=4, color=Blue
  - B: strength=6, color=Red
* Breeding (breed(A, B)):
  - Genotype: Each trait inherits one allele from each parent:
     - species: ["Raptor", "Raptor"]
     - color:   ["Blue", "Red"]
     - strength: [4, 6]
  -Phenotype Expression:
     - species: always "Raptor"
     - color: picks the first matching in [Red, Green, etc] ordering
     - strength: average of [4,6] → 5
  - Child Creation: A new dino A_B_child appears with traits {species: Raptor, color: Red, strength: 5} and default food=10.

![Image](https://github.com/user-attachments/assets/718de8c9-4cef-427e-a093-bb8be92c03a1)


* complex_example.dino:

A multi-step scenario involving three dinos: Spike, Alpha, and Beta.

1.) Initialization: Three dinos are created with different starting strength and food levels.

2.) Survival Loop (repeat 3 times):
* Feed Spike before time passes, boosting its strength and food (capped at MAX_FOOD).
* Tick 1 decrements all dinos’ food by 1. Since Alpha and Beta are never fed in the loop, they drop below zero and die on the first tick. Spike survives because it was fed first.
* Conditional Feed checks if Spike’s food < 6 and tops off if needed (never triggered after iteration 1).

3.) Post-loop Feeding: Alpha and Beta have already died, so subsequent feed calls for them produce error messages. Only Spike remains.

4.) Breeding Attempts: Three breed statements run in sequence, but since Alpha and Beta are dead, each prints a “parents not found” error.

5.) Final Tick & Feed:
* tick 5 further reduces Spike’s food over five time units.
* A final feed(Spike, "plants") replenishes Spike so it ends the program alive.

![Image](https://github.com/user-attachments/assets/3fb2be7b-4d59-493b-88c2-16d857caba97)

* complex_example output:

![Image](https://github.com/user-attachments/assets/6c5ba9f4-006f-4d3e-ae31-71074b28fe64)

* Lines 1–10: Dino declarations and creation logs.
* Lines 12–22: Loop iterations showing feed → tick → conditional, with Alpha/Beta starvations.
* Lines 24–26: Errors when feeding dead dinos.
* Lines 28–36: Errors for breeding dead parents.
* Lines 38–44: Final tick and feed sequence for Spike.
