import { test, expect } from '@playwright/test'
import fixtures from './fixtures/test-data.json'

/**
 * Chat smoke e2e。
 *
 * 设计原则：
 * - 绕过 mock 登录：直接注入 localStorage user (has_profile=true)
 * - 选择器优先 placeholder + class fallback —— UI 改了 placeholder 这个测试要更新
 * - 只验"管道通"：一次 chat 能流出可见文本，不验答案质量（那是 eval 层的事）
 *
 * 修改前请阅读 CLAUDE.md：spec.ts 是契约，agent 不允许擅自修改。
 */

test.describe('chat smoke', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript((user) => {
      window.localStorage.setItem('user', JSON.stringify(user))
    }, fixtures.auth.user)
  })

  test('用户能发一条消息并看到流式回复', async ({ page }) => {
    await page.goto('/app/chat')

    // 1. 输入框可见
    const input = page.locator(`textarea[placeholder="${fixtures.chat.expectations.input_placeholder}"]`)
    await expect(input).toBeVisible({ timeout: 10_000 })

    // 2. 发送 prompt
    const startMs = Date.now()
    await input.fill(fixtures.chat.prompt)
    await page.locator('.chat-input-send').click()

    // 3. 等流式内容出现（first chunk）
    const messageList = page.locator('.chat-message-list')
    await expect(messageList).toContainText(fixtures.chat.prompt, { timeout: 5_000 })

    // 等到 user 消息之外有任何 assistant 文本（>= min_visible_chars）
    const messages = page.locator('.chat-message-list .message-bubble, .chat-message-list__inner > *')
    await expect(async () => {
      const total = await messageList.innerText()
      // 减去用户消息本身的字数
      const remainder = total.replace(fixtures.chat.prompt, '').trim()
      expect(remainder.length).toBeGreaterThanOrEqual(fixtures.chat.expectations.min_visible_chars)
    }).toPass({ timeout: fixtures.chat.expectations.first_chunk_ms_max })

    const firstChunkMs = Date.now() - startMs
    console.log(`[smoke] first visible reply chunk in ${firstChunkMs}ms`)

    // 4. 输入框被清空（发送后的 UX 契约）
    await expect(input).toHaveValue('', { timeout: 3_000 })
  })
})
