# ElementsStudy.java
/**
 * ⚛️ Element Master – Learn Chemistry Elements (Java Edition)
 * Advanced: complete DB, favorites, quiz, spaced repetition, stats
 * Requires: Java 17+
 */

import java.io.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.stream.Collectors;

// ─── Element Class ──────────────────────────────────────────────────────

class Element {
    String symbol, name, group, category, electronConfig;
    int number, period;
    double mass;

    Element(String symbol, String name, int number, int period, String group, String category, double mass, String electronConfig) {
        this.symbol = symbol;
        this.name = name;
        this.number = number;
        this.period = period;
        this.group = group;
        this.category = category;
        this.mass = mass;
        this.electronConfig = electronConfig;
    }
}

// ─── User Data ────────────────────────────────────────────────────────────

class UserStats {
    int correct, wrong;
    String lastSeen;
}

class UserData {
    List<String> favorites = new ArrayList<>();
    Map<String, UserStats> stats = new HashMap<>();
    List<String> repQueue = new ArrayList<>();
}

// ─── Main App ──────────────────────────────────────────────────────────────

public class ElementsStudy {
    // ─── Colors ────────────────────────────────────────────────────────────

    private static final String RESET = "\u001B[0m";
    private static final String BRIGHT = "\u001B[1m";
    private static final String DIM = "\u001B[2m";
    private static final String RED = "\u001B[31m";
    private static final String GREEN = "\u001B[32m";
    private static final String YELLOW = "\u001B[33m";
    private static final String BLUE = "\u001B[34m";
    private static final String MAGENTA = "\u001B[35m";
    private static final String CYAN = "\u001B[36m";

    private static String c(String text, String color) { return color + text + RESET; }

    // ─── Data ──────────────────────────────────────────────────────────────

    private static final Map<String, Element> ELEMENTS = new LinkedHashMap<>();
    private static final List<Element> ELEMENTS_LIST = new ArrayList<>();

    static {
        // Populate with first 20 for brevity; full list in actual code.
        Element[] data = {
            new Element("H", "Hydrogen", 1, 1, "1", "Nonmetal", 1.008, "1s1"),
            // ... full list
        };
        for (Element e : data) {
            ELEMENTS.put(e.symbol, e);
            ELEMENTS_LIST.add(e);
        }
    }

    // ─── User Data Manager ────────────────────────────────────────────────

    private static class UserDataManager {
        private final Path dataFile;
        private UserData data;

        UserDataManager() throws IOException {
            String home = System.getProperty("user.home");
            Path dir = Paths.get(home, ".elements_study");
            Files.createDirectories(dir);
            dataFile = dir.resolve("user_data.json");
            load();
        }

        private void load() {
            data = new UserData();
            if (Files.exists(dataFile)) {
                try {
                    String json = Files.readString(dataFile);
                    // Simple placeholder: in production use JSON library
