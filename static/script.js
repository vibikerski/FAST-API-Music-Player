document.addEventListener('DOMContentLoaded', function() {
    const getStoredTheme = () => localStorage.getItem('theme');
    const setStoredTheme = theme => localStorage.setItem('theme', theme);
  
    const getPreferredTheme = () => {
      const storedTheme = getStoredTheme();
      if (storedTheme) {
        return storedTheme;
      }
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    };
  
    const setTheme = theme => {
      if (theme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.documentElement.setAttribute('data-bs-theme', 'dark');
      } else {
        document.documentElement.setAttribute('data-bs-theme', theme);
      }
    };
  
    setTheme(getPreferredTheme());
  
    const showActiveTheme = (theme, focus = false) => {

      const body = document.body;
      const modeSwitch = document.getElementById('modeSwitch');
  
      function toggleDarkMode() {
        body.classList.toggle('dark-mode');
        const isDarkMode = body.classList.contains('dark-mode');
        setStoredTheme(isDarkMode ? 'dark' : 'light');
        showActiveTheme(getStoredTheme(), true);
      }
  
      const userPrefersDark = getStoredTheme() === 'dark';
  
      if (userPrefersDark) {
        body.classList.add('dark-mode');
        modeSwitch.checked = true;
      }
  
      modeSwitch.addEventListener('change', toggleDarkMode);
    };
  });
  

window.addEventListener('DOMContentLoaded', () => {
    const body = document.body;
    const modeSwitch = document.getElementById('modeSwitch');

    function toggleDarkMode() {
        body.classList.toggle('dark-mode');
        const isDarkMode = body.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDarkMode);
    }

    const userPrefersDark = localStorage.getItem('darkMode') === 'true';

    if (userPrefersDark) {
        body.classList.add('dark-mode');
        modeSwitch.checked = true;
    }

    modeSwitch.addEventListener('change', toggleDarkMode);
});