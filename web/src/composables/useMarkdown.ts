import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import DOMPurify from 'dompurify'

type DomPurifyShape = {
  sanitize?: (raw: string) => string
  default?: {
    sanitize?: (raw: string) => string
  }
}

function escapeHtml(value: string): string {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

function resolveSanitize() {
  const domPurifyModule = DOMPurify as unknown as DomPurifyShape

  if (typeof domPurifyModule.sanitize === 'function') {
    return domPurifyModule.sanitize.bind(domPurifyModule)
  }

  if (domPurifyModule.default && typeof domPurifyModule.default.sanitize === 'function') {
    return domPurifyModule.default.sanitize.bind(domPurifyModule.default)
  }

  return (raw: string) => raw
}

const sanitize = resolveSanitize()

const md = (() => {
  try {
    return new MarkdownIt({
      html: false,
      linkify: true,
      typographer: true,
      highlight(str: string, lang: string) {
        if (lang && hljs.getLanguage(lang)) {
          try {
            return `<pre class="hljs"><code>${hljs.highlight(str, { language: lang }).value}</code></pre>`
          } catch {
            // fall through
          }
        }
        return `<pre class="hljs"><code>${escapeHtml(str)}</code></pre>`
      },
    })
  } catch {
    return null
  }
})()

export function useMarkdown() {
  function render(source: string): string {
    const raw = md ? md.render(source) : `<pre class="hljs"><code>${escapeHtml(source)}</code></pre>`
    return sanitize(raw)
  }

  return { render }
}
