// Исправленный плагин - исключаем keyframes и анимации
export default function vueStyleIsolator(opts = {}) {
  const isolationSelector = opts.selector || '.vue-isolated-app';
  
  const processRule = (rule) => {
    // Пропускаем служебные селекторы и keyframes
    if (!rule.selector || 
        rule.selector.startsWith('@') || 
        rule.selector.includes('::') ||
        rule.selector.includes(isolationSelector) ||
        rule.selector.includes('html') ||
        rule.selector.includes('body') ||
        // ИСКЛЮЧАЕМ keyframes селекторы
        rule.selector.includes('%') ||
        rule.selector === 'from' ||
        rule.selector === 'to' ||
        /^\d+%$/.test(rule.selector.trim()) ||
        // Проверяем, находимся ли внутри keyframes
        rule.parent?.type === 'atrule' && rule.parent?.name === 'keyframes') {
      return;
    }
    
    // Обрабатываем :root переменные
    if (rule.selector.includes(':root')) {
      rule.selector = rule.selector.replace(':root', isolationSelector);
      return;
    }
    
    // Простое добавление префикса
    const selectors = rule.selector.split(',').map(sel => {
      const trimmed = sel.trim();
      
      if (trimmed.includes(isolationSelector)) {
        return trimmed;
      }
      
      // Добавляем двойную специфичность
      return `${isolationSelector}${isolationSelector} ${trimmed}`;
    });
    
    rule.selector = selectors.join(', ');
  };
  
  return {
    postcssPlugin: 'vue-style-isolator',
    Rule: processRule,
    AtRule: {
      // НЕ обрабатываем keyframes!
      keyframes(atRule) {
        // Пропускаем keyframes полностью
        return;
      },
      media(atRule) {
        atRule.walkRules(processRule);
      },
      supports(atRule) {
        atRule.walkRules(processRule);
      }
    }
  };
}

vueStyleIsolator.postcss = true;