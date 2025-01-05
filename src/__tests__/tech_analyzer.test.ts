import { describe, expect, it, beforeEach, jest } from '@jest/globals';
import { TechStackAnalyzer } from '../tech_analyzer';

describe('TechStackAnalyzer', () => {
    let analyzer: TechStackAnalyzer;

    beforeEach(() => {
        analyzer = new TechStackAnalyzer();
    });

    describe('process_text', () => {
        it('should detect Python in text', async () => {
            const result = await analyzer.process_text('Using Python with Django');
            expect(result.success).toBe(true);
            if (result.success && result.data) {
                expect(result.data.identified_technologies).toEqual(
                    expect.arrayContaining([
                        expect.objectContaining({
                            name: 'python',
                            type: 'language'
                        })
                    ])
                );
            }
        });

        it('should handle empty text', async () => {
            const result = await analyzer.process_text('');
            expect(result.success).toBe(true);
            if (result.success && result.data) {
                expect(result.data.identified_technologies).toHaveLength(0);
            }
        });

        it('should respect tech type filters', async () => {
            const result = await analyzer.process_text(
                'Using Python and React',
                '',
                ['language']
            );
            expect(result.success).toBe(true);
            if (result.success && result.data) {
                const techs = result.data.identified_technologies;
                expect(techs.every(t => t.type === 'language')).toBe(true);
            }
        });

        it('should use cache when enabled', async () => {
            const text = 'Using Python and React';
            
            // First call
            const result1 = await analyzer.process_text(text);
            expect(result1.success).toBe(true);
            expect(result1.metadata?.cache_hit).toBe(false);
            
            // Second call should hit cache
            const result2 = await analyzer.process_text(text);
            expect(result2.success).toBe(true);
            expect(result2.metadata?.cache_hit).toBe(true);
        });

        it('should bypass cache when disabled', async () => {
            const text = 'Using Python and React';
            
            // First call
            const result1 = await analyzer.process_text(text);
            expect(result1.success).toBe(true);
            expect(result1.metadata?.cache_hit).toBe(false);
            
            // Second call with cache disabled
            const result2 = await analyzer.process_text(text, '', undefined, undefined, false);
            expect(result2.success).toBe(true);
            expect(result2.metadata?.cache_hit).toBe(false);
        });
    });

    describe('confidence scoring', () => {
        it('should assign higher confidence to exact matches', async () => {
            const result = await analyzer.process_text('Using python and python3');
            expect(result.success).toBe(true);
            if (result.success && result.data) {
                const techs = result.data.identified_technologies;
                const exactMatch = techs.find(t => t.name === 'python');
                expect(exactMatch?.confidence_score).toBeGreaterThan(0.8);
            }
        });

        it('should handle case-insensitive matches', async () => {
            const result = await analyzer.process_text('Using PYTHON and Python');
            expect(result.success).toBe(true);
            if (result.success && result.data) {
                const techs = result.data.identified_technologies;
                const match = techs.find(t => t.name === 'python');
                expect(match).toBeDefined();
                expect(match?.confidence_score).toBeGreaterThan(0.7);
            }
        });
    });

    describe('error handling', () => {
        it('should handle invalid input gracefully', async () => {
            const result = await analyzer.process_text(null as unknown as string);
            expect(result.success).toBe(false);
            expect(result.error).toBeDefined();
        });

        it('should handle invalid tech types filter', async () => {
            const result = await analyzer.process_text(
                'Using Python',
                '',
                ['invalid_type']
            );
            expect(result.success).toBe(true);
            if (result.success && result.data) {
                expect(result.data.identified_technologies).toHaveLength(0);
            }
        });
    });

    describe('metadata handling', () => {
        it('should include tech count in metadata', async () => {
            const result = await analyzer.process_text('Using Python, React, and MongoDB');
            expect(result.success).toBe(true);
            expect(result.metadata).toBeDefined();
            expect(result.metadata?.tech_count).toBeGreaterThan(0);
        });

        it('should track cache status in metadata', async () => {
            const text = 'Using Python and TypeScript';
            
            const result1 = await analyzer.process_text(text);
            expect(result1.metadata?.cache_hit).toBe(false);
            
            const result2 = await analyzer.process_text(text);
            expect(result2.metadata?.cache_hit).toBe(true);
        });
    });
});
