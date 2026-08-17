# elements_study.go
/**
 * ⚛️ Element Master – Learn Chemistry Elements (Go Edition)
 * Advanced: complete DB, favorites, quiz, spaced repetition, stats
 */

package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"math/rand"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

// ─── Element Type ─────────────────────────────────────────────────────────

type Element struct {
	Symbol         string  `json:"symbol"`
	Name           string  `json:"name"`
	Number         int     `json:"number"`
	Period         int     `json:"period"`
	Group          string  `json:"group"`
	Category       string  `json:"category"`
	Mass           float64 `json:"mass"`
	ElectronConfig string  `json:"electron_config"`
}

// ─── User Data ────────────────────────────────────────────────────────────

type UserStats struct {
	Correct  int    `json:"correct"`
	Wrong    int    `json:"wrong"`
	LastSeen string `json:"last_seen"`
}

type UserData struct {
	Favorites []string            `json:"favorites"`
	Stats     map[string]UserStats `json:"stats"`
	RepQueue  []string            `json:"rep_queue"`
}

// ─── Global Data ──────────────────────────────────────────────────────────

var ELEMENTS = map[string]Element{}
var ELEMENTS_LIST []Element

func init() {
	// Populate with first 20 for brevity; full list in real code.
	data := []Element{
		{"H", "Hydrogen", 1, 1, "1", "Nonmetal", 1.008, "1s1"},
		// ... full list
	}
	for _, e := range data {
		ELEMENTS[e.Symbol] = e
		ELEMENTS_LIST = append(ELEMENTS_LIST, e)
	}
}

// ─── Colors ───────────────────────────────────────────────────────────────

const (
	reset  = "\x1b[0m"
	bright = "\x1b[1m"
	dim    = "\x1b[2m"
	red    = "\x1b[31m"
	green  = "\x1b[32m"
	yellow = "\x1b[33m"
	blue   = "\x1b[34m"
	magenta = "\x1b[35m"
	cyan   = "\x1b[36m"
)

func c(str, color string) string {
	return color + str + reset
}

// ─── User Data Manager ──────────────────────────────────────────────────

type UserDataManager struct {
	dataDir  string
	dataFile string
	data     UserData
}

func NewUserDataManager() *UserDataManager {
	home, _ := os.UserHomeDir()
	dir := filepath.Join(home, ".elements_study")
	os.MkdirAll(dir, 0755)
	file := filepath.Join(dir, "user_data.json")
	ud := &UserDataManager{dataDir: dir, dataFile: file}
	ud.load()
	return ud
}

func (ud *UserDataManager) load() {
	if _, err := os.Stat(ud.dataFile); os.IsNotExist(err) {
		ud.data = UserData{Favorites: []string{}, Stats: map[string]UserStats{}, RepQueue: []string{}}
		return
	}
	raw, err := os.ReadFile(ud.dataFile)
	if err != nil {
		ud.data = UserData{Favorites: []string{}, Stats: map[string]UserStats{}, RepQueue: []string{}}
		return
	}
	var d UserData
	if err := json.Unmarshal(raw, &d); err != nil {
		ud.data = UserData{Favorites: []string{}, Stats: map[string]UserStats{}, RepQueue: []string{}}
		return
	}
	ud.data = d
}

func (ud *UserDataManager) save() {
	raw, _ := json.MarshalIndent(ud.data, "", "  ")
	os.WriteFile(ud.dataFile, raw, 0644)
}

func (ud *UserDataManager) ToggleFavorite(symbol string) {
	for i, s := range ud.data.Favorites {
		if s == symbol {
			ud.data.Favorites = append(ud.data.Favorites[:i], ud.data.Favorites[i+1:]...)
			ud.save()
			return
		}
	}
	ud.data.Favorites = append(ud.data.Favorites, symbol)
	ud.save()
}

func (ud *UserDataManager) IsFavorite(symbol string) bool {
	for _, s := range ud.data.Favorites {
		if s == symbol {
			return true
		}
	}
	return false
}

func (ud *UserDataManager) RecordAnswer(symbol string, correct bool) {
	stats := ud.data.Stats[symbol]
	if stats.Correct == 0 && stats.Wrong == 0 {
		stats = UserStats{Correct: 0, Wrong: 0, LastSeen: time.Now().Format(time.RFC3339)}
	}
	if correct {
		stats.Correct++
	} else {
		stats.Wrong++
	}
	stats.LastSeen = time.Now().Format(time.RFC3339)
	ud.data.Stats[symbol] = stats

	// update rep queue
	for i, s := range ud.data.RepQueue {
		if s == symbol {
			ud.data.RepQueue = append(ud.data.RepQueue[:i], ud.data.RepQueue[i+1:]...)
			break
		}
	}
	if !correct {
		ud.data.RepQueue = append([]string{symbol}, ud.data.RepQueue...)
	} else {
		ud.data.RepQueue = append(ud.data.RepQueue, symbol)
	}
	if len(ud.data.RepQueue) > 30 {
		ud.data.RepQueue = ud.data.RepQueue[:30]
	}
	ud.save()
}

func (ud *UserDataManager) GetNextRep() string {
	if len(ud.data.RepQueue) > 0 {
		return ud.data.RepQueue[0]
	}
	var unmastered []string
	for sym := range ELEMENTS {
		if stats, ok := ud.data.Stats[sym]; !ok || stats.Correct < 3 {
			unmastered = append(unmastered, sym)
		}
	}
	if len(unmastered) > 0 {
		return unmastered[rand.Intn(len(unmastered))]
	}
	// all mastered
	syms := make([]string, 0, len(ELEMENTS))
	for sym := range ELEMENTS {
		syms = append(syms, sym)
	}
	return syms[rand.Intn(len(syms))]
}

func (ud *UserDataManager) GetProgress() (mastered, total int) {
	total = len(ELEMENTS)
	for sym := range ELEMENTS {
		if stats, ok := ud.data.Stats[sym]; ok && stats.Correct >= 3 {
			mastered++
		}
	}
	return
}

// ─── Quiz Engine ──────────────────────────────────────────────────────────

type QuizEngine struct {
	user *UserDataManager
	reader *bufio.Reader
}

func NewQuizEngine(user *UserDataManager) *QuizEngine {
	return &QuizEngine{user: user, reader: bufio.NewReader(os.Stdin)}
}

func (q *QuizEngine) ask(prompt string) string {
	fmt.Print(prompt)
	line, _ := q.reader.ReadString('\n')
	return strings.TrimSpace(line)
}

func (q *QuizEngine) getOptions(element Element, field string) []string {
	correct := ""
	if field == "name" {
		correct = element.Name
	} else {
		correct = element.Symbol
	}
	var pool []Element
	for _, e := range ELEMENTS_LIST {
		val := ""
		if field == "name" {
			val = e.Name
		} else {
			val = e.Symbol
		}
		if val != correct {
			pool = append(pool, e)
		}
	}
	others := []string{}
	for len(others) < 3 {
		r := pool[rand.Intn(len(pool))]
		val := ""
		if field == "name" {
			val = r.Name
		} else {
			val = r.Symbol
		}
		found := false
		for _, o := range others {
			if o == val {
				found = true
				break
			}
		}
		if !found && val != correct {
			others = append(others, val)
		}
	}
	options := append([]string{correct}, others...)
	rand.Shuffle(len(options), func(i, j int) { options[i], options[j] = options[j], options[i] })
	return options
}

func (q *QuizEngine) RunQuiz(numQuestions int) {
	correctCount := 0
	fmt.Println(c("\n🧠 Quiz Time! Answer questions about elements.", bright+cyan))
	for i := 0; i < numQuestions; i++ {
		qType := rand.Intn(2)
		element := ELEMENTS_LIST[rand.Intn(len(ELEMENTS_LIST))]
		var prompt, correct string
		var options []string
		if qType == 0 {
			correct = element.Name
			prompt = fmt.Sprintf("What is the name of element with symbol %s?", element.Symbol)
			options = q.getOptions(element, "name")
		} else {
			correct = element.Symbol
			prompt = fmt.Sprintf("What is the symbol of %s?", element.Name)
			options = q.getOptions(element, "symbol")
		}
		fmt.Printf("\n%s %s\n", c(fmt.Sprintf("Q%d.", i+1), yellow), prompt)
		for idx, opt := range options {
			fmt.Printf("  %d. %s\n", idx+1, opt)
		}
		choice := q.ask("Your choice (1-4): ")
		idx, _ := strconv.Atoi(choice)
		selected := options[idx-1]
		isCorrect := selected == correct
		q.user.RecordAnswer(element.Symbol, isCorrect)
		if isCorrect {
			correctCount++
			fmt.Printf("%s\n", c("✅ Correct! "+correct, green))
		} else {
			fmt.Printf("%s\n", c("❌ Wrong! The answer was "+correct, red))
		}
	}
	fmt.Printf("\n%s Correct: %s, Wrong: %s\n", c("Quiz finished!", bright), c(strconv.Itoa(correctCount), green), c(strconv.Itoa(numQuestions-correctCount), red))
}

// ─── Main App ─────────────────────────────────────────────────────────────

type ElementApp struct {
	user  *UserDataManager
	quiz  *QuizEngine
	reader *bufio.Reader
}

func NewElementApp() *ElementApp {
	rand.Seed(time.Now().UnixNano())
	user := NewUserDataManager()
	return &ElementApp{
		user:   user,
		quiz:   NewQuizEngine(user),
		reader: bufio.NewReader(os.Stdin),
	}
}

func (app *ElementApp) ask(prompt string) string {
	fmt.Print(prompt)
	line, _ := app.reader.ReadString('\n')
	return strings.TrimSpace(line)
}

func (app *ElementApp) askInt(prompt string) int {
	for {
		line := app.ask(prompt)
		if i, err := strconv.Atoi(line); err == nil {
			return i
		}
		fmt.Println(c("Please enter a number.", yellow))
	}
}

func (app *ElementApp) showMenu() {
	mastered, total := app.user.GetProgress()
	fmt.Println("\n" + c(strings.Repeat("═", 50), cyan))
	fmt.Println(c("⚛️ ELEMENT MASTER", bright+cyan))
	fmt.Println(c(strings.Repeat("═", 50), cyan))
	fmt.Printf("  Favorites: %d\n", len(app.user.data.Favorites))
	fmt.Printf("  Mastered: %d/%d\n", mastered, total)
	fmt.Printf("  Next repetition: %s\n", app.user.GetNextRep())
	fmt.Println(c(strings.Repeat("═", 50), cyan))
	fmt.Println("  1. 📋 List All Elements")
	fmt.Println("  2. 🔍 Search Element")
	fmt.Println("  3. ⭐ Favorites")
	fmt.Println("  4. 🧠 Start Quiz")
	fmt.Println("  5. 📊 Statistics")
	fmt.Println("  6. 🔁 Spaced Repetition")
	fmt.Println("  7. ➕ Toggle Favorite")
	fmt.Println("  0. 🚪 Exit")
	fmt.Println(c(strings.Repeat("═", 50), cyan))
}

func (app *ElementApp) listElements() {
	fmt.Println("\n📋 ALL ELEMENTS")
	fmt.Println(c(strings.Repeat("─", 60), dim))
	for _, e := range ELEMENTS_LIST {
		star := ""
		if app.user.IsFavorite(e.Symbol) {
			star = "⭐"
		}
		fmt.Printf("  %-3s %s %-12s #%-3d %-15s %.3f\n", e.Symbol, star, e.Name, e.Number, e.Category, e.Mass)
	}
}

func (app *ElementApp) searchElement() {
	query := app.ask("🔍 Enter symbol, name, or number: ")
	results := []Element{}
	for _, e := range ELEMENTS_LIST {
		if strings.Contains(strings.ToLower(e.Symbol), strings.ToLower(query)) ||
			strings.Contains(strings.ToLower(e.Name), strings.ToLower(query)) ||
			strconv.Itoa(e.Number) == query ||
			strings.Contains(strings.ToLower(e.Category), strings.ToLower(query)) {
			results = append(results, e)
		}
	}
	if len(results) == 0 {
		fmt.Println(c("No elements found.", yellow))
		return
	}
	fmt.Printf("\n🔍 Results (%d)\n", len(results))
	for _, e := range results {
		star := ""
		if app.user.IsFavorite(e.Symbol) {
			star = "⭐"
		}
		fmt.Printf("  %-3s %s %-12s #%-3d %-15s %.3f\n", e.Symbol, star, e.Name, e.Number, e.Category, e.Mass)
	}
}

func (app *ElementApp) showFavorites() {
	favs := []Element{}
	for _, sym := range app.user.data.Favorites {
		if e, ok := ELEMENTS[sym]; ok {
			favs = append(favs, e)
		}
	}
	if len(favs) == 0 {
		fmt.Println(c("No favorites yet.", yellow))
		return
	}
	fmt.Println("\n⭐ FAVORITES")
	for _, e := range favs {
		fmt.Printf("  %-3s %-12s #%-3d %s\n", e.Symbol, e.Name, e.Number, e.Category)
	}
}

func (app *ElementApp) startQuiz() {
	num := app.askInt("Number of questions (default 10): ")
	if num <= 0 {
		num = 10
	}
	app.quiz.RunQuiz(num)
}

func (app *ElementApp) showStats() {
	mastered, total := app.user.GetProgress()
	totalAnswers := 0
	correctAnswers := 0
	for _, s := range app.user.data.Stats {
		totalAnswers += s.Correct + s.Wrong
		correctAnswers += s.Correct
	}
	fmt.Println("\n📊 STATISTICS")
	fmt.Println(c(strings.Repeat("─", 30), dim))
	fmt.Printf("  Total Elements: %d\n", total)
	fmt.Printf("  Mastered: %d\n", mastered)
	fmt.Printf("  Favorites: %d\n", len(app.user.data.Favorites))
	fmt.Printf("  Total Answers: %d\n", totalAnswers)
	fmt.Printf("  Correct Answers: %d\n", correctAnswers)
	if totalAnswers > 0 {
		fmt.Printf("  Accuracy: %.1f%%\n", float64(correctAnswers)/float64(totalAnswers)*100)
	}
}

func (app *ElementApp) spacedRepetition() {
	symbol := app.user.GetNextRep()
	if symbol == "" {
		fmt.Println(c("No elements to repeat. Keep learning!", green))
		return
	}
	element := ELEMENTS[symbol]
	fmt.Printf("\n🔁 Repetition: %s (%s)\n", element.Name, element.Symbol)
	fmt.Printf("  Number: %d  Category: %s  Mass: %.3f\n", element.Number, element.Category, element.Mass)
	qType := rand.Intn(2)
	var ans, correct string
	if qType == 0 {
		ans = app.ask(fmt.Sprintf("What is the name of %s? ", element.Symbol))
		correct = element.Name
	} else {
		ans = app.ask(fmt.Sprintf("What is the symbol of %s? ", element.Name))
		correct = element.Symbol
	}
	isCorrect := strings.ToLower(strings.TrimSpace(ans)) == strings.ToLower(correct)
	app.user.RecordAnswer(symbol, isCorrect)
	if isCorrect {
		fmt.Println(c("✅ Correct!", green))
	} else {
		fmt.Printf("%s\n", c("❌ Wrong. The answer was "+correct, red))
	}
}

func (app *ElementApp) toggleFavorite() {
	sym := app.ask("Enter element symbol to toggle favorite: ")
	symbol := strings.ToUpper(strings.TrimSpace(sym))
	if _, ok := ELEMENTS[symbol]; !ok {
		fmt.Println(c("Element not found.", red))
		return
	}
	app.user.ToggleFavorite(symbol)
	state := "removed from"
	if app.user.IsFavorite(symbol) {
		state = "added to"
	}
	fmt.Printf("%s\n", c("✅ "+symbol+" "+state+" favorites.", green))
}

func (app *ElementApp) run() {
	fmt.Print("\033[H\033[2J")
	fmt.Println(c("\n⚛️ Element Master – Learn Chemistry Elements", bright+cyan))
	fmt.Println(c("Master the periodic table, one element at a time!", dim))

	for {
		app.showMenu()
		choice := app.ask("Your choice: ")
		switch choice {
		case "1":
			app.listElements()
		case "2":
			app.searchElement()
		case "3":
			app.showFavorites()
		case "4":
			app.startQuiz()
		case "5":
			app.showStats()
		case "6":
			app.spacedRepetition()
		case "7":
			app.toggleFavorite()
		case "0":
			fmt.Println(c("👋 Goodbye! Keep learning!", cyan))
			return
		default:
			fmt.Println(c("❌ Invalid choice.", red))
		}
		if choice != "0" {
			fmt.Print("\nPress Enter to continue...")
			app.reader.ReadString('\n')
		}
	}
}

func main() {
	app := NewElementApp()
	app.run()
}
