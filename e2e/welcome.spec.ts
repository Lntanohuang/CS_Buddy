import { test, expect } from '@playwright/test'
import fixtures from './fixtures/test-data.json'

/**
 * Welcome e2e 契约。
 *
 * 设计原则：
 * - 绕过 mock 登录：直接注入 localStorage user，但在 spec 内覆盖 has_profile=false
 * - 选择器优先 data-testid，避免用 nth-child 或复杂 CSS chain 绑定 UI 结构
 * - 只验问答流完整可用：7 题全部回答后能完成画像并进入 /app/chat
 *
 * 修改前请阅读 CLAUDE.md：spec.ts 是契约，agent 不允许擅自修改既有契约文件。
 */

test.describe('welcome profile flow', () => {
  test.beforeEach(async ({ page }) => {
    const welcomeUser = { ...fixtures.auth.user, has_profile: false }

    await page.addInitScript((user) => {
      window.localStorage.setItem('user', JSON.stringify(user))
    }, welcomeUser)

    await page.route('**/api/v1/profile/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          user_id: welcomeUser.user_id,
          major: '计算机科学',
          current_level: 'INTERMEDIATE',
          learning_goal: 'EXAM_PREP',
          preferred_style: 'CODE_FIRST',
          cognitive_style: 'PRACTICAL',
          error_patterns: [],
          daily_time_minutes: 60,
          knowledge_mastery: {},
          weak_points: [],
          style_weights: {},
          subjects: ['DATA_STRUCTURE', 'ALGORITHM'],
          profile_complete: true,
          updated_at: new Date().toISOString(),
        }),
      })
    })
  })

  test('welcome 用户能完成全部 7 题并跳到 /app/chat', async ({ page }) => {
    await page.goto('/welcome')

    await expect(page.getByText('你目前学的是什么专业?')).toBeVisible()
    await page.getByTestId('welcome-input-major').fill('计算机科学')
    await page.getByTestId('welcome-next').click()

    await page.getByRole('button', { name: '备考(期末/秋招/考研)' }).click()
    await page.getByRole('button', { name: '进阶中' }).click()

    await page.getByRole('button', { name: '数据结构' }).click()
    await page.getByRole('button', { name: '算法' }).click()
    await page.getByTestId('welcome-next').click()

    await page.getByRole('button', { name: '看代码示例边学边练' }).click()
    await page.getByRole('button', { name: '偏实战应用' }).click()

    await page.getByTestId('welcome-input-daily_time_minutes').fill('60')
    await page.getByTestId('welcome-next').click()

    const startButton = page.getByTestId('welcome-start')
    await expect(startButton).toBeVisible()
    await startButton.click()

    await expect(page).toHaveURL(/\/app\/chat$/)
  })
})
