from textx import metamodel_from_file
import sys
import random

# MAX_FOOD limits how full a dino's food bar can get
MAX_FOOD = 10

# Load the grammar and build the metamodel
mm = metamodel_from_file('dinolution.tx')  # metamodel file must match your grammar

# Domain class for representing each dinosaur in the simulation
def class_repr(dino):
    return f"Dino(name='{dino.name}', traits={dino.traits}, food={dino.food})"

class Dino:
    def __init__(self, name, traits, food=10):
        # Basic metadata
        self.name = name
        self.traits = traits      # dict: trait_name -> value
        self.genotype = {}        # store inherited alleles during breeding
        self.food = food          # current food level
        self.alive = True         # alive status flag

    def __repr__(self):
        return class_repr(self)

class DinoInterpreter:
    def __init__(self):
        # Environment holds all dinos and functions in scope
        self.env = {
            'dinos': {},         # name -> Dino instance
            'functions': {}      # name -> FunctionDecl AST node
        }
        print("✨ DinoInterpreter initialized")  # debug print

    def run(self, model):
        # Entry point: visit every top-level statement
        print("➡️ Starting program execution...")
        for stmt in model.statements:
            self.visit(stmt)
        print("✅ Program execution complete")

    def visit(self, node):
        # Dispatch based on node class name
        method_name = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        # Called if no explicit visitor method is found
        raise NotImplementedError(f"No visitor method for {node.__class__.__name__}")

    def visit_Program(self, program):
        # Program node is just a container for statements
        print(f"📜 Program contains {len(program.statements)} statements")
        for stmt in program.statements:
            self.visit(stmt)

    def visit_DinoDecl(self, decl):
        # Create a new Dino from its declaration
        traits = {}
        for t in decl.traits:
            traits[t.name] = self._parse_value(t.value)
        new_dino = Dino(decl.name, traits)
        self.env['dinos'][decl.name] = new_dino
        # Pretty-print the DSL form back to the console
        print(f"dino {decl.name} {{")
        for t in decl.traits:
            print(f"  {t.name}: {t.value}")
        print("}")
        print(f"🦖 Created {new_dino}")

    def visit_FeedStmt(self, stmt):
        # Feed action: refuel food bar and buff strength
        dino_name = stmt.target
        if dino_name not in self.env['dinos']:
            print(f"❌ Error: Dino '{dino_name}' does not exist or is dead.")
            return
        current_dino = self.env['dinos'][dino_name]
        food_item = self._parse_value(stmt.food)
        print(f"🛠 Feeding {dino_name} with {food_item}")
        # Increase strength by 1
        old_strength = current_dino.traits.get('strength', 0)
        current_dino.traits['strength'] = old_strength + 1
        print(f"  strength: {old_strength} → {current_dino.traits['strength']}")
        # Refuel food bar
        old_food = current_dino.food
        # cap at MAX_FOOD
        current_dino.food = min(current_dino.food + 5, MAX_FOOD)
        print(f"  food: {old_food} → {current_dino.food}")

    def visit_TickStmt(self, stmt):
        # Tick action: advance time and decrease food levels
        print(f"⏱ Ticking {stmt.count} time(s)")
        for _ in range(stmt.count):
            # copy keys so we can delete while iterating
            for name, dino in list(self.env['dinos'].items()):
                if not dino.alive:
                    continue  # skip dead dinos
                dino.food -= 1
                print(f"  Tick: {name}.food → {dino.food}")
                if dino.food <= 0:
                    dino.alive = False
                    del self.env['dinos'][name]
                    print(f"💀 {name} has starved to death.")

    def visit_MutateStmt(self, stmt):
        # Mutate action: apply a change to a trait
        dino_name = stmt.target
        if dino_name not in self.env['dinos']:
            print(f"❌ Error: Dino '{dino_name}' does not exist.")
            return
        current_dino = self.env['dinos'][dino_name]
        mut = stmt.mutation
        op = mut.op or '='  # default assignment
        trait = mut.trait
        value = self._parse_value(mut.value, trait)
        old_val = current_dino.traits.get(trait)
        if old_val is None:
            print(f"❌ Error: Trait '{trait}' not found on {dino_name}.")
            return
        # Compute new value
        if op == '+':
            new_val = old_val + value
        elif op == '-':
            new_val = old_val - value
        elif op == '=':
            new_val = value
        else:
            print(f"❌ Unknown mutation operator '{op}'")
            return
        current_dino.traits[trait] = new_val
        print(f"🔄 Mutating {dino_name}.{trait} {op}{value} → {old_val} → {new_val}")

    def visit_BreedStmt(self, stmt):
        # Breed action: create a new child dino
        p1_name, p2_name = stmt.parent1, stmt.parent2
        if p1_name not in self.env['dinos'] or p2_name not in self.env['dinos']:
            print(f"❌ Error: One or both parents ('{p1_name}', '{p2_name}') not found.")
            return
        parent1 = self.env['dinos'][p1_name]
        parent2 = self.env['dinos'][p2_name]
        print(f"💑 Breeding {p1_name} x {p2_name}")
        # 1) Inherit alleles
        expressed = {}
        genotype = {}
        for trait, val1 in parent1.traits.items():
            val2 = parent2.traits.get(trait, val1)
            # pick one allele each
            a1 = random.choice(val1 if isinstance(val1, list) else [val1])
            a2 = random.choice(val2 if isinstance(val2, list) else [val2])
            genotype[trait] = [a1, a2]
            # express phenotype
            expressed[trait] = self._express_trait(trait, [a1, a2])
        # 2) Apply mutations in breed block
        for mut in stmt.breedBlock.mutations:
            op = mut.op or '='
            val = self._parse_value(mut.value, mut.trait)
            old = expressed.get(mut.trait)
            if isinstance(old, (int, float)):
                if op == '+': new = old + val
                elif op == '-': new = old - val
                else: new = val
                expressed[mut.trait] = new
                print(f"  Breed-mutate {mut.trait} {op}{val} → {old} → {new}")
            else:
                if op == '=':
                    expressed[mut.trait] = val
                    print(f"  Breed-mutate {mut.trait} = {val}")
        # 3) Create and register child
        child_name = f"{p1_name}_{p2_name}_child"
        child = Dino(child_name, expressed)
        child.genotype = genotype
        self.env['dinos'][child_name] = child
        print(f"🌟 Bred new dino {child}")
        print(f"  Genotype: {genotype}")

    def visit_FunctionDecl(self, stmt):
        # Register a user-made function
        fname = stmt.name
        self.env['functions'][fname] = stmt
        print(f"🔖 Registered function '{fname}'")

    def visit_IfStmt(self, stmt):
        # Conditional execution
        cond = stmt.condition
        result = self._eval_condition(cond)
        print(f"🔍 If {cond.dino}.{cond.trait} {cond.op} {cond.value} → {result}")
        if result:
            for s in stmt.block.statements:
                self.visit(s)
        elif hasattr(stmt, 'elseBlock') and stmt.elseBlock:
            print("🔄 Entering else block")
            for s in stmt.elseBlock.statements:
                self.visit(s)

    def visit_RepeatStmt(self, stmt):
        # Loop execution
        times = self._parse_value(stmt.count)
        print(f"🔁 Repeat {times} times")
        for i in range(times):
            print(f"  Iteration {i+1}")
            for s in stmt.block.statements:
                self.visit(s)

    def _eval_condition(self, cond):
        dino_obj = self.env['dinos'].get(cond.dino)
        if not dino_obj:
            print(f"❌ Error: Dino '{cond.dino}' not found for condition")
            return False
        left = dino_obj.traits.get(cond.trait)
        right = self._parse_value(cond.value)
        return eval(f"{left} {cond.op} {right}")

    def _parse_value(self, raw, trait_name=None):
        # Translate token to Python value
        if isinstance(raw, str) and raw == 'random':
            if trait_name == 'color':
                return random.choice(['Red','Orange','Yellow','Green','Blue','Purple'])
            return random.randint(1, 10)  # random stat
        if isinstance(raw, str) and raw.startswith('"') and raw.endswith('"'):
            return raw[1:-1]
        try:
            return int(raw)
        except (ValueError, TypeError):
            return raw

    def _express_trait(self, trait, alleles):
        # Decide phenotype from two alleles
        if trait == 'color':
            # Dominance order for colors
            order = ['Red','Green','Blue','Yellow','Orange','Purple']
            for c in order:
                if c in alleles:
                    return c
            return alleles[0]
        if trait == 'strength':
            return sum(alleles) // len(alleles)
        # default: pick first allele
        return alleles[0]

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python dino.py <model_file>")
        sys.exit(1)
    file_path = sys.argv[1]
    # Parse the model from the .dino file
    program_model = mm.model_from_file(file_path)
    # Create interpreter and run
    interp = DinoInterpreter()
    interp.run(program_model)
