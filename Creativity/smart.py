"""
Smart Study Planner
====================
A console-based program that helps a student log, review and analyse
study sessions across different subjects over the course of a semester.

All session data is saved to a plain text file (study_log.txt) so that
the program keeps working correctly across multiple runs.
"""

import os

# The file used to persist session data between runs.
DATA_FILE = "study_log.txt"

# The character used to separate fields within a single saved record.
# A pipe is used instead of a comma because subject/topic text could
# legitimately contain commas.
FIELD_SEPARATOR = "|"


# ---------------------------------------------------------------------
# Part (c): classify_session
# ---------------------------------------------------------------------
def classify_session(duration):
    """
    Classify a study session based on its duration in minutes.

    Short  : under 30 minutes
    Medium : 30 to 90 minutes (inclusive)
    Long   : over 90 minutes
    """
    if duration < 30:
        return "Short"
    elif duration <= 90:
        return "Medium"
    else:
        return "Long"


# ---------------------------------------------------------------------
# Part (g): save_sessions / load_sessions
# ---------------------------------------------------------------------
def load_sessions():
    """
    Load previously saved sessions from DATA_FILE into a list of
    dictionaries. If the file does not exist yet (e.g. the very first
    run of the program), simply return an empty list instead of
    crashing.
    """
    sessions = []

    # Guard against the file not existing on the first ever run.
    if not os.path.exists(DATA_FILE):
        return sessions

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue  # skip blank lines

                parts = line.split(FIELD_SEPARATOR)
                # Skip any malformed lines rather than crashing the
                # whole program because of one bad record.
                if len(parts) != 4:
                    continue

                subject, topic, date, duration_str = parts
                try:
                    duration = float(duration_str)
                except ValueError:
                    continue  # skip lines with a corrupted duration

                sessions.append({
                    "subject": subject,
                    "topic": topic,
                    "date": date,
                    "duration": duration
                })
    except OSError as error:
        # Covers permission errors, locked files, etc. The program
        # should still start with an empty list rather than crash.
        print(f"Warning: could not read '{DATA_FILE}' ({error}). "
              f"Starting with no saved sessions.")

    return sessions


def save_sessions(sessions):
    """
    Save every logged session to DATA_FILE, one session per line,
    using FIELD_SEPARATOR to separate the fields.
    """
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            for session in sessions:
                line = FIELD_SEPARATOR.join([
                    session["subject"],
                    session["topic"],
                    session["date"],
                    str(session["duration"])
                ])
                f.write(line + "\n")
        print(f"Saved {len(sessions)} session(s) to '{DATA_FILE}'.")
    except OSError as error:
        print(f"Error: could not save sessions ({error}).")


# ---------------------------------------------------------------------
# Part (b): add_session
# ---------------------------------------------------------------------
def get_valid_duration():
    """
    Repeatedly prompt the user for a session duration (in minutes)
    until a valid positive number is entered.
    """
    while True:
        raw_value = input("Duration in minutes: ").strip()
        try:
            duration = float(raw_value)
        except ValueError:
            print("Please enter a valid number for the duration.")
            continue

        if duration <= 0:
            print("Duration must be a positive number. Please try again.")
            continue

        return duration


def add_session(sessions):
    """
    Prompt the user for the details of a study session (subject,
    topic, date/day label, duration) and append it to the sessions
    list as a dictionary.
    """
    print("\n--- Add a Study Session ---")
    subject = input("Subject: ").strip()
    topic = input("Topic covered: ").strip()
    date = input("Date / day (e.g. 2026-09-04 or 'Monday'): ").strip()
    duration = get_valid_duration()

    session = {
        "subject": subject,
        "topic": topic,
        "date": date,
        "duration": duration
    }
    sessions.append(session)
    print(f"Session added: {subject} ({classify_session(duration)}, "
          f"{duration:g} min).")


# ---------------------------------------------------------------------
# Part (d): view_sessions
# ---------------------------------------------------------------------
def print_session_table(sessions):
    """
    Print a list of session dictionaries as a neatly formatted table.
    Reused by view_sessions() and search_by_subject() so the table
    layout stays consistent throughout the program.
    """
    # Column widths chosen to comfortably fit typical entries.
    header = (f"{'Subject':<15}{'Topic':<20}{'Date':<15}"
              f"{'Duration (min)':<16}{'Classification':<14}")
    print(header)
    print("-" * len(header))

    for session in sessions:
        classification = classify_session(session["duration"])
        row = (f"{session['subject']:<15}{session['topic']:<20}"
               f"{session['date']:<15}{session['duration']:<16g}"
               f"{classification:<14}")
        print(row)


def view_sessions(sessions):
    """Display every logged session in a formatted table."""
    print("\n--- All Study Sessions ---")
    if not sessions:
        print("No sessions have been logged yet.")
        return

    print_session_table(sessions)


# ---------------------------------------------------------------------
# Part (e): search_by_subject
# ---------------------------------------------------------------------
def search_by_subject(sessions):
    """
    Ask the user for a subject name and display only the sessions
    recorded for that subject (case-insensitive match), along with
    the total time spent on it.
    """
    print("\n--- Search Sessions by Subject ---")
    query = input("Enter subject to search for: ").strip()

    # Case-insensitive comparison by lowering both sides.
    matches = [s for s in sessions if s["subject"].lower() == query.lower()]

    if not matches:
        print(f"No sessions found for subject '{query}'.")
        return

    print_session_table(matches)
    total_minutes = sum(s["duration"] for s in matches)
    print(f"\nTotal time spent on '{query}': {total_minutes:g} minutes "
          f"({total_minutes / 60:.2f} hours).")


# ---------------------------------------------------------------------
# Part (f): study_statistics
# ---------------------------------------------------------------------
def study_statistics(sessions):
    """
    Compute and display:
      - total hours studied overall
      - total hours studied per subject
      - the subject with the least total study time (weakest area)
      - the single longest session recorded
    """
    print("\n--- Study Statistics ---")
    if not sessions:
        print("No sessions have been logged yet, so no statistics are "
              "available.")
        return

    # Build a dictionary mapping subject -> total minutes for that subject.
    subject_totals = {}
    for session in sessions:
        subject = session["subject"]
        subject_totals[subject] = subject_totals.get(subject, 0) + session["duration"]

    total_minutes_overall = sum(subject_totals.values())
    print(f"Total time studied overall: {total_minutes_overall / 60:.2f} hours")

    print("\nTime studied per subject:")
    for subject, minutes in subject_totals.items():
        print(f"  {subject:<15}{minutes / 60:.2f} hours")

    # The weakest area is the subject with the smallest total time.
    weakest_subject = min(subject_totals, key=subject_totals.get)
    print(f"\nWeakest area (least total study time): {weakest_subject} "
          f"({subject_totals[weakest_subject] / 60:.2f} hours)")

    # The single longest session, found by comparing durations.
    longest_session = max(sessions, key=lambda s: s["duration"])
    print(f"\nLongest single session: {longest_session['subject']} - "
          f"{longest_session['topic']} on {longest_session['date']} "
          f"({longest_session['duration']:g} minutes, "
          f"{classify_session(longest_session['duration'])})")


# ---------------------------------------------------------------------
# Part (a): main menu
# ---------------------------------------------------------------------
def display_menu():
    """Print the main menu options."""
    print("\n===== Smart Study Planner =====")
    print("1. Add a study session")
    print("2. View all sessions")
    print("3. Search sessions by subject")
    print("4. View statistics")
    print("5. Save and exit")


def main():
    """
    Main program loop. Loads any existing sessions on start-up,
    repeatedly displays the menu and dispatches to the relevant
    function based on the user's choice, and rejects invalid choices
    without crashing.
    """
    sessions = load_sessions()
    if sessions:
        print(f"Loaded {len(sessions)} session(s) from '{DATA_FILE}'.")

    while True:
        display_menu()
        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            add_session(sessions)
        elif choice == "2":
            view_sessions(sessions)
        elif choice == "3":
            search_by_subject(sessions)
        elif choice == "4":
            study_statistics(sessions)
        elif choice == "5":
            save_sessions(sessions)
            print("Goodbye!")
            break
        else:
            # Invalid input is handled gracefully instead of crashing.
            print("Invalid choice. Please enter a number from 1 to 5.")


if __name__ == "__main__":
    main()
