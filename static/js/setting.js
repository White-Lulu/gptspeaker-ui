import { ThemeManager, applyOpacity } from './utils.js';

export class SettingThemeManager {
    static getSettingTheme() {
        return {
            backgroundColor: localStorage.getItem('backgroundColor') || '#f4f4f4',
            mainColor: localStorage.getItem('mainColor') || '#447de18f',
            subColor: localStorage.getItem('subColor') || '#ccc',
            opacity: localStorage.getItem('opacity') || '1',
            voice: localStorage.getItem('voice') || 'zh-CN-XiaochenNeural',
            chatname: localStorage.getItem('chatname') || '😊',
            username: localStorage.getItem('username') || '😎',
            deepseekmodel: localStorage.getItem('deepseekmodel') || 'v3',
            openaimodel: localStorage.getItem('openaimodel') || 'gpt-4o',
        };
    }

    static applyTheme() {
        ThemeManager.applyTheme();

        const theme = this.getSettingTheme();

        document.getElementById('voice').value = theme.voice;
        document.getElementById('chatname').value = theme.chatname;
        document.getElementById('username').value = theme.username;
        document.getElementById('deepseekmodel').value = theme.deepseekmodel;
        document.getElementById('openaimodel').value = theme.openaimodel;

        document.querySelectorAll('button').forEach(button => {
            button.style.backgroundColor = theme.mainColor;
        });

        const subColorElements = [
            'input[type="text"]',
            'select',
            '.left-column1',
            '.right-column1'
        ];
        subColorElements.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                elements.forEach(element => {
                    element.style.borderColor = theme.subColor;
                });
            }
        });
        document.querySelectorAll('input[type="text"]',
            'select',
            '.left-column1',
            '.right-column1').forEach(a => {
            a.style.borderColor = theme.subColor;
        });

        document.getElementById('background-color').value = theme.backgroundColor;
        document.getElementById('main-color').value = theme.mainColor;
        document.getElementById('sub-color').value = theme.subColor;

        document.documentElement.style.setProperty('--main-color', theme.mainColor);

        document.getElementById('opacity').addEventListener('input', function () {
            applyOpacity(this.value);
        });

        document.getElementById('opacity').value = theme.opacity;
        applyOpacity(theme.opacity,'input,select');
        const notes = JSON.parse(localStorage.getItem("sortedNotes")) || [];
        const select = document.getElementById("note");

        select.innerHTML = '<option value="">O.o</option>';

        notes.forEach((note, index) => {
            const option = document.createElement("option");
            option.value = `${note.title}`;
            option.textContent = `${note.title}`;
            select.appendChild(option);
        });
    }
}

