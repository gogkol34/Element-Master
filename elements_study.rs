# elements_study.rs
/**
 * ⚛️ Element Master – Learn Chemistry Elements (Rust Edition)
 * Advanced: complete DB, favorites, quiz, spaced repetition, stats
 */

use rand::seq::SliceRandom;
use rand::thread_rng;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::io::{self, Write, BufRead};
use std::path::PathBuf;
use chrono::Utc;

// ─── Types ──────────────────────────────────────────────────────────────────

#[derive(Debug, Serialize, Deserialize, Clone)]
struct Element {
    symbol: String,
    name: String,
    number: u32,
    period: u32,
    group: String,
    category: String,
    mass: f64,
    electron_config: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct UserStats {
    correct: u32,
    wrong: u32,
    last_seen: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct UserData {
    favorites: Vec<String>,
    stats: HashMap<String, UserStats>,
    rep_queue: Vec<String>,
}

// ─── Global Data ──────────────────────────────────────────────────────────

lazy_static! {
    static ref ELEMENTS: HashMap<String, Element> = {
        let data = vec![
            Element { symbol: "H".to_string(), name: "Hydrogen".to_string(), number: 1, period: 1, group: "1".to_string(), category: "Nonmetal".to_string(), mass: 1.008, electron_config: "1s1".to_string() },
            // ... full list
        ];
        let mut map = HashMap::new();
        for e in data {
            map.insert(e.symbol.clone(), e);
        }
        map
    };
    static ref ELEMENTS_LIST: Vec<Element> = ELEMENTS.values().cloned().collect();
}

// ─── Colors ──────────────────────────────────────────────────────────────────

fn c(text: &str, color: &str) -> String {
    format!("{}{}{}", color, text, "\x1b[0m")
}

const RESET: &str = "\x1b[0m";
const BRIGHT: &str = "\x1b[1m";
const DIM: &str = "\x1b[2m";
const RED: &str = "\x1b[31m";
const GREEN: &str = "\x1b[32m";
const YELLOW: &str = "\x1b[33m";
const BLUE: &str = "\x1b[34m";
const MAGENTA: &str = "\x1b[35m";
const CYAN: &str = "\x1b[36m";

// ─── User Data Manager ─────────────────────────────────────────────────────

struct UserDataManager {
    file_path: PathBuf,
    data: UserData,
}

impl UserDataManager {
    fn new() -> Self {
        let home = std::env::var("HOME").or_else(|_| std::env::var("USERPROFILE")).unwrap_or_else(|_| ".".to_string());
        let dir = PathBuf::from(home).join(".elements_study");
        fs::create_dir_all(&dir).unwrap();
        let file_path = dir.join("user_data.json");
        let mut ud = UserDataManager { file_path, data: UserData { favorites: Vec::new(), stats: HashMap::new(), rep_queue: Vec::new() } };
        ud.load();
        ud
    }

    fn load(&mut self) {
        if let Ok(raw) = fs::read_to_string(&self.file_path) {
            if let Ok(data) = serde_json::from_str::<UserData>(&raw) {
                self.data = data;
                return;
            }
        }
        self.data = UserData { favorites: Vec::new(), stats: HashMap::new(), rep_queue: Vec::new() };
    }

    fn save(&self) {
        let raw = serde_json::to_string_pretty(&self.data).unwrap();
        let _ = fs::write(&self.file_path, raw);
    }

    fn toggle_favorite(&mut self, symbol: &str) {
        if let Some(pos) = self.data.favorites.iter().position(|s| s == symbol) {
            self.data.favorites.remove(pos);
        } else {
            self.data.favorites.push(symbol.to_string());
        }
        self.save();
    }

    fn is_favorite(&self, symbol: &str) -> bool {
        self.data.favorites.contains(&symbol.to_string())
    }

    fn record_answer(&mut self, symbol: &str, correct: bool) {
        let stats = self.data.stats.entry(symbol.to_string()).or_insert(UserStats { correct: 0, wrong: 0, last_seen: Utc::now().to_rfc3339() });
        if correct { stats.correct += 1; } else { stats.wrong += 1; }
        stats.last_seen = Utc::now().to_rfc3339();

        // update rep queue
        if let Some(pos) = self.data.rep_queue.iter().position(|s| s == symbol) {
            self.data.rep_queue.remove(pos);
        }
        if !correct {
            self.data.rep_queue.insert(0, symbol.to_string());
        } else {
            self.data.rep_queue.push(symbol.to_string());
        }
        if self.data.rep_queue.len() > 30 {
            self.data.rep_queue.truncate(30);
        }
        self.save();
    }

    fn get_next_rep(&self) -> Option<String> {
        if !self.data.rep_queue.is_empty() {
            return Some(self.data.rep_queue[0].clone());
        }
        let mut unmastered = Vec::new();
        for (sym, stats) in &self.data.stats {
            if stats.correct < 3 {
                unmastered.push(sym.clone());
            }
        }
        if !unmastered.is_empty() {
            return Some(unmastered.choose(&mut thread_rng()).unwrap().clone());
        }
        let syms: Vec<String> = ELEMENTS.keys().cloned().collect();
        syms.choose(&mut thread_rng()).cloned()
    }

    fn get_progress(&self) -> (usize, usize) {
        let total = ELEMENTS.len();
        let mastered = self.data.stats.iter().filter(|(_, stats)| stats.correct >= 3).count();
        (mastered, total)
    }
}

// ─── Quiz Engine ──────────────────────────────────────────────────────────

struct QuizEngine {
    user: UserDataManager,
    rng: rand::rngs::ThreadRng,
}

impl QuizEngine {
    fn new(user: UserDataManager) -> Self {
        QuizEngine { user, rng: thread_rng() }
    }

    fn get_options(&self, element: &Element, field: &str) -> Vec<String> {
        let correct = if field == "name" { element.name.clone() } else { element.symbol.clone() };
        let pool: Vec<&Element> = ELEMENTS_LIST.iter().filter(|e| {
            let val = if field == "name" { &e.name } else { &e.symbol };
            val != &correct
        }).collect();
        let mut others = Vec::new();
        while others.len() < 3 {
            let r = pool.choose(&mut self.rng).unwrap();
            let val = if field == "name" { &r.name } else { &r.symbol };
            if !others.contains(val) && val != &correct {
                others.push(val.clone());
            }
        }
        let mut options = vec![correct.clone()];
        options.extend(others);
        options.shuffle(&mut self.rng);
        options
    }

    fn run_quiz(&mut self, num_questions: u32) {
        let mut correct_count = 0;
        println!("{}", c("\n🧠 Quiz Time! Answer questions about elements.", &format!("{}{}", BRIGHT, CYAN)));
        for i in 0..num_questions {
            let q_type = if rand::random() { 0 } else { 1 };
            let element = ELEMENTS_LIST.choose(&mut self.rng).unwrap();
            let (prompt, correct, options) = if q_type == 0 {
                let correct = element.name.clone();
                let prompt = format!("What is the name of element with symbol {}?", element.symbol);
                let options = self.get_options(element, "name");
                (prompt, correct, options)
            } else {
                let correct = element.symbol.clone();
                let prompt = format!("What is the symbol of {}?", element.name);
                let options = self.get_options(element, "symbol");
                (prompt, correct, options)
            };
            println!("\n{} {}", c(&format!("Q{}", i+1), YELLOW), prompt);
            for (idx, opt) in options.iter().enumerate() {
                println!("  {}. {}", idx+1, opt);
            }
            print!("Your choice (1-4): ");
            io::stdout().flush().unwrap();
            let mut choice = String::new();
            io::stdin().read_line(&mut choice).unwrap();
            let idx: usize = choice.trim().parse().unwrap_or(1);
            let selected = &options[idx-1];
            let is_correct = selected == &correct;
            self.user.record_answer(&element.symbol, is_correct);
            if is_correct {
                correct_count += 1;
                println!("{}", c(&format!("✅ Correct! {}", correct), GREEN));
            } else {
                println!("{}", c(&format!("❌ Wrong! The answer was {}", correct), RED));
            }
        }
        println!("\n{} Correct: {}, Wrong: {}", c("Quiz finished!", BRIGHT), c(&correct_count.to_string(), GREEN), c(&(num_questions - correct_count).to_string(), RED));
    }
}

// ─── Main App ─────────────────────────────────────────────────────────────

struct ElementApp {
    user: UserDataManager,
    quiz: QuizEngine,
}

impl ElementApp {
    fn new() -> Self {
        let user = UserDataManager::new();
        let quiz = QuizEngine::new(user);
        ElementApp { user, quiz }
    }

    fn ask(&self, prompt: &str) -> String {
        print!("{}", prompt);
        io::stdout().flush().unwrap();
        let mut line = String::new();
        io::stdin().read_line(&mut line).unwrap();
        line.trim().to_string()
    }

    fn ask_int(&self, prompt: &str) -> u32 {
        loop {
            let ans = self.ask(prompt);
            if let Ok(num) = ans.parse::<u32>() {
                return num;
            }
            println!("{}", c("Please enter a number.", YELLOW));
        }
    }

    fn show_menu(&self) {
        let (mastered, total) = self.user.get_progress();
        let next = self.user.get_next_rep().unwrap_or_else(|| "—".to_string());
        println!("\n{}", c(&"=".repeat(50), CYAN));
        println!("{}", c("⚛️ ELEMENT MASTER", &format!("{}{}", BRIGHT, CYAN)));
        println!("{}", c(&"=".repeat(50), CYAN));
        println!("  Favorites: {}", self.user.data.favorites.len());
        println!("  Mastered: {}/{}", mastered, total);
        println!("  Next repetition: {}", next);
        println!("{}", c(&"=".repeat(50), CYAN));
        println!("  1. 📋 List All Elements");
        println!("  2. 🔍 Search Element");
        println!("  3. ⭐ Favorites");
        println!("  4. 🧠 Start Quiz");
        println!("  5. 📊 Statistics");
        println!("  6. 🔁 Spaced Repetition");
        println!("  7. ➕ Toggle Favorite");
        println!("  0. 🚪 Exit");
        println!("{}", c(&"=".repeat(50), CYAN));
    }

    fn list_elements(&self) {
        println!("\n📋 ALL ELEMENTS");
        println!("{}", c(&"-".repeat(60), DIM));
        for e in ELEMENTS_LIST.iter() {
            let star = if self.user.is_favorite(&e.symbol) { "⭐" } else { "" };
            println!("  {:3} {} {:12} #{:3} {:15} {:.3}", e.symbol, star, e.name, e.number, e.category, e.mass);
        }
    }

    fn search_element(&self) {
        let query = self.ask("🔍 Enter symbol, name, or number: ");
        let results: Vec<&Element> = ELEMENTS_LIST.iter().filter(|e| {
            e.symbol.to_lowercase().contains(&query.to_lowercase()) ||
            e.name.to_lowercase().contains(&query.to_lowercase()) ||
            e.number.to_string() == query ||
            e.category.to_lowercase().contains(&query.to_lowercase())
        }).collect();
        if results.is_empty() {
            println!("{}", c("No elements found.", YELLOW));
            return;
        }
        println!("\n🔍 Results ({})", results.len());
        for e in results {
            let star = if self.user.is_favorite(&e.symbol) { "⭐" } else { "" };
            println!("  {:3} {} {:12} #{:3} {:15} {:.3}", e.symbol, star, e.name, e.number, e.category, e.mass);
        }
    }

    fn show_favorites(&self) {
        let favs: Vec<&Element> = self.user.data.favorites.iter().filter_map(|s| ELEMENTS.get(s)).collect();
        if favs.is_empty() {
            println!("{}", c("No favorites yet.", YELLOW));
            return;
        }
        println!("\n⭐ FAVORITES");
        for e in favs {
            println!("  {:3} {:12} #{:3} {}", e.symbol, e.name, e.number, e.category);
        }
    }

    fn start_quiz(&mut self) {
        let num = self.ask_int("Number of questions (default 10): ");
        let n = if num == 0 { 10 } else { num };
        self.quiz.run_quiz(n);
    }

    fn show_stats(&self) {
        let (mastered, total) = self.user.get_progress();
        let total_answers: u32 = self.user.data.stats.values().map(|s| s.correct + s.wrong).sum();
        let correct_answers: u32 = self.user.data.stats.values().map(|s| s.correct).sum();
        println!("\n📊 STATISTICS");
        println!("{}", c(&"-".repeat(30), DIM));
        println!("  Total Elements: {}", total);
        println!("  Mastered: {}", mastered);
        println!("  Favorites: {}", self.user.data.favorites.len());
        println!("  Total Answers: {}", total_answers);
        println!("  Correct Answers: {}", correct_answers);
        if total_answers > 0 {
            println!("  Accuracy: {:.1}%", correct_answers as f64 / total_answers as f64 * 100.0);
        }
    }

    fn spaced_repetition(&mut self) {
        if let Some(symbol) = self.user.get_next_rep() {
            if let Some(element) = ELEMENTS.get(&symbol) {
                println!("\n🔁 Repetition: {} ({})", element.name, element.symbol);
                println!("  Number: {}  Category: {}  Mass: {:.3}", element.number, element.category, element.mass);
                let q_type = if rand::random() { 0 } else { 1 };
                let (prompt, correct) = if q_type == 0 {
                    (format!("What is the name of {}? ", element.symbol), element.name.clone())
                } else {
                    (format!("What is the symbol of {}? ", element.name), element.symbol.clone())
                };
                let ans = self.ask(&prompt);
                let is_correct = ans.trim().to_lowercase() == correct.to_lowercase();
                self.user.record_answer(&symbol, is_correct);
                if is_correct {
                    println!("{}", c("✅ Correct!", GREEN));
                } else {
                    println!("{}", c(&format!("❌ Wrong. The answer was {}", correct), RED));
                }
                return;
            }
        }
        println!("{}", c("No elements to repeat. Keep learning!", GREEN));
    }

    fn toggle_favorite(&mut self) {
        let sym = self.ask("Enter element symbol to toggle favorite: ");
        let symbol = sym.trim().to_uppercase();
        if !ELEMENTS.contains_key(&symbol) {
            println!("{}", c("Element not found.", RED));
            return;
        }
        self.user.toggle_favorite(&symbol);
        let state = if self.user.is_favorite(&symbol) { "added to" } else { "removed from" };
        println!("{}", c(&format!("✅ {} {} favorites.", symbol, state), GREEN));
    }

    fn run(&mut self) {
        println!("{}", c("\n⚛️ Element Master – Learn Chemistry Elements", &format!("{}{}", BRIGHT, CYAN)));
        println!("{}", c("Master the periodic table, one element at a time!", DIM));

        loop {
            self.show_menu();
            let choice = self.ask("Your choice: ");
            match choice.as_str() {
                "1" => self.list_elements(),
                "2" => self.search_element(),
                "3" => self.show_favorites(),
                "4" => self.start_quiz(),
                "5" => self.show_stats(),
                "6" => self.spaced_repetition(),
                "7" => self.toggle_favorite(),
                "0" => {
                    println!("{}", c("👋 Goodbye! Keep learning!", CYAN));
                    break;
                }
                _ => println!("{}", c("❌ Invalid choice.", RED)),
            }
            if choice != "0" {
                print!("\nPress Enter to continue...");
                io::stdout().flush().unwrap();
                let mut _dummy = String::new();
                io::stdin().read_line(&mut _dummy).unwrap();
            }
        }
    }
}

// ─── Main ────────────────────────────────────────────────────────────────────

#[macro_use] extern crate lazy_static;

fn main() {
    let mut app = ElementApp::new();
    app.run();
}
