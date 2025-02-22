import { ThemeManager,applyOpacity } from './utils.js';

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

        console.log("loadNotes called"); // 调试信息
    const notesList = document.getElementById("notes-list");
    const notes = JSON.parse(localStorage.getItem("notes")) || [];
    console.log("Notes data:", notes); // 打印 notes 数据

    // 按时间倒序排列
    notes.sort((a, b) => new Date(b.date) - new Date(a.date));

    // 清空现有内容
    notesList.innerHTML = "";

    // 如果没有 notes 数据，显示提示信息
    if (notes.length === 0) {
        notesList.innerHTML = "<p>No notes found.</p>";
        return;
    }

    // 遍历 notes 数据并展示
    notes.forEach(note => {
        if (!note.title || !note.content || !note.date) {
            console.error("Invalid note format:", note); // 打印错误格式
            return;
        }

        const noteDiv = document.createElement("div");
        noteDiv.className = "note-container";

        // 设置初始背景色
        noteDiv.style.backgroundColor = "#f9f9f9"; // 默认背景色

        // 设置 borderColor
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

    // 应用透明度
    applyOpacity(theme.opacity, ".note-container");

    // 存储排序后的 notes（带序号）到 localStorage，供 `settings.html` 使用
    localStorage.setItem("sortedNotes", JSON.stringify(notes));
    }
}