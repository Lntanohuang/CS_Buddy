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

const COPY_ICON_SVG =
  '<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
  '<rect x="5" y="5" width="9" height="9" rx="1.5"/>' +
  '<path d="M3 11V3.5C3 2.67157 3.67157 2 4.5 2H11"/>' +
  '</svg>'

const CHECK_ICON_SVG =
  '<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
  '<path d="M3 8.5L6.5 12L13 4.5"/>' +
  '</svg>'

function wrapCodeBlock(innerHighlightedHtml: string, lang: string): string {
  const safeLang = escapeHtml((lang || 'text').toLowerCase())
  return (
    '<div class="code-block">' +
    '<div class="code-block-header">' +
    `<span class="code-block-lang">${safeLang}</span>` +
    '<button class="code-block-copy" type="button" aria-label="复制代码" title="复制">' +
    `<span class="code-block-copy-icon code-block-copy-icon--copy">${COPY_ICON_SVG}</span>` +
    `<span class="code-block-copy-icon code-block-copy-icon--check">${CHECK_ICON_SVG}</span>` +
    '</button>' +
    '</div>' +
    `<pre class="hljs"><code>${innerHighlightedHtml}</code></pre>` +
    '</div>'
  )
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
            return wrapCodeBlock(hljs.highlight(str, { language: lang }).value, lang)
          } catch {
            // fall through
          }
        }
        return wrapCodeBlock(escapeHtml(str), lang)
      },
    })
  } catch {
    return null
  }
})()

export function useMarkdown() {
  function render(source: string): string {
    const raw = md ? md.render(source) : wrapCodeBlock(escapeHtml(source), 'text')
    return sanitize(raw)
  }

  return { render }
}
