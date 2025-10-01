import asyncio
from playwright.async_api import async_playwright, expect

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # 1. Navigate to the local file
        await page.goto("file:///app/index.html")

        # 2. Verify AI features are removed
        await expect(page.locator("label[for='tvStb']")).to_be_hidden()
        await expect(page.get_by_text("9. 상담 내용으로 AI 설득 문자 생성")).to_be_hidden()

        # 3. Verify VAT Toggle and new UI elements
        vat_toggle_label = page.locator("label[for='vatToggle']")
        await expect(vat_toggle_label).to_be_visible()

        # Click the visible label to switch to VAT-exclusive pricing
        await vat_toggle_label.click()

        await expect(page.locator("#serviceSelectionTitle")).to_have_text("1. 서비스 선택 (3년 약정 기준, VAT 별도)")

        internet_plan_selector = page.locator("#internetPlan")
        await expect(internet_plan_selector.locator("option[value='internet_100m_standalone']")).to_have_text("100M 인터넷 (단독) (20,000원)")

        commission_tier_selector = page.locator("#commissionTier")
        await expect(commission_tier_selector).to_be_visible()
        await expect(page.locator("input[name='installationTime'][value='self_paid']")).to_be_visible()

        await expect(page.get_by_text("4. 카드 자동이체 청구할인 (선택)")).to_be_visible()

        # 4. Select options to test calculation logic
        await page.locator("input[name='internetType'][value='standalone']").check()
        await commission_tier_selector.select_option(value="60000")
        await page.locator("input[name='installationTime'][value='self_paid']").check()

        # 5. Click calculate and verify results
        await page.locator("#calculateButton").click()

        # 6. Assert the calculated values are correct
        await expect(page.locator("#summaryTotalGift")).to_have_text("163,000원")
        await expect(page.locator("#giftInstallationFeeSupport")).to_have_text("33,000")
        await expect(page.locator("#summaryMonthlyCost")).to_have_text("20,000원")

        # 7. Verify generated scripts
        await expect(page.locator("#memoScript")).to_contain_text("이름:")
        await expect(page.locator("#memoScript")).to_contain_text("핸드폰 번호:")
        await expect(page.locator("#infoScript")).to_contain_text("월 20,000원 (VAT별도)")
        await expect(page.locator("#infoScript")).to_contain_text("설치비 지원 33,000원")

        # 8. Take a final screenshot
        await page.screenshot(path="jules-scratch/verification/verification.png", full_page=True)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())