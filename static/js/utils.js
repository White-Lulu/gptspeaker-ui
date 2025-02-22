// Service Worker
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('http://localhost:5000/static/js/service-worker.js', { scope: '/static/js/' })
        .then(registration => {
            console.log('Service Worker done:', registration);
        })
        .catch(error => {
            console.log('Failed to set Service Worker:', error);
        });
}

export class ThemeManager {
    static getDefaultTheme() {
        return {
            backgroundColor: localStorage.getItem('backgroundColor') || '#f4f4f4',
            mainColor: localStorage.getItem('mainColor') || '#447de18f',
            subColor: localStorage.getItem('subColor') || '#ccc',
            opacity: localStorage.getItem('opacity') || '1'
        };
    }

    static applyTheme() {
        const theme = this.getDefaultTheme();

        // Apply background color
        document.body.style.backgroundColor = theme.backgroundColor;
        document.querySelectorAll('.noactive-nav').forEach(a => {
            a.style.borderColor = theme.backgroundColor;
        });

        // Apply main color
        document.querySelector('.active-nav').style.borderColor = theme.mainColor;

        // Apply sub color
        document.querySelector('.navbar').style.borderBottomColor = theme.subColor;

        const navLink4 = document.querySelector('.nav-links4');
        if (navLink4) {
            navLink4.style.backgroundColor = theme.subColor;
            navLink4.style.borderColor = theme.subColor;
            navLink4.style.color = getContrastColor(theme.subColor);
        }

        return theme;
    }

    static convertToRGBA(color, opacity) {
        let r, g, b;

        if (color.startsWith("rgb")) {
            let rgbValues = color.match(/\d+/g);
            r = parseInt(rgbValues[0]);
            g = parseInt(rgbValues[1]);
            b = parseInt(rgbValues[2]);
        } else if (color.startsWith("#")) {
            let hex = color.replace("#", "");
            if (hex.length === 3) {
                hex = hex.split("").map(c => c + c).join("");
            }
            r = parseInt(hex.substring(0, 2), 16);
            g = parseInt(hex.substring(2, 4), 16);
            b = parseInt(hex.substring(4, 6), 16);
        } else {
            return `rgba(255, 255, 255, ${opacity})`;
        }

        return `rgba(${r}, ${g}, ${b}, ${opacity})`;
    }
}

export function getContrastColor(hexColor) {
    hexColor = hexColor.replace(/^#/, '');
    if (hexColor.length === 3) {
        hexColor = hexColor.split('').map(c => c + c).join('');
    }

    let r = parseInt(hexColor.substring(0, 2), 16) / 255;
    let g = parseInt(hexColor.substring(2, 4), 16) / 255;
    let b = parseInt(hexColor.substring(4, 6), 16) / 255;

    let luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b;
    return luminance > 0.5 ? '#000000' : '#ffffff';
}

export function applyOpacity(opacity, element) {
    document.querySelectorAll(element).forEach(el => {
        const bgColor = window.getComputedStyle(el).backgroundColor;
        el.style.backgroundColor = ThemeManager.convertToRGBA(bgColor, opacity);
    });
}