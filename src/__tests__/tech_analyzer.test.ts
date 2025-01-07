import { describe, expect, it, beforeEach } from '@jest/globals';
import { TechStackAnalyzer, Technology } from '../tech_analyzer';

describe('TechStackAnalyzer', () => {
    let analyzer: TechStackAnalyzer;

    beforeEach(() => {
        analyzer = new TechStackAnalyzer();
    });

    describe('process_text', () => {
        it('should handle empty input', async () => {
            const result = await analyzer.process_text('');
            expect(result.success).toBe(false);
            expect(result.error?.error_type).toBe('ValidationError');
        });

        it('should handle invalid input', async () => {
            const result = await analyzer.process_text(null as unknown as string);
            expect(result.success).toBe(false);
            expect(result.error?.error_type).toBe('ValidationError');
        });

        it('should process valid text', async () => {
            const result = await analyzer.process_text('python javascript typescript');
            expect(result.success).toBe(true);
            expect(result.data?.identified_technologies.length).toBeGreaterThan(0);
        });

        it('should respect tech_types filter', async () => {
            const result = await analyzer.process_text(
                'python javascript typescript react angular',
                '',
                ['language']
            );
            expect(result.success).toBe(true);
            if (result.success) {
                const techs = result.data.identified_technologies;
                expect(techs.length).toBeGreaterThan(0);
                expect(techs.every((t: Technology) => t.type === 'language')).toBe(true);
            }
        });

        it('should respect categories filter', async () => {
            const result = await analyzer.process_text(
                'react angular vue python django',
                '',
                undefined,
                ['frontend']
            );
            expect(result.success).toBe(true);
            if (result.success) {
                const techs = result.data.identified_technologies;
                expect(techs.length).toBeGreaterThan(0);
                expect(techs.every((t: Technology) => t.category === 'frontend')).toBe(true);
            }
        });

        it('should handle caching', async () => {
            const text = 'python javascript';
            const result1 = await analyzer.process_text(text);
            const result2 = await analyzer.process_text(text);

            expect(result1.success && result2.success).toBe(true);
            if (result1.success && result2.success) {
                expect(result2.metadata?.cache_hit).toBe(true);
                expect(result1.data).toEqual(result2.data);
            }
        });

        it('should calculate confidence scores', async () => {
            const result = await analyzer.process_text('python python python');
            expect(result.success).toBe(true);
            if (result.success) {
                const techs = result.data.identified_technologies;
                const exactMatch = techs.find((t: Technology) => t.name === 'python');
                expect(exactMatch).toBeDefined();
                expect(exactMatch?.confidence_score).toBeGreaterThan(0.7);
            }
        });

        it('should handle case insensitivity', async () => {
            const result = await analyzer.process_text('PYTHON Python python');
            expect(result.success).toBe(true);
            if (result.success) {
                const techs = result.data.identified_technologies;
                const match = techs.find((t: Technology) => t.name === 'python');
                expect(match).toBeDefined();
                expect(match?.confidence_score).toBeGreaterThan(0.7);
            }
        });
    });

    describe('stack analysis', () => {
        it('should check stack completeness', async () => {
            const result = await analyzer.process_text('react node.js mongodb');
            expect(result.success).toBe(true);
            if (result.success) {
                const completeness = result.data.stack_analysis.completeness;
                expect(completeness.frontend).toBe(true);
                expect(completeness.backend).toBe(true);
                expect(completeness.database).toBe(true);
            }
        });

        it('should generate suggestions', async () => {
            const result = await analyzer.process_text('react node.js mongodb');
            expect(result.success).toBe(true);
            if (result.success) {
                const suggestions = result.data.stack_analysis.suggestions;
                expect(Array.isArray(suggestions)).toBe(true);
                expect(suggestions.length).toBeGreaterThan(0);
            }
        });
    });
});
