# elements_study.py
#!/usr/bin/env python3
"""
⚛️ Element Master – Learn Chemistry Elements (Python Edition)
Advanced: complete element DB, favorites, quiz, spaced repetition, stats
"""

import json
import os
import sys
import random
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  Install 'rich' for enhanced UI: pip install rich")


# ─── Element Database ──────────────────────────────────────────────────────

@dataclass
class Element:
    symbol: str
    name: str
    number: int
    period: int
    group: str
    category: str
    mass: float
    electron_config: str

# Pre‑populated list of 118 elements (simplified)
ELEMENTS_DATA = [
    # 1‑20
    Element("H", "Hydrogen", 1, 1, "1", "Nonmetal", 1.008, "1s1"),
    Element("He", "Helium", 2, 1, "18", "Noble gas", 4.0026, "1s2"),
    Element("Li", "Lithium", 3, 2, "1", "Alkali metal", 6.94, "[He]2s1"),
    Element("Be", "Beryllium", 4, 2, "2", "Alkaline earth metal", 9.0122, "[He]2s2"),
    Element("B", "Boron", 5, 2, "13", "Metalloid", 10.81, "[He]2s2 2p1"),
    Element("C", "Carbon", 6, 2, "14", "Nonmetal", 12.011, "[He]2s2 2p2"),
    Element("N", "Nitrogen", 7, 2, "15", "Nonmetal", 14.007, "[He]2s2 2p3"),
    Element("O", "Oxygen", 8, 2, "16", "Nonmetal", 15.999, "[He]2s2 2p4"),
    Element("F", "Fluorine", 9, 2, "17", "Halogen", 18.998, "[He]2s2 2p5"),
    Element("Ne", "Neon", 10, 2, "18", "Noble gas", 20.180, "[He]2s2 2p6"),
    Element("Na", "Sodium", 11, 3, "1", "Alkali metal", 22.990, "[Ne]3s1"),
    Element("Mg", "Magnesium", 12, 3, "2", "Alkaline earth metal", 24.305, "[Ne]3s2"),
    Element("Al", "Aluminium", 13, 3, "13", "Post‑transition metal", 26.982, "[Ne]3s2 3p1"),
    Element("Si", "Silicon", 14, 3, "14", "Metalloid", 28.085, "[Ne]3s2 3p2"),
    Element("P", "Phosphorus", 15, 3, "15", "Nonmetal", 30.974, "[Ne]3s2 3p3"),
    Element("S", "Sulfur", 16, 3, "16", "Nonmetal", 32.06, "[Ne]3s2 3p4"),
    Element("Cl", "Chlorine", 17, 3, "17", "Halogen", 35.45, "[Ne]3s2 3p5"),
    Element("Ar", "Argon", 18, 3, "18", "Noble gas", 39.948, "[Ne]3s2 3p6"),
    Element("K", "Potassium", 19, 4, "1", "Alkali metal", 39.098, "[Ar]4s1"),
    Element("Ca", "Calcium", 20, 4, "2", "Alkaline earth metal", 40.078, "[Ar]4s2"),
    # 21‑30
    Element("Sc", "Scandium", 21, 4, "3", "Transition metal", 44.956, "[Ar]3d1 4s2"),
    Element("Ti", "Titanium", 22, 4, "4", "Transition metal", 47.867, "[Ar]3d2 4s2"),
    Element("V", "Vanadium", 23, 4, "5", "Transition metal", 50.942, "[Ar]3d3 4s2"),
    Element("Cr", "Chromium", 24, 4, "6", "Transition metal", 51.996, "[Ar]3d5 4s1"),
    Element("Mn", "Manganese", 25, 4, "7", "Transition metal", 54.938, "[Ar]3d5 4s2"),
    Element("Fe", "Iron", 26, 4, "8", "Transition metal", 55.845, "[Ar]3d6 4s2"),
    Element("Co", "Cobalt", 27, 4, "9", "Transition metal", 58.933, "[Ar]3d7 4s2"),
    Element("Ni", "Nickel", 28, 4, "10", "Transition metal", 58.693, "[Ar]3d8 4s2"),
    Element("Cu", "Copper", 29, 4, "11", "Transition metal", 63.546, "[Ar]3d10 4s1"),
    Element("Zn", "Zinc", 30, 4, "12", "Transition metal", 65.38, "[Ar]3d10 4s2"),
    # 31‑40
    Element("Ga", "Gallium", 31, 4, "13", "Post‑transition metal", 69.723, "[Ar]3d10 4s2 4p1"),
    Element("Ge", "Germanium", 32, 4, "14", "Metalloid", 72.630, "[Ar]3d10 4s2 4p2"),
    Element("As", "Arsenic", 33, 4, "15", "Metalloid", 74.922, "[Ar]3d10 4s2 4p3"),
    Element("Se", "Selenium", 34, 4, "16", "Nonmetal", 78.971, "[Ar]3d10 4s2 4p4"),
    Element("Br", "Bromine", 35, 4, "17", "Halogen", 79.904, "[Ar]3d10 4s2 4p5"),
    Element("Kr", "Krypton", 36, 4, "18", "Noble gas", 83.798, "[Ar]3d10 4s2 4p6"),
    Element("Rb", "Rubidium", 37, 5, "1", "Alkali metal", 85.468, "[Kr]5s1"),
    Element("Sr", "Strontium", 38, 5, "2", "Alkaline earth metal", 87.62, "[Kr]5s2"),
    Element("Y", "Yttrium", 39, 5, "3", "Transition metal", 88.906, "[Kr]4d1 5s2"),
    Element("Zr", "Zirconium", 40, 5, "4", "Transition metal", 91.224, "[Kr]4d2 5s2"),
    # 41‑50
    Element("Nb", "Niobium", 41, 5, "5", "Transition metal", 92.906, "[Kr]4d4 5s1"),
    Element("Mo", "Molybdenum", 42, 5, "6", "Transition metal", 95.95, "[Kr]4d5 5s1"),
    Element("Tc", "Technetium", 43, 5, "7", "Transition metal", 98.0, "[Kr]4d5 5s2"),
    Element("Ru", "Ruthenium", 44, 5, "8", "Transition metal", 101.07, "[Kr]4d7 5s1"),
    Element("Rh", "Rhodium", 45, 5, "9", "Transition metal", 102.91, "[Kr]4d8 5s1"),
    Element("Pd", "Palladium", 46, 5, "10", "Transition metal", 106.42, "[Kr]4d10"),
    Element("Ag", "Silver", 47, 5, "11", "Transition metal", 107.87, "[Kr]4d10 5s1"),
    Element("Cd", "Cadmium", 48, 5, "12", "Transition metal", 112.41, "[Kr]4d10 5s2"),
    Element("In", "Indium", 49, 5, "13", "Post‑transition metal", 114.82, "[Kr]4d10 5s2 5p1"),
    Element("Sn", "Tin", 50, 5, "14", "Post‑transition metal", 118.71, "[Kr]4d10 5s2 5p2"),
    # 51‑60
    Element("Sb", "Antimony", 51, 5, "15", "Metalloid", 121.76, "[Kr]4d10 5s2 5p3"),
    Element("Te", "Tellurium", 52, 5, "16", "Metalloid", 127.60, "[Kr]4d10 5s2 5p4"),
    Element("I", "Iodine", 53, 5, "17", "Halogen", 126.90, "[Kr]4d10 5s2 5p5"),
    Element("Xe", "Xenon", 54, 5, "18", "Noble gas", 131.29, "[Kr]4d10 5s2 5p6"),
    Element("Cs", "Caesium", 55, 6, "1", "Alkali metal", 132.91, "[Xe]6s1"),
    Element("Ba", "Barium", 56, 6, "2", "Alkaline earth metal", 137.33, "[Xe]6s2"),
    Element("La", "Lanthanum", 57, 6, "3", "Lanthanide", 138.91, "[Xe]5d1 6s2"),
    Element("Ce", "Cerium", 58, 6, "3", "Lanthanide", 140.12, "[Xe]4f1 5d1 6s2"),
    Element("Pr", "Praseodymium", 59, 6, "3", "Lanthanide", 140.91, "[Xe]4f3 6s2"),
    Element("Nd", "Neodymium", 60, 6, "3", "Lanthanide", 144.24, "[Xe]4f4 6s2"),
    # 61‑70
    Element("Pm", "Promethium", 61, 6, "3", "Lanthanide", 145.0, "[Xe]4f5 6s2"),
    Element("Sm", "Samarium", 62, 6, "3", "Lanthanide", 150.36, "[Xe]4f6 6s2"),
    Element("Eu", "Europium", 63, 6, "3", "Lanthanide", 151.96, "[Xe]4f7 6s2"),
    Element("Gd", "Gadolinium", 64, 6, "3", "Lanthanide", 157.25, "[Xe]4f7 5d1 6s2"),
    Element("Tb", "Terbium", 65, 6, "3", "Lanthanide", 158.93, "[Xe]4f9 6s2"),
    Element("Dy", "Dysprosium", 66, 6, "3", "Lanthanide", 162.50, "[Xe]4f10 6s2"),
    Element("Ho", "Holmium", 67, 6, "3", "Lanthanide", 164.93, "[Xe]4f11 6s2"),
    Element("Er", "Erbium", 68, 6, "3", "Lanthanide", 167.26, "[Xe]4f12 6s2"),
    Element("Tm", "Thulium", 69, 6, "3", "Lanthanide", 168.93, "[Xe]4f13 6s2"),
    Element("Yb", "Ytterbium", 70, 6, "3", "Lanthanide", 173.05, "[Xe]4f14 6s2"),
    # 71‑80
    Element("Lu", "Lutetium", 71, 6, "3", "Lanthanide", 174.97, "[Xe]4f14 5d1 6s2"),
    Element("Hf", "Hafnium", 72, 6, "4", "Transition metal", 178.49, "[Xe]4f14 5d2 6s2"),
    Element("Ta", "Tantalum", 73, 6, "5", "Transition metal", 180.95, "[Xe]4f14 5d3 6s2"),
    Element("W", "Tungsten", 74, 6, "6", "Transition metal", 183.84, "[Xe]4f14 5d4 6s2"),
    Element("Re", "Rhenium", 75, 6, "7", "Transition metal", 186.21, "[Xe]4f14 5d5 6s2"),
    Element("Os", "Osmium", 76, 6, "8", "Transition metal", 190.23, "[Xe]4f14 5d6 6s2"),
    Element("Ir", "Iridium", 77, 6, "9", "Transition metal", 192.22, "[Xe]4f14 5d7 6s2"),
    Element("Pt", "Platinum", 78, 6, "10", "Transition metal", 195.08, "[Xe]4f14 5d9 6s1"),
    Element("Au", "Gold", 79, 6, "11", "Transition metal", 196.97, "[Xe]4f14 5d10 6s1"),
    Element("Hg", "Mercury", 80, 6, "12", "Post‑transition metal", 200.59, "[Xe]4f14 5d10 6s2"),
    # 81‑90
    Element("Tl", "Thallium", 81, 6, "13", "Post‑transition metal", 204.38, "[Xe]4f14 5d10 6s2 6p1"),
    Element("Pb", "Lead", 82, 6, "14", "Post‑transition metal", 207.2, "[Xe]4f14 5d10 6s2 6p2"),
    Element("Bi", "Bismuth", 83, 6, "15", "Post‑transition metal", 208.98, "[Xe]4f14 5d10 6s2 6p3"),
    Element("Po", "Polonium", 84, 6, "16", "Post‑transition metal", 209.0, "[Xe]4f14 5d10 6s2 6p4"),
    Element("At", "Astatine", 85, 6, "17", "Halogen", 210.0, "[Xe]4f14 5d10 6s2 6p5"),
    Element("Rn", "Radon", 86, 6, "18", "Noble gas", 222.0, "[Xe]4f14 5d10 6s2 6p6"),
    Element("Fr", "Francium", 87, 7, "1", "Alkali metal", 223.0, "[Rn]7s1"),
    Element("Ra", "Radium", 88, 7, "2", "Alkaline earth metal", 226.0, "[Rn]7s2"),
    Element("Ac", "Actinium", 89, 7, "3", "Actinide", 227.0, "[Rn]6d1 7s2"),
    Element("Th", "Thorium", 90, 7, "3", "Actinide", 232.04, "[Rn]6d2 7s2"),
    # 91‑100
    Element("Pa", "Protactinium", 91, 7, "3", "Actinide", 231.04, "[Rn]5f2 6d1 7s2"),
    Element("U", "Uranium", 92, 7, "3", "Actinide", 238.03, "[Rn]5f3 6d1 7s2"),
    Element("Np", "Neptunium", 93, 7, "3", "Actinide", 237.0, "[Rn]5f4 6d1 7s2"),
    Element("Pu", "Plutonium", 94, 7, "3", "Actinide", 244.0, "[Rn]5f6 7s2"),
    Element("Am", "Americium", 95, 7, "3", "Actinide", 243.0, "[Rn]5f7 7s2"),
    Element("Cm", "Curium", 96, 7, "3", "Actinide", 247.0, "[Rn]5f7 6d1 7s2"),
    Element("Bk", "Berkelium", 97, 7, "3", "Actinide", 247.0, "[Rn]5f9 7s2"),
    Element("Cf", "Californium", 98, 7, "3", "Actinide", 251.0, "[Rn]5f10 7s2"),
    Element("Es", "Einsteinium", 99, 7, "3", "Actinide", 252.0, "[Rn]5f11 7s2"),
    Element("Fm", "Fermium", 100, 7, "3", "Actinide", 257.0, "[Rn]5f12 7s2"),
    # 101‑118
    Element("Md", "Mendelevium", 101, 7, "3", "Actinide", 258.0, "[Rn]5f13 7s2"),
    Element("No", "Nobelium", 102, 7, "3", "Actinide", 259.0, "[Rn]5f14 7s2"),
    Element("Lr", "Lawrencium", 103, 7, "3", "Actinide", 266.0, "[Rn]5f14 6d1 7s2"),
    Element("Rf", "Rutherfordium", 104, 7, "4", "Transition metal", 267.0, "[Rn]5f14 6d2 7s2"),
    Element("Db", "Dubnium", 105, 7, "5", "Transition metal", 268.0, "[Rn]5f14 6d3 7s2"),
    Element("Sg", "Seaborgium", 106, 7, "6", "Transition metal", 269.0, "[Rn]5f14 6d4 7s2"),
    Element("Bh", "Bohrium", 107, 7, "7", "Transition metal", 270.0, "[Rn]5f14 6d5 7s2"),
    Element("Hs", "Hassium", 108, 7, "8", "Transition metal", 277.0, "[Rn]5f14 6d6 7s2"),
    Element("Mt", "Meitnerium", 109, 7, "9", "Transition metal", 278.0, "[Rn]5f14 6d7 7s2"),
    Element("Ds", "Darmstadtium", 110, 7, "10", "Transition metal", 281.0, "[Rn]5f14 6d8 7s2"),
    Element("Rg", "Roentgenium", 111, 7, "11", "Transition metal", 282.0, "[Rn]5f14 6d9 7s2"),
    Element("Cn", "Copernicium", 112, 7, "12", "Transition metal", 285.0, "[Rn]5f14 6d10 7s2"),
    Element("Nh", "Nihonium", 113, 7, "13", "Post‑transition metal", 286.0, "[Rn]5f14 6d10 7s2 7p1"),
    Element("Fl", "Flerovium", 114, 7, "14", "Post‑transition metal", 289.0, "[Rn]5f14 6d10 7s2 7p2"),
    Element("Mc", "Moscovium", 115, 7, "15", "Post‑transition metal", 290.0, "[Rn]5f14 6d10 7s2 7p3"),
    Element("Lv", "Livermorium", 116, 7, "16", "Post‑transition metal", 293.0, "[Rn]5f14 6d10 7s2 7p4"),
    Element("Ts", "Tennessine", 117, 7, "17", "Halogen", 294.0, "[Rn]5f14 6d10 7s2 7p5"),
    Element("Og", "Oganesson", 118, 7, "18", "Noble gas", 294.0, "[Rn]5f14 6d10 7s2 7p6"),
]

ELEMENTS = {e.symbol: e for e in ELEMENTS_DATA}
SYMBOLS = list(ELEMENTS.keys())

# ─── User Data Manager ─────────────────────────────────────────────────────

class UserData:
    DATA_DIR = Path.home() / ".elements_study"
    DATA_FILE = DATA_DIR / "user_data.json"

    def __init__(self):
        self.favorites: List[str] = []
        self.stats: Dict[str, Dict] = {}  # symbol -> {correct, wrong, last_seen}
        self.rep_queue: List[str] = []
        self._load()

    def _load(self):
        if self.DATA_FILE.exists():
            try:
                with open(self.DATA_FILE, 'r') as f:
                    data = json.load(f)
                    self.favorites = data.get("favorites", [])
                    self.stats = data.get("stats", {})
                    self.rep_queue = data.get("rep_queue", [])
            except Exception:
                pass

    def save(self):
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(self.DATA_FILE, 'w') as f:
            json.dump({
                "favorites": self.favorites,
                "stats": self.stats,
                "rep_queue": self.rep_queue
            }, f, indent=2)

    def toggle_favorite(self, symbol: str):
        if symbol in self.favorites:
            self.favorites.remove(symbol)
        else:
            self.favorites.append(symbol)
        self.save()

    def is_favorite(self, symbol: str) -> bool:
        return symbol in self.favorites

    def record_answer(self, symbol: str, correct: bool):
        if symbol not in self.stats:
            self.stats[symbol] = {"correct": 0, "wrong": 0, "last_seen": datetime.now().isoformat()}
        if correct:
            self.stats[symbol]["correct"] += 1
        else:
            self.stats[symbol]["wrong"] += 1
        self.stats[symbol]["last_seen"] = datetime.now().isoformat()
        # Update rep queue: if wrong, push to front; if correct, push to back
        if symbol in self.rep_queue:
            self.rep_queue.remove(symbol)
        if not correct:
            self.rep_queue.insert(0, symbol)
        else:
            self.rep_queue.append(symbol)
        if len(self.rep_queue) > 30:
            self.rep_queue = self.rep_queue[:30]
        self.save()

    def get_next_rep(self) -> Optional[str]:
        """Return next element for repetition (SM‑2 like)"""
        if not self.rep_queue:
            # pick a random element not yet mastered
            unmastered = [s for s in SYMBOLS if s not in self.stats or self.stats[s].get("correct", 0) < 3]
            if unmastered:
                return random.choice(unmastered)
            return random.choice(SYMBOLS)
        return self.rep_queue[0]

    def get_progress(self) -> Tuple[int, int]:
        mastered = sum(1 for s in SYMBOLS if s in self.stats and self.stats[s].get("correct", 0) >= 3)
        return mastered, len(SYMBOLS)


# ─── Quiz Engine ───────────────────────────────────────────────────────────

class QuizEngine:
    def __init__(self, user_data: UserData):
        self.user = user_data
        self.console = Console() if RICH_AVAILABLE else None
        self.questions_asked = 0
        self.correct_answers = 0

    def run_quiz(self, num_questions: int = 10):
        self.questions_asked = 0
        self.correct_answers = 0
        if self.console:
            self.console.print(Panel.fit("[bold cyan]🧠 Quiz Time![/bold cyan]\nAnswer questions about elements.", border_style="cyan"))
        else:
            print("\n🧠 Quiz Time! Answer questions about elements.\n")

        for i in range(num_questions):
            # Pick a question type: 0 = symbol->name, 1 = name->symbol
            q_type = random.choice([0, 1])
            if q_type == 0:
                element = random.choice(ELEMENTS_DATA)
                correct = element.name
                prompt = f"What is the name of element with symbol {element.symbol}?"
                options = self._get_options(element, 'name')
            else:
                element = random.choice(ELEMENTS_DATA)
                correct = element.symbol
                prompt = f"What is the symbol of {element.name}?"
                options = self._get_options(element, 'symbol')

            if self.console:
                self.console.print(f"\n[bold yellow]Q{i+1}.[/bold yellow] {prompt}")
                for idx, opt in enumerate(options, 1):
                    self.console.print(f"  [{idx}] {opt}")
                choice = Prompt.ask("Your choice", choices=["1","2","3","4"], default="1")
            else:
                print(f"\nQ{i+1}. {prompt}")
                for idx, opt in enumerate(options, 1):
                    print(f"  {idx}. {opt}")
                choice = input("Your choice (1-4): ").strip()
                while choice not in ["1","2","3","4"]:
                    choice = input("Please enter 1-4: ").strip()

            selected = options[int(choice)-1]
            is_correct = (selected == correct)
            self.user.record_answer(element.symbol, is_correct)
            if is_correct:
                self.correct_answers += 1
                msg = f"✅ Correct! {correct}"
                color = "green"
            else:
                msg = f"❌ Wrong! The answer was {correct}"
                color = "red"
            self.questions_asked += 1
            if self.console:
                self.console.print(f"[{color}]{msg}[/{color}]")
            else:
                print(msg)

        if self.console:
            self.console.print(f"\n[bold]Quiz finished![/bold] Correct: [green]{self.correct_answers}[/green], Wrong: [red]{num_questions - self.correct_answers}[/red]")
        else:
            print(f"\nQuiz finished! Correct: {self.correct_answers}, Wrong: {num_questions - self.correct_answers}")

    def _get_options(self, element: Element, field: str) -> List[str]:
        """Generate 4 options (one correct, three random) for a given field."""
        correct = getattr(element, field)
        others = [getattr(e, field) for e in random.sample(ELEMENTS_DATA, 20) if getattr(e, field) != correct]
        options = [correct] + random.sample(others, 3)
        random.shuffle(options)
        return options


# ─── Main App ──────────────────────────────────────────────────────────────

class ElementApp:
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.user = UserData()
        self.quiz = QuizEngine(self.user)

    def show_menu(self):
        mastered, total = self.user.get_progress()
        if self.console:
            panel = Panel(
                f"[bold cyan]⚛️ Element Master[/bold cyan]\n"
                f"  Favorites: {len(self.user.favorites)}\n"
                f"  Mastered: {mastered}/{total}\n"
                f"  Next repetition: {self.user.get_next_rep() or '—'}",
                title="📋 Main Menu",
                border_style="blue"
            )
            self.console.print(panel)
            self.console.print(" [1] 📋 List All Elements")
            self.console.print(" [2] 🔍 Search Element")
            self.console.print(" [3] ⭐ Favorites")
            self.console.print(" [4] 🧠 Start Quiz")
            self.console.print(" [5] 📊 Statistics")
            self.console.print(" [6] 🔁 Spaced Repetition")
            self.console.print(" [7] ➕ Toggle Favorite")
            self.console.print(" [0] 🚪 Exit")
        else:
            print("\n" + "="*50)
            print(c("⚛️ ELEMENT MASTER", "bright"))
            print("="*50)
            print(f"  Favorites: {len(self.user.favorites)}")
            print(f"  Mastered: {mastered}/{total}")
            print(f"  Next repetition: {self.user.get_next_rep() or '—'}")
            print("="*50)
            print("  1. 📋 List All Elements")
            print("  2. 🔍 Search Element")
            print("  3. ⭐ Favorites")
            print("  4. 🧠 Start Quiz")
            print("  5. 📊 Statistics")
            print("  6. 🔁 Spaced Repetition")
            print("  7. ➕ Toggle Favorite")
            print("  0. 🚪 Exit")
            print("="*50)

    def list_elements(self):
        if self.console:
            table = Table(title="📋 All Elements", box=box.ROUNDED)
            table.add_column("Symbol", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Number")
            table.add_column("Category", style="yellow")
            table.add_column("Mass", justify="right")
            for e in ELEMENTS_DATA:
                star = "⭐" if self.user.is_favorite(e.symbol) else ""
                table.add_row(e.symbol + star, e.name, str(e.number), e.category, f"{e.mass:.3f}")
            self.console.print(table)
        else:
            print("\n📋 ALL ELEMENTS")
            print("-"*60)
            for e in ELEMENTS_DATA:
                fav = "⭐" if self.user.is_favorite(e.symbol) else ""
                print(f"  {e.symbol:3} {fav} {e.name:12} #{e.number:3} {e.category:15} {e.mass:.3f}")

    def search_element(self):
        if self.console:
            query = Prompt.ask("🔍 Enter symbol, name, or number")
        else:
            query = input("🔍 Enter symbol, name, or number: ").strip()
        results = []
        for e in ELEMENTS_DATA:
            if (query.lower() in e.symbol.lower() or query.lower() in e.name.lower() or
                query == str(e.number) or query == str(e.period) or query.lower() in e.category.lower()):
                results.append(e)
        if not results:
            print(c("No elements found.", "yellow"))
            return
        if self.console:
            table = Table(title=f"🔍 Results ({len(results)})", box=box.ROUNDED)
            table.add_column("Symbol", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Number")
            table.add_column("Category")
            table.add_column("Mass")
            for e in results:
                star = "⭐" if self.user.is_favorite(e.symbol) else ""
                table.add_row(e.symbol + star, e.name, str(e.number), e.category, f"{e.mass:.3f}")
            self.console.print(table)
        else:
            print(f"\n🔍 Results ({len(results)})")
            for e in results:
                fav = "⭐" if self.user.is_favorite(e.symbol) else ""
                print(f"  {e.symbol:3} {fav} {e.name:12} #{e.number:3} {e.category:15} {e.mass:.3f}")

    def show_favorites(self):
        if not self.user.favorites:
            print(c("No favorites yet.", "yellow"))
            return
        fav_elements = [ELEMENTS[s] for s in self.user.favorites if s in ELEMENTS]
        if self.console:
            table = Table(title="⭐ Favorites", box=box.ROUNDED)
            table.add_column("Symbol", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Number")
            table.add_column("Category")
            for e in fav_elements:
                table.add_row(e.symbol, e.name, str(e.number), e.category)
            self.console.print(table)
        else:
            print("\n⭐ FAVORITES")
            for e in fav_elements:
                print(f"  {e.symbol:3} {e.name:12} #{e.number:3} {e.category}")

    def start_quiz(self):
        if self.console:
            num = IntPrompt.ask("Number of questions", default=10)
        else:
            try:
                num = int(input("Number of questions (default 10): ") or "10")
            except ValueError:
                num = 10
        self.quiz.run_quiz(num)

    def show_stats(self):
        mastered, total = self.user.get_progress()
        total_answers = sum(s.get("correct", 0) + s.get("wrong", 0) for s in self.user.stats.values())
        correct_answers = sum(s.get("correct", 0) for s in self.user.stats.values())
        if self.console:
            table = Table(title="📊 Your Statistics", box=box.ROUNDED)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            table.add_row("Total Elements", str(total))
            table.add_row("Mastered (≥3 correct)", str(mastered))
            table.add_row("Favorites", str(len(self.user.favorites)))
            table.add_row("Total Answers", str(total_answers))
            table.add_row("Correct Answers", str(correct_answers))
            if total_answers > 0:
                table.add_row("Accuracy", f"{correct_answers/total_answers*100:.1f}%")
            else:
                table.add_row("Accuracy", "—")
            self.console.print(table)
        else:
            print("\n📊 STATISTICS")
            print("-"*30)
            print(f"  Total Elements: {total}")
            print(f"  Mastered: {mastered}")
            print(f"  Favorites: {len(self.user.favorites)}")
            print(f"  Total Answers: {total_answers}")
            print(f"  Correct Answers: {correct_answers}")
            if total_answers > 0:
                print(f"  Accuracy: {correct_answers/total_answers*100:.1f}%")

    def spaced_repetition(self):
        symbol = self.user.get_next_rep()
        if not symbol:
            print(c("No elements to repeat. Keep learning!", "green"))
            return
        element = ELEMENTS[symbol]
        if self.console:
            self.console.print(Panel(f"[bold]🔁 Repetition: {element.name} ({element.symbol})[/bold]\n"
                                     f"Number: {element.number}  Category: {element.category}  Mass: {element.mass}",
                                     title="Spaced Repetition", border_style="magenta"))
            # Ask a quick question
            if random.choice([0,1]):
                ans = Prompt.ask(f"What is the name of {element.symbol}?", default="")
                correct = element.name
            else:
                ans = Prompt.ask(f"What is the symbol of {element.name}?", default="")
                correct = element.symbol
            is_correct = ans.strip().lower() == correct.lower()
            self.user.record_answer(symbol, is_correct)
            if is_correct:
                self.console.print("[green]✅ Correct![/green]")
            else:
                self.console.print(f"[red]❌ Wrong. The answer was {correct}[/red]")
        else:
            print(f"\n🔁 Repetition: {element.name} ({element.symbol})")
            print(f"  Number: {element.number}  Category: {element.category}  Mass: {element.mass}")
            if random.choice([0,1]):
                ans = input(f"What is the name of {element.symbol}? ")
                correct = element.name
            else:
                ans = input(f"What is the symbol of {element.name}? ")
                correct = element.symbol
            is_correct = ans.strip().lower() == correct.lower()
            self.user.record_answer(symbol, is_correct)
            if is_correct:
                print(c("✅ Correct!", "green"))
            else:
                print(c(f"❌ Wrong. The answer was {correct}", "red"))

    def toggle_favorite(self):
        if self.console:
            sym = Prompt.ask("Enter element symbol to toggle favorite").strip().upper()
        else:
            sym = input("Enter element symbol to toggle favorite: ").strip().upper()
        if sym not in ELEMENTS:
            print(c("Element not found.", "red"))
            return
        self.user.toggle_favorite(sym)
        state = "added to" if self.user.is_favorite(sym) else "removed from"
        print(c(f"✅ {sym} {state} favorites.", "green"))

    def run(self):
        if self.console:
            self.console.print(Panel.fit("[bold cyan]⚛️ Element Master – Learn Chemistry Elements[/bold cyan]", border_style="cyan"))
        else:
            print(c("\n⚛️ Element Master – Learn Chemistry Elements", "bright"))
            print(c("Master the periodic table, one element at a time!", "dim"))

        while True:
            self.show_menu()
            if self.console:
                choice = Prompt.ask("Your choice", choices=["0","1","2","3","4","5","6","7"])
            else:
                choice = input("Your choice: ").strip()

            if choice == "1":
                self.list_elements()
            elif choice == "2":
                self.search_element()
            elif choice == "3":
                self.show_favorites()
            elif choice == "4":
                self.start_quiz()
            elif choice == "5":
                self.show_stats()
            elif choice == "6":
                self.spaced_repetition()
            elif choice == "7":
                self.toggle_favorite()
            elif choice == "0":
                print(c("👋 Goodbye! Keep learning!", "cyan"))
                break
            else:
                print(c("❌ Invalid choice.", "red"))

            if choice != "0":
                if self.console:
                    self.console.print("\n[dim]Press Enter to continue...[/dim]")
                    input()
                else:
                    input("\nPress Enter to continue...")


def main():
    try:
        app = ElementApp()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(c(f"❌ Unexpected error: {e}", "red"))
        sys.exit(1)

if __name__ == "__main__":
    main()
