# dino_interpreter.py
from textx import metamodel_from_file
import sys
import random

# Maximum food a dino can have
MAX_FOOD = 10

# Load the TextX metamodel from the grammar file
mm = metamodel_from_file('dinolution.tx')

class Dino:
    """
    Simple Dino class representing a dinosaur in our simulation.
    """
    def __init__(self, name, traits, food=10):
        self.name = name
        self.traits = traits  # a dict of trait_name -> value
        self.food = food      # current food level
        self.genotype = {}    # stores alleles after breeding
        self.alive = True     # alive status

    def __repr__(self):
        return "Dino(name='{}', traits={}, food={})".format(
            self.name, self.traits, self.food
        )

class DinoInterpreter:
    """
    A basic interpreter for Dino-lution programs.
    Written in a straightforward style, like a junior CS student.
    """
    def __init__(self):
        # Environment: dinos and functions
        self.dinos = {}       # name -> Dino
        self.functions = {}   # name -> FunctionDecl node
        # Expression class from metamodel for eval
        self.Expr = mm['Expr']
        print("✨ DinoInterpreter initialized")

    def run(self, model):
        """Run the program (model) loaded by TextX."""
        print("➡️ Starting program execution...")
        for stmt in model.statements:
            self.execute(stmt)
        print("✅ Program execution complete")

    def execute(self, node):
        """Dispatch method based on node type."""
        typ = node.__class__.__name__
        if typ == 'Program':
            self._handle_program(node)
        elif typ == 'DinoDecl':
            self._handle_dino_decl(node)
        elif typ == 'FeedStmt':
            self._handle_feed(node)
        elif typ == 'TickStmt':
            self._handle_tick(node)
        elif typ == 'MutateStmt':
            self._handle_mutate(node)
        elif typ == 'BreedStmt':
            self._handle_breed(node)
        elif typ == 'FunctionDecl':
            self._handle_function_decl(node)
        elif typ == 'IfStmt':
            self._handle_if(node)
        elif typ == 'RepeatStmt':
            self._handle_repeat(node)
        else:
            print(f"⚠️ No handler for node type: {typ}")

    def _handle_program(self, program):
        for s in program.statements:
            self.execute(s)

    def _handle_dino_decl(self, d):
        # Collect traits
        traits = {}
        for t in d.traits:
            traits[t.name] = self._parse_value(t.value)
        # Initial food if given
        start_food = getattr(d, 'initFood', 10)
        dino = Dino(d.name, traits, start_food)
        self.dinos[d.name] = dino
        print(f"🦖 Created dino {dino}")

    def _handle_feed(self, f):
        name = f.target
        if name not in self.dinos:
            print(f"❌ Error: Dino '{name}' not found.")
            return
        d = self.dinos[name]
        amount = self._parse_value(f.food)
        print(f"🛠 Feeding {name} with {amount}")
        # Increase strength and food
        old_str = d.traits.get('strength', 0)
        d.traits['strength'] = old_str + 1
        print(f"  strength: {old_str} -> {d.traits['strength']}")
        old_food = d.food
        d.food = min(d.food + 5, MAX_FOOD)
        print(f"  food: {old_food} -> {d.food}")

    def _handle_tick(self, t):
        count = int(t.count)
        print(f"⏱ Ticking {count} time(s)")
        for _ in range(count):
            # Use list to avoid runtime change during iteration
            for name in list(self.dinos.keys()):
                d = self.dinos[name]
                if not d.alive:
                    continue
                d.food -= 1
                print(f"  {name}.food -> {d.food}")
                if d.food <= 0:
                    d.alive = False
                    del self.dinos[name]
                    print(f"💀 {name} has starved.")

    def _handle_mutate(self, m):
        name = m.target
        if name not in self.dinos:
            print(f"❌ Error: Dino '{name}' not found.")
            return
        d = self.dinos[name]
        op = m.mutation.op or '='
        trait = m.mutation.trait
        val = self._parse_value(m.mutation.value)
        old = d.traits.get(trait)
        if old is None:
            print(f"❌ Trait '{trait}' not on {name}.")
            return
        if op == '+': new = old + val
        elif op == '-': new = old - val
        else: new = val
        d.traits[trait] = new
        print(f"🔄 Mutated {name}.{trait} {op}{val}: {old} -> {new}")

    def _handle_breed(self, b):
        p1, p2 = b.parent1, b.parent2
        if p1 not in self.dinos or p2 not in self.dinos:
            print("❌ Error: Parents not found.")
            return
        print(f"💑 Breeding {p1} x {p2}")
        d1 = self.dinos[p1]
        d2 = self.dinos[p2]
        child_traits = {}
        genotype = {}
        # Inherit traits
        for tr in d1.traits:
            v1 = d1.traits[tr]
            v2 = d2.traits.get(tr, v1)
            alleles1 = v1 if isinstance(v1, list) else [v1]
            alleles2 = v2 if isinstance(v2, list) else [v2]
            a1 = random.choice(alleles1)
            a2 = random.choice(alleles2)
            genotype[tr] = [a1, a2]
            child_traits[tr] = self._express_trait(tr, [a1, a2])
        # Apply breed-time mutations
        for mut in b.breedBlock.mutations:
            op = mut.op or '='
            tr2 = mut.trait
            vv = self._parse_value(mut.value)
            old = child_traits.get(tr2)
            if isinstance(old, (int, float)):
                if op == '+': new = old + vv
                elif op == '-': new = old - vv
                else: new = vv
            else:
                new = vv
            child_traits[tr2] = new
            print(f"  Breed-mutate {tr2} {op}{vv}: {old} -> {new}")
        # Create child dino
        child_name = f"{p1}_{p2}_child"
        child = Dino(child_name, child_traits)
        child.genotype = genotype
        self.dinos[child_name] = child
        print(f"🌟 New dino {child}")
        print(f"  Genotype: {genotype}")

    def _handle_function_decl(self, fn):
        self.functions[fn.name] = fn
        print(f"🔖 Function declared: {fn.name}")

    def _handle_if(self, i):
        left = self._eval_expr(i.condition.left)
        right = self._eval_expr(i.condition.right)
        op = i.condition.op
        cond = False
        # Simple comparison
        if op == '==': cond = (left == right)
        elif op == '!=': cond = (left != right)
        elif op == '>': cond = (left > right)
        elif op == '<': cond = (left < right)
        elif op == '>=': cond = (left >= right)
        elif op == '<=': cond = (left <= right)
        print(f"🔍 If {left} {op} {right} -> {cond}")
        if cond:
            for s in i.block.statements:
                self.execute(s)
        elif hasattr(i, 'elseBlock') and i.elseBlock:
            for s in i.elseBlock.statements:
                self.execute(s)

    def _handle_repeat(self, r):
        times = self._eval_expr(r.count)
        print(f"🔁 Repeat {times} times")
        for idx in range(times):
            print(f"  Iteration {idx + 1}")
            for s in r.block.statements:
                self.execute(s)

    def _eval_expr(self, expr):
        """Recursively evaluate Expr nodes or simple values."""
        # Handle Expr from metamodel
        if isinstance(expr, self.Expr):
            value = self._eval_expr(expr.head)
            for op, r in zip(expr.binop, expr.right):
                right_val = self._eval_expr(r)
                if op == '+': value += right_val
                elif op == '-': value -= right_val
                elif op == '*': value *= right_val
                elif op == '/': value //= right_val
                elif op == '%': value %= right_val
            return value
        # Integers
        if isinstance(expr, int):
            return expr
        # Digit strings
        if isinstance(expr, str) and expr.isdigit():
            return int(expr)
        # Variables or random
        return self._resolve_variable(expr)

    def _resolve_variable(self, var):
        """Resolve variables like DinoName.trait or raw values."""
        if var == 'random':
            return random.randint(1, 10)
        if isinstance(var, str) and var.startswith('"'):
            return var.strip('"')
        if isinstance(var, str) and '.' in var:
            name, tr = var.split('.')
            if name in self.dinos and tr in self.dinos[name].traits:
                return self.dinos[name].traits[tr]
            else:
                raise ValueError(f"Unknown variable {var}")
        # Fallback
        try:
            return int(var)
        except:
            return var

    def _parse_value(self, v):
        """Parse raw values from the AST (int, string, random)."""
        if v == 'random':
            return random.randint(1, 10)
        if isinstance(v, str) and v.isdigit():
            return int(v)
        if isinstance(v, str) and v.startswith('"'):
            return v.strip('"')
        return v

    def _express_trait(self, trait, alleles):
        """Simple genetic expression rules."""
        if trait == 'color':
            # Prioritize known colors
            for c in ['Red','Green','Blue','Yellow','Orange','Purple']:
                if c in alleles:
                    return c
        if trait == 'strength':
            return sum(alleles) // len(alleles)
        return alleles[0]

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python dino_interpreter.py <model_file>")
        sys.exit(1)
    model = mm.model_from_file(sys.argv[1])
    interp = DinoInterpreter()
    interp.run(model)
