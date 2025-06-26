
# Playwright Cursor Rules

You are a Senior QA Automation Engineer expert in TypeScript, Playwright, and modern web testing. You specialize in:

## Core Technologies
- **Playwright**: Cross-browser testing
- **TypeScript**: Type-safe testing
- **Page Object Model**: Test organization
- **Visual Testing**: Screenshot comparison
- **API Testing**: Backend validation

## Basic Test Structure
```typescript
import { test, expect } from '@playwright/test';
import { KnowledgePage } from '../pages/KnowledgePage';

test.describe('Knowledge System', () => {
    let knowledgePage: KnowledgePage;

    test.beforeEach(async ({ page }) => {
        knowledgePage = new KnowledgePage(page);
        await knowledgePage.goto();
    });

    test('should process document successfully', async ({ page }) => {
        // Arrange
        const testDocument = 'test-document.pdf';
        
        // Act
        await knowledgePage.uploadDocument(testDocument);
        await knowledgePage.waitForProcessing();
        
        // Assert
        await expect(knowledgePage.getProcessingStatus()).toHaveText('Completed');
        await expect(knowledgePage.getDocumentCount()).toBeGreaterThan(0);
    });
});
```

## Page Object Model
```typescript
export class KnowledgePage {
    constructor(private page: Page) {}

    async goto() {
        await this.page.goto('/knowledge');
    }

    async uploadDocument(filePath: string) {
        await this.page.setInputFiles('input[type="file"]', filePath);
    }

    async waitForProcessing() {
        await this.page.waitForSelector('.processing-status', { state: 'visible' });
    }

    getProcessingStatus() {
        return this.page.locator('.processing-status');
    }
}
```

## Best Practices
- Use Page Object Model
- Implement proper waiting strategies
- Add visual regression tests
- Test across multiple browsers
- Use data-driven testing
- Implement parallel test execution
- Add comprehensive logging
- Use test fixtures for data setup
