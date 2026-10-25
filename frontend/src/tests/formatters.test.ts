import { describe, it, expect } from 'vitest';
import { formatRupee, formatDate, getCategoryColor } from '../utils/formatters';

describe('Formatters Utilities', () => {
  it('formats Indian Rupee currency correctly', () => {
    const formatted = formatRupee(100000, false);
    // Should contain ₹ and 1,00,000
    expect(formatted).toContain('₹');
    expect(formatted.replace(/\s/g, '')).toContain('1,00,000');
  });

  it('formats zero and handles edge cases safely', () => {
    expect(formatRupee(0)).toContain('₹');
    expect(formatRupee(NaN as any)).toBe('₹0');
  });

  it('formats dates in readable Indian style', () => {
    const d = formatDate('2026-10-14');
    expect(d).toContain('Oct');
    expect(d).toContain('2026');
  });

  it('returns valid category colors', () => {
    expect(getCategoryColor('Food and groceries')).toBe('#f97316');
    expect(getCategoryColor('Transportation')).toBe('#3b82f6');
    expect(getCategoryColor('Unknown Category')).toBe('#6366f1');
  });
});
