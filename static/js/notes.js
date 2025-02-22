import { ThemeManager, applyOpacity } from './utils.js';

export class NotesThemeManager {
    static getNotesTheme() {
        return {
            backgroundColor: localStorage.getItem('backgroundColor') || '#f4f4f4',
            mainColor: localStorage.getItem('mainColor') || '#447de18f',
            subColor: localStorage.getItem('subColor') || '#ccc',
            opacity: localStorage.getItem('opacity') || '1'
        };
    }

    static applyTheme() {
        ThemeManager.applyTheme();

        const theme = this.getNotesTheme();

        console.log("loadNotes called");
        const notesList = document.getElementById("notes-list");
        const notes = JSON.parse(localStorage.getItem("notes")) || [];
        console.log("Notes data:", notes);

        notes.sort((a, b) => new Date(b.date) - new Date(a.date));


        notesList.innerHTML = "";

        if (notes.length === 0) {
            notesList.innerHTML = "<p>No notes found.</p>";
            return;
        }

        notes.forEach(note => {
            if (!note.title || !note.content || !note.date) {
                console.error("Invalid note format:", note);
                return;
            }

            const noteDiv = document.createElement("div");
            noteDiv.className = "note-container";

            noteDiv.style.backgroundColor = "#f9f9f9";

            noteDiv.style.borderColor = localStorage.getItem('subColor') || '#ccc';

            const title = document.createElement("div");
            title.className = "note-title";
            title.textContent = note.title;

            const content = document.createElement("div");
            content.className = "note-content";
            content.textContent = note.content;

            const date = document.createElement("div");
            date.className = "note-date";
            date.textContent = `Date: ${note.date}`;

            noteDiv.appendChild(title);
            noteDiv.appendChild(content);
            noteDiv.appendChild(date);

            notesList.appendChild(noteDiv);
        });

        applyOpacity(theme.opacity, ".note-container");

        localStorage.setItem("sortedNotes", JSON.stringify(notes));
    }
}