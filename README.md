# Dino-lution
Dino-lution is a domain-specific language for simulating and interacting with virtual dinosaurs. In this repository is:
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

![Image](https://github.com/user-attachments/assets/0ec5a192-d6fa-46a6-bc0b-9737e23f1b46)

* breed_example output:

![Image](https://github.com/user-attachments/assets/718de8c9-4cef-427e-a093-bb8be92c03a1)


* complex_example.dino:

A more complex scenario with three dinos. Demonstrates:

* Loops (repeat ... times) combined with tick and conditional feed to sustain dinos.
* Feeding multiple dinos.
* Breeding with trait mutations.
* Final tick and feed to observe post-breeding status.

![Image](https://github.com/user-attachments/assets/3fb2be7b-4d59-493b-88c2-16d857caba97)

* complex_example output:

![Image](https://github.com/user-attachments/assets/6c5ba9f4-006f-4d3e-ae31-71074b28fe64)
