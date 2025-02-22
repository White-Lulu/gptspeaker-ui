import { getContrastColor, applyOpacity } from './utils.js';

export class SpeakerThemeManager {
    static getSpeakerTheme() {
        return {
            backgroundColor: localStorage.getItem('backgroundColor') || '#f4f4f4',
            mainColor: localStorage.getItem('mainColor') || '#447de18f',
            subColor: localStorage.getItem('subColor') || '#ccc',
            opacity: localStorage.getItem('opacity') || '1'
        };
    }

    static applyTheme() {
        const theme = this.getSpeakerTheme();

        document.querySelectorAll(".deepseek-btn, .openai-btn").forEach(btn => {
            btn.innerText = btn.innerText.replace(" √", "");
        });

        // Apply MainColor
        const mainColorElements = ['.confirm-btn', '.action-btn2'];
        mainColorElements.forEach(selector => {
            const element = document.querySelector(selector);
            if (element) {
                element.style.backgroundColor = theme.mainColor;
            }
        });

        // Apply SubColor
        const subColorElements = [
            '.left-column',
            '.multi-line-input', '.single-line-input',
            '.prompt-input', '.action-btn1'
        ];
        subColorElements.forEach(selector => {
            const element = document.querySelector(selector);
            if (element) {
                element.style.borderColor = theme.subColor;
            }
        });

        document.querySelector('.action-btn1').style.backgroundColor = theme.subColor;
        document.querySelector('.action-btn1').style.color = getContrastColor(theme.subColor);
        applyOpacity(theme.opacity, '.left-column, .prompt-input, .multi-line-input,.single-line-input');

    }
}